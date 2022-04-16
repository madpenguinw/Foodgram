from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import (Favorite, Ingredient, IngredientsQuantity, Recipe,
                            ShoppingCart, Tag)
from users.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly

from .pagination import PagePagination
from .serializers import (IngredientsSerializer, RecipeSerializer,
                          RecipeShortSerializer, TagSerializer)


class TagsViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = PagePagination
    filter_backends = (filters.SearchFilter,)
    filterset_fields = (
        'author',
        'tag',
    )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['GET', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'GET':
            serializer = RecipeShortSerializer(recipe)
            Favorite.objects.create(user=self.request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            Favorite.objects.get(
                user=self.request.user, recipe=recipe
                ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['GET', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'GET':
            serializer = RecipeShortSerializer(recipe)
            ShoppingCart.objects.create(user=self.request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            ShoppingCart.objects.get(
                user=self.request.user, recipe=recipe
                ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = IngredientsQuantity.objects.filter(
            recipe__is_in_shopping_cart=request.user).values(
                'ingredient__name', 'ingredient__unit'
            ).order_by(
                'ingredient__name'
            ).annotate(ingredient_total=Sum('quantity'))
        ingredients_to_buy = 'Список покупок: \n'
        for ingredient in ingredients:
            ingredients_to_buy += (
                f'{ingredient["ingredient"]} '
                f'({ingredient["unit"]}) - '
                f'{ingredient["quantity"]} \n'
            )
        response = HttpResponse(
            ingredients_to_buy,
            content_type='text/plain; charset=utf8'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"')
        return response
