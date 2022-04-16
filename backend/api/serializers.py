from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientsQuantity, Recipe,
                            ShoppingCart, Tag)
from users.serializers import CustomUsersSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientsQuantitySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.units'
    )

    class Meta:
        model = IngredientsQuantity
        fields = (
            'id'
            'ingredients',
            'recipe',
            'quantity',
        )


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'units'
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUsersSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientsQuantitySerializer(
        many=True,
        source='ingredient_in_recipe'
    )
    tag = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tag',
            'cooking_time',
            'pub_date',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, id=obj.id).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=user, id=obj.id).exists()
        return False

    def create_ingredients_quantity(self, recipe, ingredients):
        for ingredient in ingredients:
            IngredientsQuantity.objects.create(
                recipe=recipe,
                ingredients=ingredient.get('ingredients'),
                quantity=ingredient.get('quantity')
            )

    def create(self, validated_data):
        image = validated_data.pop('image')
        recipe = Recipe.objects.create(image=image, **validated_data)
        ingredients = validated_data.pop('ingredient_in_recipe')
        tag = validated_data.pop('tag')
        recipe.tag.set(tag)
        self.create_ingredients_quantity(recipe, ingredients)
        return recipe

    def update(self, obj, validated_data):
        obj.name = validated_data.get('name', obj.name)
        obj.image = validated_data.get('image', obj.image)
        obj.text = validated_data.get('text', obj.text)
        obj.cooking_time = validated_data.get(
            'cooking_time',
            obj.cooking_time
        )
        obj.tags.set(validated_data.get('tags'))
        self.create_ingredients_quantity(
            obj, validated_data.get('ingredient_in_recipe'))
        obj.save()
        return obj


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
