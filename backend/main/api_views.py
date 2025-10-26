import os

from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from django.db.models import Exists, OuterRef
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from rest_framework.parsers import MultiPartParser

from .serializer import *
from .models import *
from .utils import *


SERIALIZER_MAP = {
    'publication': (Publication, PublicationReadSerializer),
    'presentation': (Presentation, PresentationReadSerializer),
}

def get_serializer_by_type(post_type):
    return SERIALIZER_MAP.get(post_type)[1]

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        user_roles = UserRole.objects.filter(user=user).select_related('role')
        roles_list = [user_role.role.name for user_role in user_roles]
        
        user_info_data = UserInfoSerializer(user).data

        return Response({
            'token': str(refresh.access_token),
            'user_info': user_info_data,
            'roles': roles_list
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# get_user_info
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    try:
        user = request.user

        user_roles = UserRole.objects.filter(user=user).select_related('role')
        roles_list = [user_role.role.name for user_role in user_roles]
        
        user_info_data = UserInfoSerializer(user).data

        response_data = {
            'user_info': user_info_data,
            'roles': roles_list
        }
        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': 'Ошибка при получении информации о пользователе',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# GET /api/get_post_information/{id}/
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_post_information(request, id):
    try:
        user = request.user
        post_id = int(id)

        post = get_object_or_404(
            Post.objects.select_related('publication', 'presentation')
            .prefetch_related('publication__external_authors'),
            id=post_id
        )

        if not is_user_has_access_to_post(user, post):
            return Response({
                'error': 'Доступ запрещен. У вас нет прав для просмотра этого поста.'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = PostWithDetailsSerializer({
            'post': post,
            'details': get_post_details(post)
        })

        return Response(serializer.data, status=status.HTTP_200_OK)

    except ValueError:
        return Response({
            'error': 'Некорректный ID поста'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Ошибка при получении информации о посте',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# POST /api/create_post/
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def create_post(request):
    try:
        data = request.data.copy()

        internal_authors_from_request = request.data.getlist('internal_authors_list')
        if internal_authors_from_request:
            processed_authors = []
            for author_id in internal_authors_from_request:
                if author_id and str(author_id).strip():
                    try:
                        processed_authors.append(int(author_id))
                    except (ValueError, TypeError):
                        continue
            data['internal_authors_list'] = processed_authors
        else:
            data['internal_authors_list'] = []

        external_authors_from_request = request.data.getlist('external_authors_list')
        if external_authors_from_request:
            processed_external = []
            for author_name in external_authors_from_request:
                if author_name and str(author_name).strip():
                    processed_external.append(str(author_name).strip())
            data['external_authors_list'] = processed_external
        else:
            data['external_authors_list'] = []

        if 'type' not in data:
            return Response({
                'error': 'Отсутствуют обязательные поля: post и post.type'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        post_type = data.get('type')

        if post_type not in ['publication', 'presentation']:
            return Response({
                'error': f'Неподдерживаемый тип поста: {post_type}. Допустимые типы: publication, presentation'
            }, status=status.HTTP_400_BAD_REQUEST)

        validation_errors = validate_post_data(post_type, data)
        if validation_errors:
            return Response({
                'error': 'Ошибки валидации',
                'details': validation_errors
            }, status=status.HTTP_400_BAD_REQUEST)

        post_data = {
            'type': post_type,
            'comment': data.get('comment', '')
        }
        
        details_data = {}
        exclude_fields = ['type', 'comment']
        for key, value in data.items():
            if key not in exclude_fields:
                details_data[key] = value

        if request.FILES:
            for file_key, file_obj in request.FILES.items():
                details_data[file_key] = file_obj

        serializer_data = {
            'post': post_data,
            'details': details_data
        }


        print("Serializer data:", serializer_data)

        serializer = PostWithDetailsCreateSerializer(
            data=serializer_data,
            context={'request': request}
        )

        if serializer.is_valid():
            post = serializer.save()

            return Response({
                'id': post.id,
                'message': f'{post_type.capitalize()} успешно создан',
                'type': post_type
            }, status=status.HTTP_201_CREATED)
        else:
            print("Serializer errors:", serializer.errors)
            return Response({
                'error': 'Ошибки валидации данных',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'error': 'Ошибка при создании поста',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#PUT /api/update_post/{id}
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def update_post(request, id):
    try:
        user = request.user
        post_id = int(id)

        post = get_object_or_404(
            Post.objects.select_related('publication', 'presentation')
            .prefetch_related('publication__external_authors'),
            id=post_id
        )

        if not post.authors.filter(user=user).exists() and not is_admin_user(user):
            return Response({
                'error': 'Доступ запрещен. Вы не имеете достаточно прав для изменения этого поста.'
            }, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()

        internal_authors_from_request = request.data.getlist('internal_authors_list')
        if internal_authors_from_request:
            processed_authors = []
            for author_id in internal_authors_from_request:
                if author_id and str(author_id).strip():
                    try:
                        processed_authors.append(int(author_id))
                    except (ValueError, TypeError):
                        continue
            
            data['internal_authors_list'] = processed_authors
        else:
            data['internal_authors_list'] = []

        external_authors_from_request = request.data.getlist('external_authors_list')
        if external_authors_from_request:
            processed_external = []
            for author_name in external_authors_from_request:
                if author_name and str(author_name).strip():
                    processed_external.append(str(author_name).strip())
            data['external_authors_list'] = processed_external
        else:
            data['external_authors_list'] = []

        post_data = {
            'type': data.get('type'),
            'comment': data.get('comment', '')
        }

        if not post_data.get('type'):
            return Response({
                'error': 'Отсутствует обязательный раздел "post"'
            }, status=status.HTTP_400_BAD_REQUEST)

        post_serializer = PostCreateSerializer(post, data=post_data, partial=False)
        if not post_serializer.is_valid():
            return Response({
                'error': 'Ошибки валидации данных поста',
                'details': post_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        post_serializer.save()

        details_data = {}
        for key, value in data.items():
            if key not in ['type', 'comment']:
                details_data[key] = value

        if request.FILES:
            for file_key, file_obj in request.FILES.items():
                details_data[file_key] = file_obj

        update_errors = update_post_details(post, details_data)

        internal_authors = details_data.get('internal_authors_list', [])
        
        current_authors = set(post.authors.values_list('user_id', flat=True))
        
        authors_to_add = set(internal_authors) - current_authors
        
        authors_to_remove = current_authors - set(internal_authors) - {user.id}
        
        PostAuthor.objects.filter(post=post, user_id__in=authors_to_remove).delete()
        
        for user_id in authors_to_add:
            try:
                user_obj = User.objects.get(id=user_id)
                PostAuthor.objects.create(post=post, user=user_obj)
            except User.DoesNotExist:
                continue
        
        if not post.authors.filter(user=user).exists():
            PostAuthor.objects.create(post=post, user=user)

        if update_errors:
            return Response({
                'error': 'Ошибки при обновлении деталей поста',
                'details': update_errors
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'id': post.id,
            'message': 'Пост успешно обновлен',
            'type': post.type
        }, status=status.HTTP_200_OK)

    except ValueError:
        return Response({
            'error': 'Некорректный ID поста'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Ошибка при обновлении поста',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#DELETE /api/delete_post/{id}
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post(request, id):
    try:
        user = request.user
        post_id = int(id)

        post = get_object_or_404(Post, id=post_id)

        if not post.authors.filter(user=user).exists() and not is_admin_user(user):
            return Response({
                'error': 'Доступ запрещен. Вы не являетесь автором этого поста.'
            }, status=status.HTTP_403_FORBIDDEN)

        post_type = post.type
        post_id = post.id

        post.delete()

        return Response({
            'message': f'Пост {post_id} типа "{post_type}" успешно удален'
        }, status=status.HTTP_200_OK)

    except ValueError:
        return Response({
            'error': 'Некорректный ID поста'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Ошибка при удалении поста',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_user(request):
    try:
        current_user = request.user

        if not is_admin_user(current_user):
            return Response({
                'error': 'Доступ запрещен. Требуются права администратора.'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = UserCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'error': 'Ошибки валидации данных',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        roles_to_assign = request.data.get('roles', [])
        can_assign, error_message = can_user_assign_roles(current_user, roles_to_assign)

        if not can_assign:
            return Response({
                'error': error_message
            }, status=status.HTTP_403_FORBIDDEN)

        user = serializer.save()

        return Response({
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'error': 'Ошибка при создании пользователя',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# PUT /api/update_user/{id}
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request, id):
    try:
        current_user = request.user
        target_user_id = int(id)
        target_user = get_object_or_404(User, id=target_user_id)

        if not have_enough_rights(current_user, target_user):
            return Response({
                'error': 'Доступ запрещен. Недостаточно прав для обновления профиля.'
            }, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        serializer = UserUpdateSerializer(
            target_user,
            data=data,
            partial=True
        )
        if serializer.is_valid():
            updated_user = serializer.save()

            return Response({
                'message': 'Данные пользователя успешно обновлены',
                'user': UserSerializer(updated_user).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Ошибки валидации данных',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except ValueError:
        return Response({
            'error': 'Некорректный ID пользователя'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Ошибка при обновлении пользователя',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#DELETE /api/delete_user/{id}
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, id):
    try:
        current_user = request.user
        target_user_id = int(id)

        if current_user.id == target_user_id:
            return Response({
                'error': 'Нельзя удалить собственный аккаунт'
            }, status=status.HTTP_400_BAD_REQUEST)

        target_user = get_object_or_404(User, id=target_user_id)

        can_delete, error_message = can_user_delete_user(current_user, target_user)
        if not can_delete:
            return Response({
                'error': error_message
            }, status=status.HTTP_403_FORBIDDEN)

        user_info = {
            'id': target_user.id,
            'username': target_user.username,
            'email': target_user.email,
            'full_name': target_user.get_full_name(),
            'group': target_user.group
        }

        target_user.delete()

        return Response({
            'message': 'Пользователь успешно удален',
            'deleted_user': user_info
        }, status=status.HTTP_200_OK)

    except ValueError:
        return Response({
            'error': 'Некорректный ID пользователя'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Ошибка при удалении пользователя',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# GET /api/get_all_users/
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_users(request):
    try:
        current_user = request.user

        user_roles = UserRole.objects.filter(user=current_user).select_related('role')
        role_names = [user_role.role.name for user_role in user_roles]

        visible_roles = ['SPbUUser', 'POMIUser']

        users_with_visible_roles = User.objects.filter(
            roles__role__name__in=visible_roles
        ).distinct().prefetch_related('roles').order_by('second_name_rus', 'first_name_rus')

        group_filter = request.GET.get('group')
        if group_filter in ['SPbU', 'POMI']:
            users_with_visible_roles = users_with_visible_roles.filter(group=group_filter)

        serializer = UserInfoSerializer(users_with_visible_roles, many=True)

        return Response({
            'users': serializer.data
        }, status=200)

    except Exception as e:
        return Response({
            'error': 'Ошибка при получении списка пользователей',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#POST /api/submit_science_report_on_checking/{year}/
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_science_report_on_checking(request, year):
    try:
        user = request.user
        year = int(year)

        # if not is_admin_user(user):
        #  return Response({
        #          'error': 'Доступ запрещен. Требуются права администратора.'
        #      }, status=status.HTTP_403_FORBIDDEN)

        current_year = datetime.now().year
        if year < 2000 or year > current_year + 1:
            return Response({
                'error': f'Некорректный год. Допустимый диапазон: 2000-{current_year + 1}'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ScienceReportSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Ошибки валидации данных',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        report_text = serializer.validated_data['year_report']

        try:
            user_report = UserReport.objects.select_related('report').get(
                user=user,
                report__year=year
            )
            year_report = user_report.report
        except UserReport.DoesNotExist:
            year_report = YearReport.objects.create(
                year=year,
                report_text=report_text,
                status='on_checking'
            )
            UserReport.objects.create(user=user, report=year_report)
        else:
            year_report.report_text = report_text
            year_report.status = 'on_checking'
            year_report.save()

        return Response({
            'message': f'Научный отчет за {year} год отправлен на проверку',
            #'report_id': year_report.id,
            #'status': year_report.status,
            #'year': year_report.year,
            #'updated_at': year_report.updated_at.isoformat() if hasattr(year_report, 'updated_at') else None
        }, status=status.HTTP_200_OK)

    except ValueError:
        return Response({
            'error': 'Некорректный формат года'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Ошибка при отправке отчета на проверку',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#POST /api/set_science_report_new_status/{user_id}/{year}/
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_science_report_new_status(request, user_id, year):
    try:
        admin_user = request.user
        target_user_id = int(user_id)
        year = int(year)

        target_user = get_object_or_404(User, id=target_user_id)

        # can_update = (is_master_admin(admin_user) or is_group_admin(admin_user, target_user.group))
        # if not can_update:
        #     return Response({
        #         'error': "Недостаточно прав"
        #     }, status=status.HTTP_403_FORBIDDEN)

        serializer = ScienceReportStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Ошибки валидации данных',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        new_status = serializer.validated_data['new_status']
        admin_comment = serializer.validated_data.get('admin_comment', '')

        try:
            user_report = UserReport.objects.select_related('report').get(
                user=target_user,
                report__year=year
            )
            year_report = user_report.report
        except UserReport.DoesNotExist:
            return Response({
                'error': f'Отчет пользователя за {year} год не найден'
            }, status=status.HTTP_404_NOT_FOUND)

        if year_report.status != 'on_checking':
            return Response({
                'error': f'Отчет должен быть в статусе "on_checking". Текущий статус: {year_report.status}'
            }, status=status.HTTP_400_BAD_REQUEST)

        year_report.status = new_status
        year_report.admin_comment = admin_comment
        year_report.save()

        return Response({
            'message': f'Статус отчета пользователя {target_user.username} за {year} год изменен',
            'report_id': year_report.id,
            'user_id': target_user.id,
            'username': target_user.username,
            'year': year,
            'new_status': new_status,
            'previous_status': 'on_checking',
            'admin_comment': admin_comment,
            'updated_by': admin_user.username
        }, status=status.HTTP_200_OK)

    except ValueError:
        return Response({
            'error': 'Некорректный формат ID пользователя или года'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Ошибка при изменении статуса отчета',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


####################################################################################

# POST /api/impersonate/start/
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def impersonate_start(request):
    try:
        current_user = request.user

        if not is_admin_user(current_user):
            return Response({
                'error': 'Доступ запрещен. Требуются права администратора.'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = ImpersonationStartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Ошибки валидации данных',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        target_user = serializer.validated_data['user_id']

        if not can_impersonate_user(current_user, target_user):
            return Response({
                'error': f'Недостаточно прав для имперсонализации пользователя из группы {target_user.group}'
            }, status=status.HTTP_403_FORBIDDEN)

        tokens = create_impersonation_tokens(current_user, target_user)

        session = ImpersonationSession.objects.create(
            impersonator=current_user,
            target_user=target_user,
            impersonation_token=tokens['token'],
            context_token=tokens['context_token']
        )

        user_roles = UserRole.objects.filter(user=target_user).select_related('role')
        roles_list = [user_role.role.name for user_role in user_roles]

        user_info_data = UserInfoSerializer(target_user).data

        return Response({
            'token': tokens['token'],
            'context_token': tokens['context_token'],
            'user_info': user_info_data,
            'roles': roles_list,
            'impersonator': {
                'id': current_user.id,
                'username': current_user.username,
                'first_name_rus': current_user.first_name_rus,
                'second_name_rus': current_user.second_name_rus,
            },
            'is_impersonating': True,
            'message': f'Режим имперсонализации для пользователя {target_user.username}'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': 'Ошибка при запуске имперсонализации',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# POST /api/impersonate/stop/
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def impersonate_stop(request):
    try:
        serializer = ImpersonationStopSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Неверный или отсутствующий context_token'
            }, status=status.HTTP_400_BAD_REQUEST)

        context_token = serializer.validated_data['context_token']

        context_data, error_message = validate_context_token(context_token)
        if error_message:
            return Response({
                'error': error_message
            }, status=status.HTTP_400_BAD_REQUEST)

        impersonator = context_data['impersonator']
        target_user = context_data['target_user']
        session = context_data['session']

        session.is_active = False
        session.save()

        refresh = RefreshToken.for_user(impersonator)

        user_roles = UserRole.objects.filter(user=impersonator).select_related('role')
        roles_list = [user_role.role.name for user_role in user_roles]

        user_info_data = UserInfoSerializer(impersonator).data

        return Response({
            'token': str(refresh.access_token),
            'user_info': user_info_data,
            'roles': roles_list,
            'is_impersonating': False,
            'message': 'Режим имперсонализации завершен'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': 'Ошибка при завершении имперсонализации',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# GET /api/impersonate/status/
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def impersonate_status(request):
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            status_info = get_impersonation_status(request.user, token)

            return Response(status_info, status=status.HTTP_200_OK)
        else:
            return Response({
                'is_impersonating': False
            }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': 'Ошибка при получении статуса имперсонализации',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#########################################################################################


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        try:
            user = serializer.save()
            user_data = UserSerializer(user).data

            return Response({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name_rus": user.first_name_rus,
                "second_name_rus": user.second_name_rus,
                "middle_name_rus": user.middle_name_rus,
                "group": user.group,
                "message": "User created successfully"
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "error": "Ошибка при создании пользователя",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    else:
        errors = serializer.errors

        if 'username' in errors:
            return Response({
                "error": "Username already exists"
            }, status=status.HTTP_400_BAD_REQUEST)

        elif 'email' in errors:
            return Response({
                "error": "Email already registered"
            }, status=status.HTTP_400_BAD_REQUEST)

        elif 'password' in errors:
            return Response({
                "error": "Password validation failed",
                "details": errors['password']
            }, status=status.HTTP_400_BAD_REQUEST)

        elif 'non_field_errors' in errors:
            return Response({
                "error": errors['non_field_errors'][0]
            }, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({
                "error": "Invalid data",
                "details": errors
            }, status=status.HTTP_400_BAD_REQUEST)


#/get_year_report
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_year_report(request, year):
    try:
        user = request.user
        year = int(year)

        from datetime import datetime
        if year < 2023 or year > 2031:
            return Response({
                'error': f'Некорректный год. Допустимый диапазон: 2023-2031'
            }, status=status.HTTP_400_BAD_REQUEST)

        from django.db.models import Q

        user_posts = Post.objects.filter(
            authors__user=user
        ).filter(
            Q(publication__preprint_date__year=year) |
            Q(publication__submission_date__year=year) |
            Q(publication__acceptance_date__year=year) |
            Q(publication__publication_date__year=year) |
            Q(presentation__presentation_date__year=year)
        ).select_related(
            'publication', 'presentation'
        ).prefetch_related(
            'publication__external_authors'
        ).distinct().order_by('-created_at')

        posts_data = []
        for post in user_posts:
            post_data = {
                'post': {
                    'id': post.id,
                    'type': post.type,
                    'comment': post.comment,
                    'created_at': post.created_at,
                    'updated_at': post.updated_at
                },
                'details': get_post_details(post)
            }
            posts_data.append(post_data)

        try:
            user_report = UserReport.objects.select_related('report').get(
                user=user,
                report__year=year
            )
            year_report = user_report.report
        except UserReport.DoesNotExist:
            year_report = YearReport.objects.create(
                year=year,
                report_text="",
                short_report_text="",
                external_publications="",
                status='wip'
            )
            UserReport.objects.create(user=user, report=year_report)

        report_data = {
            'id': year_report.id,
            'year': year_report.year,
            'report_text': year_report.report_text,
            'short_report_text': year_report.short_report_text,
            'external_publications': year_report.external_publications,
            'status': year_report.status,
            'admin_comment': year_report.admin_comment
            #'created_at': year_report.created_at,
            #'updated_at': year_report.updated_at
        }
        response_data = {
            'posts': posts_data,
            'year_report': report_data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except ValueError:
        return Response({
            'error': 'Некорректный формат года'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Ошибка при получении годового отчета',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# POST /api/get_db_info/
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_db_info(request):
    try:
        data = request.data
        start_date, end_date = get_period(data)

        user_type = data.get("user_type", "all")
        user_id = data.get("user_id")

        users = get_target_users(user_type, user_id)

        include_publications = data.get("publications", False)
        include_presentations = data.get("presentations", False)
        only_published = data.get("only_printed_publications", False)
        include_science_reports = data.get("science_reports", False)

        rtf_lines = []

        def escape_rtf(text):
            if not text:
                return ""
            escaped = ""
            for char in text:
                code = ord(char)
                if code > 127:
                    escaped += f"\\u{code}?"
                else:
                    escaped += char
            return escaped

        def get_full_name(user):
            parts = []
            if user.second_name_rus:
                parts.append(user.second_name_rus)
            if user.first_name_rus:
                parts.append(user.first_name_rus)
            if user.middle_name_rus:
                parts.append(user.middle_name_rus)
            return " ".join(parts) if parts else user.username

        for user in users:
            full_name = get_full_name(user)
            rtf_lines.append(r"{\b " + escape_rtf("Пользователь: ") + escape_rtf(full_name) + r"}\line")

            if include_publications:
                publications = Publication.objects.filter(post__authors__user=user).distinct()
                for pub in publications:
                    status_on_date = get_publication_status_on_date(pub, end_date)
                    if not status_on_date:
                        continue
                    if only_published and status_on_date != "published":
                        continue

                    line = format_publication_for_rtf(pub, end_date)
                    if line:
                        escaped_line = escape_rtf(line)
                        rtf_lines.append(escaped_line + r"\line")

            if include_presentations:
                presentations = Presentation.objects.filter(post__authors__user=user).distinct()
                for pres in presentations:
                    pres_date = pres.presentation_date
                    if pres_date and start_date <= pres_date <= end_date:
                        title = escape_rtf(pres.title or "Без названия")
                        place = escape_rtf(pres.presentation_place or "")
                        line = f"{title} // {place} - {pres_date.isoformat()}"
                        rtf_lines.append(escape_rtf(line) + r"\line")

            if include_science_reports and data.get("load_type") == "yearly":
                science_line = escape_rtf(f"Научный отчет пользователя {full_name}")
                rtf_lines.append(science_line + r"\line")

            rtf_lines.append(r"\line")

        rtf_text = r"{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}}" + "\n" + "\n".join(rtf_lines) + "\n}"

        response = HttpResponse(rtf_text.encode('utf-8'), content_type='application/rtf')
        response['Content-Disposition'] = 'attachment; filename="report.rtf"'
        return response

    except Exception as e:
        error_text = f"Ошибка при выгрузке данных: {str(e)}"
        response = HttpResponse(error_text.encode('utf-8'), content_type='text/plain')
        response.status_code = 500
        return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_report(request, year):
    try:
        user = request.user
        year = int(year)

        if year < 2023 or year > 2031:
            return Response({
                'error': f'Некорректный год. Допустимый диапазон: 2023-2031'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ReportSaveSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Ошибки валидации данных',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_report = UserReport.objects.select_related('report').get(
                user=user,
                report__year=year
            )
            year_report = user_report.report
        except UserReport.DoesNotExist:
            year_report = YearReport.objects.create(
                year=year,
                report_text=serializer.validated_data['report_text'],
                short_report_text=serializer.validated_data.get('short_report_text', ''),
                external_publications=serializer.validated_data.get('external_publications', ''),
                status='wip'
            )
            UserReport.objects.create(user=user, report=year_report)
        else:
            year_report.report_text = serializer.validated_data['report_text']
            year_report.short_report_text = serializer.validated_data.get('short_report_text', '')
            year_report.external_publications = serializer.validated_data.get('external_publications', '')
            year_report.save()

        return Response({
            'status': year_report.status,
            'year': year_report.year
        }, status=status.HTTP_200_OK)

    except ValueError:
        return Response({
            'error': 'Некорректный формат года'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Ошибка при сохранении отчета',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sign_report(request, year):
    try:
        user = request.user
        year = int(year)

        if year < 2023 or year > 2031:
            return Response({
                'error': f'Некорректный год. Допустимый диапазон: 2023-2031'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ReportSaveSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Ошибки валидации данных',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_report = UserReport.objects.select_related('report').get(
                user=user,
                report__year=year
            )
            year_report = user_report.report
        except UserReport.DoesNotExist:
            year_report = YearReport.objects.create(
                year=year,
                report_text=serializer.validated_data['report_text'],
                short_report_text=serializer.validated_data.get('short_report_text', ''),
                external_publications=serializer.validated_data.get('external_publications', ''),
                status='signed'
            )
            UserReport.objects.create(user=user, report=year_report)
        else:
            year_report.report_text = serializer.validated_data['report_text']
            year_report.short_report_text = serializer.validated_data.get('short_report_text', '')
            year_report.external_publications = serializer.validated_data.get('external_publications', '')
            year_report.status = 'signed'
            year_report.save()

        return Response({
            'status': year_report.status,
            'year': year_report.year
        }, status=status.HTTP_200_OK)

    except ValueError:
        return Response({
            'error': 'Некорректный формат года'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Ошибка при подписании отчета',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_to_rework(request, user_id, year):
    try:
        admin_user = request.user
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else ''

        status_info = get_impersonation_status(request.user, token)
        
        if status_info['is_impersonating']:
            admin_user = User.objects.get(id=status_info['impersonator']['id'])
        else:
            admin_user = request.user

        if not is_admin_user(admin_user):
            return Response({
                'error': 'Доступ запрещен. Требуются права администратора.'
            }, status=status.HTTP_403_FORBIDDEN)

        target_user_id = int(user_id)
        year = int(year)
        target_user = get_object_or_404(User, id=target_user_id)

        if year < 2023 or year > 2031:
            return Response({
                'error': f'Некорректный год. Допустимый диапазон: 2023-2031'
            }, status=status.HTTP_400_BAD_REQUEST)

        admin_comment = request.data.get('admin_comment', '')

        try:
            user_report = UserReport.objects.select_related('report').get(
                user=target_user,
                report__year=year
            )
            year_report = user_report.report
        except UserReport.DoesNotExist:
            return Response({
                'error': f'Отчет пользователя {target_user.username} за {year} год не найден'
            }, status=status.HTTP_404_NOT_FOUND)

        year_report.status = 'wip'
        year_report.admin_comment = admin_comment
        year_report.save()

        return Response({
            'user_id': target_user.id,
            'username': target_user.username,
            'year': year,
            'new_status': 'wip',
            'admin_comment': admin_comment,
            'updated_by': admin_user.username
        }, status=status.HTTP_200_OK)

    except ValueError:
        return Response({
            'error': 'Некорректный формат ID пользователя или года'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Ошибка при отправке отчета на доработку',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#POST /api/publications/{id}/upload_file/
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def upload_publication_file(request, id):
    try:
        post_id = int(id)

        publication = get_object_or_404(
            Publication.objects.select_related('post'),
            post_id=post_id
        )

        if not publication.post.authors.filter(user=request.user).exists() and not is_admin_user(request.user):
            return Response({
                'error': 'Доступ запрещен. Вы не являетесь автором этой публикации.'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = FileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Ошибки валидации данных',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        file = serializer.validated_data['file']
        file_type = serializer.validated_data['file_type']
        file_path = get_publication_file_path(publication, file_type, file.name)
        full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)

        os.makedirs(os.path.dirname(full_file_path), exist_ok=True)

        with open(full_file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        file_field = get_file_field_by_type(publication, file_type)
        setattr(publication, file_field, file_path)
        publication.save()

        return Response({
            'message': f'Файл успешно загружен',
            'file_path': file_path,
            'file_type': file_type
        }, status=status.HTTP_200_OK)

    except ValueError:
        return Response({
            'error': 'Некорректный ID публикации'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Ошибка при загрузке файла',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#GET /api/publications/{id}/download_file/?filetype=(preprint|online_first|published)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_publication_file(request, id):
    try:
        post_id = int(id)

        publication = get_object_or_404(
            Publication.objects.select_related('post'),
            post_id=post_id  # Ищем по post_id
        )

        if not is_user_has_access_to_post(request.user, publication.post):
            return Response({
                'error': 'Доступ запрещен. У вас нет прав для просмотра этой публикации.'
            }, status=status.HTTP_403_FORBIDDEN)

        file_type = request.GET.get('filetype')
        if not file_type:
            return Response({
                'error': 'Не указан параметр filetype'
            }, status=status.HTTP_400_BAD_REQUEST)

        if file_type not in ['preprint', 'online_first', 'published']:
            return Response({
                'error': 'Недопустимый тип файла. Допустимые значения: preprint, online_first, published'
            }, status=status.HTTP_400_BAD_REQUEST)

        file_info = get_file_info_by_type(publication, file_type)
        if not file_info:
            return Response({
                'error': f'Файл типа {file_type} не найден для этой публикации'
            }, status=status.HTTP_404_NOT_FOUND)

        if not os.path.exists(file_info['full_path']):
            return Response({
                'error': 'Файл не найден на сервере'
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            file = open(file_info['full_path'], 'rb')
            response = FileResponse(file)

            ext = file_info['name'].split('.')[-1].lower()
            content_types = {
                'pdf': 'application/pdf',
                'doc': 'application/msword',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'txt': 'text/plain'
            }
            content_type = content_types.get(ext, 'application/octet-stream')

            response['Content-Type'] = content_type
            response['Content-Disposition'] = f'attachment; filename="{file_info["name"]}"'

            return response

        except IOError:
            return Response({
                'error': 'Ошибка при чтении файла'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except ValueError:
        return Response({
            'error': 'Некорректный ID публикации'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Ошибка при скачивании файла',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#DELETE /api/publications/{id}/delete_file/?filetype=(preprint|online_first|published)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_publication_file(request, id):
    try:
        post_id = int(id)

        publication = get_object_or_404(
            Publication.objects.select_related('post'),
            post_id=post_id
        )

        if not publication.post.authors.filter(user=request.user).exists() and not is_admin_user(request.user):
            return Response({
                'error': 'Доступ запрещен. Вы не являетесь автором этой публикации.'
            }, status=status.HTTP_403_FORBIDDEN)

        file_type = request.GET.get('filetype')
        if not file_type:
            return Response({
                'error': 'Не указан параметр filetype'
            }, status=status.HTTP_400_BAD_REQUEST)

        if file_type not in ['preprint', 'online_first', 'published']:
            return Response({
                'error': 'Недопустимый тип файла. Допустимые значения: preprint, online_first, published'
            }, status=status.HTTP_400_BAD_REQUEST)

        success = delete_publication_file_util(publication, file_type)

        if success:
            return Response({
                'message': f'Файл типа {file_type} успешно удален'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': f'Файл типа {file_type} не найден или не может быть удален'
            }, status=status.HTTP_404_NOT_FOUND)

    except ValueError:
        return Response({
            'error': 'Некорректный ID публикации'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Ошибка при удалении файла',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)