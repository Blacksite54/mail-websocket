import yagmail
import json

from channels.generic.websocket import AsyncWebsocketConsumer

from api.messages.models import Message


class ImportConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, request, text_data):
        user = getattr(request, "user", None)
        text_data_json = json.loads(text_data)
        email_service = text_data_json['email_service']
        email = text_data_json['email']
        password = text_data_json['password']

        # Логика импорта сообщений из почтового ящика
        yag = yagmail.SMTP(email, password)
        messages = yag.inbox()

        for message in messages:
            Message.objects.create(**message, user=user)

        # Отправка обновлений клиенту через WebSocket
        await self.send(text_data=json.dumps({
            'progress': '50%',
            'message': 'Импорт сообщений в процессе...'
        }))

        # ...

        await self.send(text_data=json.dumps({
            'progress': '100%',
            'message': 'Импорт сообщений завершен'
        }))