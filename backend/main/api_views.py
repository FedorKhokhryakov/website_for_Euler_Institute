from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .serializer import UserAuthSerializer, LoginSerializer, UserSerializer, OwnerCheckSerializer, \
    PublicationCreateSerializer, PublicationSerializer
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
    is_admin = request.user.is_staff or request.user.is_superuser

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
def login_view(request):
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        user_data = UserSerializer(user).data

        return Response({
            'token': str(refresh.access_token),
            'user': user_data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)