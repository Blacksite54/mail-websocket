from django.shortcuts import render

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from api.users.models import User
from api.users.serializers import UserSerializer


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = self.queryset
        return queryset

    def create(self, request, *args, **kwargs):
        serializer_data = request.data

        serializer = self.serializer_class(
            data=serializer_data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


def import_messages(request):
    return render(request, 'index.html', {})

