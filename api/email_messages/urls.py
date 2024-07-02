from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.email_messages.views import MessageViewSet

router = DefaultRouter(trailing_slash=True)
router.register(r"email_messages", MessageViewSet)

urlpatterns = [
    path(r"", include(router.urls)),
]