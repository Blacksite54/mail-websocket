from rest_framework import serializers

from api.email_messages.models import Message


class MessageSerializer(serializers.ModelSerializer[Message]):
    title = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    date_dispatch = serializers.DateField()
    date_receipt = serializers.DateField()
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    attachments = serializers.FileField(required=False)

    class Meta:
        model = Message
        fields = '__all__'


    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        return Message.objects.create(**validated_data)


class MessageListSerializer(serializers.ModelSerializer[Message]):
    title = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    date_dispatch = serializers.DateField()
    date_receipt = serializers.DateField()
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Message
        fields = {
            "title",
            "date_dispatch",
            "date_receipt",
            "description",
        }
