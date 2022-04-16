from rest_framework import serializers

from .models import Follow, User


class CustomUsersSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        extra_kwargs = {"password": {'write_only': True}}
        lookup_field = 'username'

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user.id
        return Follow.objects.filter(
            user=user,
            author=obj).exists()


class FollowSerializer(serializers.ModelSerializer):
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
        extra_kwargs = {"password": {'write_only': True}}
        lookup_field = 'username'

        def get_is_subscribed(self, obj):
            user = self.context.get('request').user.id
            return obj.author.filter(
                user=user).exists()

        def get_recipes(self, obj):
            from api.serializers import RecipeShortSerializer
            recipes = obj.recipes.only(
                'id',
                'name',
                'image',
                'cooking_time'
            )
            return RecipeShortSerializer(recipes, many=True).data

        def get_recipes_count(self, obj):
            return obj.recipes.count()
