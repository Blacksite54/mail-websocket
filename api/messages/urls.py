from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.messages.views import MessageViewSet

router = DefaultRouter(trailing_slash=True)
router.register(r"messages", MessageViewSet)

urlpatterns = [
    path(r"", include(router.urls)),
]