from django.contrib import admin
from django.contrib.admin import display

from .models import (
    Favourite, Ingredient, IngredientInRecipe,
    Recipe, ShoppingCart, Tag, TagInRecipe
)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'author', 'added_in_favorites')
    readonly_fields = ('added_in_favorites',)
    list_filter = ('author', 'name', 'tags',)
    search_fields = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
    inlines = [IngredientInRecipeInline]

    @display(description='Количество в избранных')
    def added_in_favorites(self, obj):
        return obj.favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    list_filter = ('user',)
    search_fields = ('user',)
    empty_value_display = '-пусто-'


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    list_filter = ('user',)
    search_fields = ('user',)
    empty_value_display = '-пусто-'


@admin.register(TagInRecipe)
class TagInRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag',)
