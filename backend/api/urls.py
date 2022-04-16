from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import UsersViewSet

from .views import IngredientsViewSet, RecipesViewSet, TagsViewSet

app_name = 'api'

router = DefaultRouter()

router.register(
    'users',
    UsersViewSet,
    basename='users'
)
router.register(
    'ingredients',
    IngredientsViewSet,
    basename='ingredients'
)
router.register(
    'recipes',
    RecipesViewSet,
    basename='recipes'
)
router.register(
    'tags',
    TagsViewSet,
    basename='tags'
)

urlpatterns = (
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
)
