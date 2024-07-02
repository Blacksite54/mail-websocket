import yagmail
import json
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer

from api.messages.models import Message


class ImportConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        email_service = text_data_json['email_service']
        email = text_data_json['email']
        password = text_data_json['password']

        # Логика импорта сообщений из почтового ящика
        yag = yagmail.SMTP(email, password)
        messages = yag.inbox()

        user = getattr(self.scope['user'], "id", None)

        for message in messages:
            Message.objects.create(user=user, **message)

        # Отправка обновлений клиенту через WebSocket
        await self.send(text_data=json.dumps({
            'progress': '0%',
            'message': 'Импорт сообщений в процессе...'
        }))

        # Поиск последнего добавленного сообщения
        last_message = Message.objects.latest('id')

        # Отправка прогресса и сообщения через WebSocket
        for i in range(100):
            await asyncio.sleep(0.1)
            await self.send(text_data=json.dumps({
                'progress': f'{i}%',
                'message': f'Поиск последнего сообщения: {i}%',
            }))

        # Отправка информации о найденном сообщении
        await self.send(text_data=json.dumps({
            'progress': '100%',
            'message': f'Найдено последнее сообщение: {last_message.subject}',
        }))