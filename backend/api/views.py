from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (
    Favourite, Ingredient, IngredientInRecipe,
    Recipe, ShoppingCart, Tag
)
from .filters import IngredientFilter, TagRecipeFilter
from .paginators import LimitPageNumberPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeWriteSerializer,
    TagSerializer
)
from .utils import ingredients_export


class IngredientViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = '^name'


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeWriteSerializer
    pagination_class = LimitPageNumberPagination
    filter_class = TagRecipeFilter
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.__add_object(Favourite, request.user, pk)
        if request.method == 'DELETE':
            return self.__delete_object(Favourite, request.user, pk)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.__add_object(ShoppingCart, request.user, pk)
        if request.method == 'DELETE':
            return self.__delete_object(ShoppingCart, request.user, pk)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def __add_object(self, model, user, pk):
        if model.objects.filter(user=user, recipe_id=pk).exists():
            return False
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        return True

    def __delete_object(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe_id=pk)
        if not obj.exists():
            return False
        obj.delete()
        return True

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return ingredients_export(self, request, ingredients)
