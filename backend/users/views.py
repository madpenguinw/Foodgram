from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.pagination import PagePagination
from api.serializers import FollowSerializer
from .models import Follow, User
from .serializers import (CustomUsersSerializer, SetPasswordSerializer)


class UsersViewSet(UserViewSet):
    serializer_class = CustomUsersSerializer
    pagination_class = PagePagination
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'subscribe':
            return FollowSerializer
        return super().get_serializer_class()

    @action(
        detail=False, methods=['GET'], permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = Follow.objects.filter(user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = FollowSerializer(
                Follow.objects.create(user=request.user, author=author),
                context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            Follow.objects.filter(
                user=request.user,
                author=author
            ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def set_password(request):
    serializer = SetPasswordSerializer(
        data=request.data,
        context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'message': 'Пароль успешно изменен'},
            status=status.HTTP_201_CREATED)
    return Response(
        {'error': 'Введенные данные некорректны'},
        status=status.HTTP_400_BAD_REQUEST)
