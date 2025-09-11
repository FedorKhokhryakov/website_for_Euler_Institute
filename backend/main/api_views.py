from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .serializer import UserAuthSerializer, LoginSerializer, UserSerializer, OwnerCheckSerializer, \
    PublicationCreateSerializer, PublicationSerializer, RegisterSerializer, UserListSerializer
from .models import User, Post


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


#GET /api/publications/
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_publications(request):
    publications = Post.objects.filter(authors__id=request.user.id).order_by('-created_at')
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

    if 'authors' not in data:
        data['authors'] = [request.user.id]
    elif request.user.id not in data['authors']:
        data['authors'].append(request.user.id)

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

    is_owner = publication.authors.filter(id=request.user.id).exists()
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