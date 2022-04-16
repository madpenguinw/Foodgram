from django.contrib import admin

from .models import Ingredient, IngredientsQuantity, Recipe, Tag


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'units',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
    )
    search_fields = ('author', 'name',)
    list_filter = ('author', 'name',)
    empty_value_display = '-пусто-'


@admin.register(IngredientsQuantity)
class IngredientsQuantityAdmin(admin.ModelAdmin):
    list_display = (
        'ingredients',
        'recipe',
        'quantity',
    )
    empty_value_display = '-пусто-'
