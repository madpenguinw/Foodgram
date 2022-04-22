from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import (Favorite, Ingredient, IngredientsAmount, Recipe,
                            ShoppingCart, Tag)
from users.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .filters import IngredientFilter, RecipeFilter
from .pagination import PagePagination
from .serializers import (IngredientsSerializer, RecipeCreateSerializer,
                          RecipeGetSerializer, RecipeShortSerializer,
                          TagSerializer)


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeGetSerializer
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = PagePagination
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def data_for_funcs(self, request, obj):
        recipe_pk = int(self.kwargs['pk'])
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        if request.method == 'POST':
            serializer = RecipeShortSerializer(recipe)
            obj.objects.create(user=self.request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if obj.objects.filter(
                    user=self.request.user, recipe=recipe).exists():
                obj.objects.get(
                    user=self.request.user, recipe=recipe
                    ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'errors': 'Нет в списке'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return self.data_for_funcs(request, Favorite)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self.data_for_funcs(request, ShoppingCart)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = IngredientsAmount.objects.select_related(
            'recipe',
            'ingredient'
        )
        ingredients = ingredients.filter(
            recipe__shopping_cart_recipe__user=request.user)
        ingredients = ingredients.values(
                'ingredient__name', 'ingredient__measurement_unit')
        ingredients = ingredients.annotate(ingredient_total=Sum('amount'))
        ingredients = ingredients.order_by('ingredient__name')
        ingredients_to_buy = 'Список покупок: \n'
        for ingredient in ingredients:
            ingredients_to_buy += (
                f'{ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]}) - '
                f'{ingredient["ingredient_total"]} \n'
            )
        response = HttpResponse(
            ingredients_to_buy,
            content_type='text/plain; charset=utf8'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"')
        return response
