from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientsAmount, Recipe,
                            ShoppingCart, Tag)
from users.serializers import CustomUsersSerializer
from users.models import User, Follow


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientsAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class AddIngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsAmount
        fields = ("id", "amount")


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = CustomUsersSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = AddIngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    cooking_time = serializers.IntegerField(min_value=1, max_value=None)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'tags',
            'text',
            'ingredients',
            'cooking_time'
        )

    def get_is_favorited(self, recipe):
        favorite = self.context['request'].user.user_favorite
        return favorite.filter(recipe=recipe).exists()

    def to_representation(self, instance):
        serializer = RecipeGetSerializer(instance)
        return serializer.data

    def validate(self, data):
        ingredients = data['ingredients']
        if not ingredients:
            raise serializers.ValidationError(
                'Добавьте ингридиент')
        unique_set = set()
        for ingredient_data in ingredients:
            current_ingredient = ingredient_data['id']
            if current_ingredient in unique_set:
                raise serializers.ValidationError(
                    'Этот ингредиент уже в списке')
            unique_set.add(current_ingredient)
            current_amount = ingredient_data['amount']
            if int(current_amount) < 0:
                raise serializers.ValidationError(
                    'Количество ингредиентов не может быть отрицательным')
        return data

    def create_ingredients_amount(self, obj, ingredients):
        for ingredient in ingredients:
            IngredientsAmount.objects.create(
                recipe=obj,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe.recipe_ingredients.all().delete()
        self.create_ingredients_amount(recipe, ingredients)
        return recipe

    def update(self, obj, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            self.create_ingredients_amount(ingredients, obj)
        if 'tags' in validated_data:
            obj.tags.set(validated_data.pop('tags'))
        return super().update(obj, validated_data)


class RecipeGetSerializer(serializers.ModelSerializer):
    author = CustomUsersSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientsAmountSerializer(
        many=True,
        source='recipe_ingredients'
    )
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'tags',
            'text',
            'ingredients',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    email = serializers.ReadOnlyField(source='author.email')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj.user, author=obj.author).exists()

    def get_recipes(self, obj):
        from api.serializers import RecipeShortSerializer
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author).order_by(
            '-pub_date')
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return RecipeShortSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
