from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.messages.filters import MessageFilter
from api.messages.models import Message
from api.messages.serializers import MessageSerializer, MessageListSerializer


class MessageViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Message.objects.prefetch_related(
        "user"
    )
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = MessageFilter

    def get_queryset(self):
        queryset = self.queryset
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return MessageListSerializer
        return MessageSerializer

    def list(self, request, *args, **kwargs):
        user = getattr(request, "user", None)

        self.check_object_permissions(request, user)

        messages = self.filter_queryset(self.get_queryset().filter(user__pk=user.pk))

        page = self.paginate_queryset(messages)

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk):
        user = getattr(request, "user", None)

        self.check_object_permissions(request, user)

        try:
            message = (
                self.get_queryset()
                .filter(user__pk=user.pk)
                .filter(pk=pk)
                .get()
            )

        except Message.DoesNotExist:
            return Response(
                {"errors": {"detail": [_("Not found or permission denied.")]}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            message,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)
