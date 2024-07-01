from rest_framework import serializers

from api.users.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    login = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = "__all__"

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance
