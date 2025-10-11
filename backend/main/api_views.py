import os

from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .serializer import UserAuthSerializer, LoginSerializer, UserSerializer, OwnerCheckSerializer, \
    PublicationCreateSerializer, PublicationSerializer, RegisterSerializer, UserListSerializer, ReportSerializer, \
    ReportCreateSerializer
from .models import User, Post, Report
from .views import generate_user_report


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        user_data = UserAuthSerializer(user).data

        return Response({
            'token': str(refresh.access_token),
            #'refresh': str(refresh),
            'user': user_data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


#GET /api/my_publications/
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_publications(request):
    publications = Post.objects.filter(created_by=request.user).order_by('-created_at')
    serializer = PublicationSerializer(publications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#GET /api/all_publications/
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_publications(request):
    publications = Post.objects.order_by('-created_at')
    serializer = PublicationSerializer(publications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# GET /api/publications/{id}/
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_publication_detail(request, id):
    publication = get_object_or_404(Post, id=id)
    serializer = PublicationSerializer(publication)
    return Response(serializer.data, status=status.HTTP_200_OK)


# POST /api/publications/
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_publication(request):
    data = request.data.copy()

    authors_input = data.get('authors', '')
    authors_list = []

    if authors_input and authors_input != 'string':
        if isinstance(authors_input, str):
            authors_input = authors_input.strip('[]')
            for aid in authors_input.split(','):
                aid = aid.strip()
                if aid and aid.isdigit():
                    authors_list.append(int(aid))
        elif isinstance(authors_input, list):
            for aid in authors_input:
                if isinstance(aid, int):
                    authors_list.append(aid)
                elif isinstance(aid, str) and aid.isdigit():
                    authors_list.append(int(aid))

    if request.user.id not in authors_list:
        authors_list.append(request.user.id)

    data['authors'] = authors_list

    serializer = PublicationCreateSerializer(data=data)

    if serializer.is_valid():
        publication = serializer.save()

        return Response({
            'id': publication.id,
            'message': 'Публикация успешно создана'
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
                "first_name": user.first_name,
                "last_name": user.last_name,
                "middle_name": user.middle_name,
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_report(request):
    """
    Генерация отчета
    POST /api/reports/
    """
    if not request.user.is_staff:
        return Response({
            "error": "Доступ запрещен. Требуются права администратора."
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = ReportCreateSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        try:
            report = serializer.save()

            response_serializer = ReportSerializer(report)

            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "error": "Ошибка при создании отчета",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response({
            "error": "Неверные данные запроса",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


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
    Получение списка отчетов пользователя
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

        report_text = f"# Отчёт по публикациям пользователя {user.last_name} {user.first_name}{ (" " + user.middle_name) or '' } за {year} год\n\n"
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