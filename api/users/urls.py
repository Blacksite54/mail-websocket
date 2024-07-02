from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.users.views import UserViewSet

router = DefaultRouter(trailing_slash=True)
router.register(r"user", UserViewSet)

urlpatterns = [
    path(r"", include(router.urls)),
]