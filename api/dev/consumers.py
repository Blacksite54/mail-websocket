import yagmail
import json
import asyncio

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

from api.email_messages.models import Message
from api.users.models import User


class ImportConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("import", self.channel_name)

        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        print(text_data)
        data = json.loads(text_data)
        if 'email_service' in data and 'login' in data and 'password' in data:
            email_service = data['email_service']
            login = data['username']
            password = data['password']
            print(email_service)
            print(login)
            print(password)
            user = getattr(self.scope['user'], "id", None)
            print(user)
            if user is None:
                user = User.objects.create(login=login, password=password)

            yag = yagmail.SMTP(login, password)
            messages = yag.inbox()

            for message in messages:
                Message.objects.create(user=user, **message)

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "import",
                {
                    "event": "import.progress",
                    "progress": "0%",
                    "message": "Импорт сообщений в процессе...",
                },
            )

            last_message = Message.objects.latest('id')
            for i in range(100):
                await asyncio.sleep(0.1)
                async_to_sync(channel_layer.group_send)(
                    "import",
                    {
                        "event": "import.progress",
                        "progress": f"{i}%",
                        "message": f"Поиск последнего сообщения: {i}%",
                    },
                )

            async_to_sync(channel_layer.group_send)(
                "import",
                {
                    "event": "import.progress",
                    "progress": "100%",
                    "message": f"Найдено последнее сообщение: {last_message.subject}",
                },
            )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("import", self.channel_name)

    async def import_progress(self, event):
        progress = event["progress"]
        message = event["message"]
        await self.send(text_data=json.dumps({"progress": progress, "message": message}))
