import os

from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from django.db.models import Exists, OuterRef
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .serializer import *
from .models import *
from .utils import *

SERIALIZER_MAP = {
    'publication': (Publication, PublicationReadSerializer),
    'monograph': (Monograph, MonographSerializer),
    'presentation': (Presentation, PresentationReadSerializer),
    'lectures': (Lecture, LectureSerializer),
    'patents': (Patent, PatentSerializer),
    'supervision': (Supervision, SupervisionSerializer),
    'editing': (Editing, EditingSerializer),
    'editorial_board': (EditorialBoard, EditorialBoardSerializer),
    'org_work': (OrgWork, OrgWorkSerializer),
    'opposition': (Opposition, OppositionSerializer),
    'grants': (Grant, GrantSerializer),
    'awards': (Award, AwardSerializer),
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


#GET /api/my_publications/
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_posts(request):
    posts = Post.objects.filter(authors__user=request.user).select_related(
        'publication', 'monograph', 'presentation', 'lecture', 'patent',
        'supervision', 'editing', 'editorial_board', 'org_work',
        'opposition', 'grant', 'award'
    ).prefetch_related('authors')
    
    result = []
    
    for post in posts:
        post_data = PostSerializer(post).data
        
        detailed_data = None
        model_class, serializer_class = SERIALIZER_MAP[post.post_type]
        related_name = post.post_type
        if hasattr(post, related_name):
            detailed_obj = getattr(post, related_name)
            detailed_data = serializer_class(detailed_obj).data
        
        result.append({
            'post': post_data,
            'details': detailed_data,
            'type': post.post_type
        })
    
    return Response(result, status=status.HTTP_200_OK)


#GET /api/all_publications/
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_publications(request):
    publications = Post.objects.order_by('-created_at')
    serializer = PublicationReadSerializer(publications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


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
def create_post(request):
    try:
        data = request.data.copy()

        if 'post' not in data or 'type' not in data['post']:
            return Response({
                'error': 'Отсутствуют обязательные поля: post и post.type'
            }, status=status.HTTP_400_BAD_REQUEST)

        post_type = data['post']['type']

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


        serializer = PostWithDetailsCreateSerializer(
            data=data,
            context={'request': request}
        )

        if serializer.is_valid():
            post = serializer.save()

            details = data.get('details', {})
            internal_authors = details.get('internal_authors_list', [])
            
            for user_id in internal_authors:
                try:
                    user_obj = User.objects.get(id=user_id)
                    if not PostAuthor.objects.filter(post=post, user=user_obj).exists():
                        PostAuthor.objects.create(post=post, user=user_obj)
                except User.DoesNotExist:
                    continue

            return Response({
                'id': post.id,
                'message': f'{post_type.capitalize()} успешно создан',
                'type': post_type
            }, status=status.HTTP_201_CREATED)
        else:
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

        data = request.data

        if 'post' not in data:
            return Response({
                'error': 'Отсутствует обязательный раздел "post"'
            }, status=status.HTTP_400_BAD_REQUEST)

        post_serializer = PostCreateSerializer(post, data=data['post'], partial=False)
        if not post_serializer.is_valid():
            return Response({
                'error': 'Ошибки валидации данных поста',
                'details': post_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        post_serializer.save()

        details_data = data.get('details', {})
        update_errors = update_post_details(post, details_data)

        if post.type == 'publication' and hasattr(post, 'publication'):
            external_authors = details_data.get('external_authors_list', [])
            post.publication.external_authors.all().delete()
            for author_name in external_authors:
                if author_name.strip():
                    ExternalPublicationAuthor.objects.create(
                        publication=post.publication,
                        author_name=author_name.strip()
                    )

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

        # if not is_admin_user(current_user):
        #     return Response({
        #         'error': 'Доступ запрещен. Требуются права администратора.'
        #     }, status=status.HTTP_403_FORBIDDEN)

        admin_role_exists = UserRole.objects.filter(
            user_id=OuterRef('id'),
            role__name__in=['MasterAdmin', 'SPbUAdmin', 'POMIAdmin']
        )
        regular_users = User.objects.annotate(
            has_admin_role=Exists(admin_role_exists)
        ).filter(has_admin_role=False).prefetch_related('roles').order_by('second_name_rus', 'first_name_rus')

        group_filter = request.GET.get('group')
        if group_filter in ['SPbU', 'POMI']:
            regular_users = regular_users.filter(group=group_filter)

        serializer = UserInfoSerializer(regular_users, many=True)

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

#GET /api/publications/{id}/check-owner/
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_publication_owner(request, id):
    publication = get_object_or_404(Post, id=id)

    is_owner = publication.created_by == id
    is_admin = request.user.is_admin or request.user.is_superuser

    serializer = OwnerCheckSerializer({
        'isOwner': is_owner,
        'isAdmin': is_admin
    })

    return Response(serializer.data, status=status.HTTP_200_OK)


#GET /api/users/{id}/
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request, id):
    user = get_object_or_404(User, id=id)
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list(request):
    users = User.objects.all()
    serializer = UserListSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_request(request):
    users = User.objects.all()

    data = []
    for user in users:
        full_name = " ".join(
            filter(None, [user.last_name, user.first_name, getattr(user, "middle_name", "")])
        )
        data.append({
            "id": user.id,
            "full_name": full_name.strip(),
            "email": user.email,
            "position": getattr(user, "position", ""),
        })

    return Response(data, status=status.HTTP_200_OK)

#/get_year_report
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_year_report(request, year):
    try:
        user = request.user
        year = int(year)

        from datetime import datetime
        current_year = datetime.now().year
        if year < 2000 or year > current_year + 1:
            return Response({
                'error': f'Некорректный год. Допустимый диапазон: 2000-{current_year + 1}'
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
                report_text=f"Отчет за {year} год",
                status='idle'
            )
            UserReport.objects.create(user=user, report=year_report)

        report_data = {
            'id': year_report.id,
            'year': year_report.year,
            'report_text': year_report.report_text,
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_report(request, id):
    """
    Скачивание отчета
    GET /api/reports/{id}/download/
    """
    report = get_object_or_404(Report, id=id)

    if not (request.user.is_staff or report.created_by == request.user or report.user == request.user):
        return Response({
            "error": "Доступ запрещен"
        }, status=status.HTTP_403_FORBIDDEN)

    if report.status != 'completed':
        return Response({
            "error": "Отчет еще не готов",
            "status": report.status
        }, status=status.HTTP_400_BAD_REQUEST)

    if not report.file_path or not os.path.exists(report.file_path):
        return Response({
            "error": "Файл отчета не найден"
        }, status=status.HTTP_404_NOT_FOUND)

    try:
        content_types = {
            'rtf': 'application/rtf',
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }

        content_type = content_types.get(report.format, 'application/octet-stream')
        response = FileResponse(open(report.file_path, 'rb'), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(report.file_path)}"'

        return response

    except Exception as e:
        return Response({
            "error": "Ошибка при загрузке файла",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_reports(request):
    """
    GET /api/reports/
    """
    if request.user.is_staff:
        reports = Report.objects.all()
    else:
        reports = Report.objects.filter(user=request.user)

    serializer = ReportSerializer(reports, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def download_report_api(request):
    if not request.user.is_staff:
        return Response({
            "error": "Доступ запрещен. Требуются права администратора."
        }, status=status.HTTP_403_FORBIDDEN)

    user_id = request.data.get('user_id')
    year = request.data.get('year')
    format_type = request.data.get('format', 'rtf')

    if not user_id or not year:
        return Response({
            "error": "Обязательные поля: user_id и year"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        year = int(year)
    except (ValueError, TypeError):
        return Response({
            "error": "Неверный формат года"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            "error": "Пользователь не найден"
        }, status=status.HTTP_404_NOT_FOUND)

    try:
        posts = Post.objects.filter(created_by=user, year=year).order_by("type", "year")

        from collections import defaultdict
        grouped = defaultdict(list)
        for post in posts:
            grouped[post.get_type_display()].append(post)

        report_text = f"# Отчёт по публикациям пользователя {user.last_name} {user.first_name}{ (' ' + user.middle_name) or '' } за {year} год\n\n"
        for type_name, items in grouped.items():
            report_text += f"## {type_name}\n"
            for p in items:
                report_text += f"- {p.year}: {p.title}, ID: {p.article_identification_number or 'Без номера'}"
                if p.web_page:
                    report_text += f" ([ссылка]({p.web_page}))"
                report_text += "\n"
            report_text += "\n\n"
            
    except Exception as e:
        return Response({
            "error": "Ошибка при генерации отчета",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    import tempfile
    import os
    from django.utils.text import slugify
    from datetime import datetime
    
    try:
        import pypandoc
        try:
            pypandoc.get_pandoc_version()
        except OSError:
            pypandoc.download_pandoc()
    except ImportError:
        return Response({
            "error": "Библиотека pypandoc не установлена"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    filename = f"report_{slugify(user.username)}_{year}_{datetime.now().strftime('%Y%m%d')}.rtf"
    temp_dir = tempfile.gettempdir()
    rtf_path = os.path.join(temp_dir, filename)

    try:
        pypandoc.convert_text(report_text, "rtf", format="md", outputfile=rtf_path, extra_args=["--standalone"])

        with open(rtf_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/rtf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            import threading
            def delete_file_later(file_path):
                import time
                time.sleep(15)
                try:
                    os.remove(file_path)
                except:
                    pass
            
            threading.Thread(target=delete_file_later, args=(rtf_path,)).start()
            
            return response

    except Exception as e:
        return Response({
            "error": "Ошибка при генерации RTF файла",
            "details": str(e)
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
