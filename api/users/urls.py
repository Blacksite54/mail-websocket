from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.users.views import UserViewSet, import_messages

router = DefaultRouter(trailing_slash=True)
router.register(r"user", UserViewSet)

urlpatterns = [
    path("import-messages/", import_messages, name="import_messages"),
    path(r"", include(router.urls)),
]