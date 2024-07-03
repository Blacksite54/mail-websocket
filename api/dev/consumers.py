import email
import imaplib
import json
import asyncio
import html2text

from datetime import datetime

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from email.header import decode_header

from asgiref.sync import async_to_sync

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

from api.email_messages.models import Message
from api.users.models import User


class ImportConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        email_service = data["emailService"]
        login = data["login"]
        password = data["password"]
        user = getattr(self.scope['user'], "id", None)

        if user is None:
            user = User.objects.create(login=login, password=password)
        else:
            user = User.objects.get(id=user)

        connection = imaplib.IMAP4_SSL(f'imap.{email_service}')
        connection.login(login, password)

        # Выбор почтового ящика (inbox)
        connection.select('INBOX')

        # Поиск писем и получение их данных
        result, data = connection.search(None, 'ALL')
        total_messages = len(data[0].split())

        await self.send(text_data=json.dumps({'total_messages': total_messages}))
        await asyncio.sleep(0.1)
        remaining_messages = total_messages

        for num in data[0].split():
            result, message_data = connection.fetch(num, '(RFC822)')
            raw_email = message_data[0][1]

            # Парсинг сырого email
            email_message = email.message_from_bytes(raw_email)

            # Получение заголовка
            subject = self.get_email_subject(email_message)

            # Получение даты отправки и получения
            date_dispatch, date_receipt = self.get_email_dates(email_message)

            # Получение содержимого
            message_content = self.get_email_content(email_message)

            # Получение вложений
            attachments = self.get_email_attachments(email_message)
            print(subject)
            # Создание сообщения в базе данных
            message = Message.objects.create(
                title=subject,
                date_dispatch=date_dispatch,
                date_receipt=date_receipt,
                description=message_content,
                user=user
            )

            for filename, attachment in attachments:
                temp_file = NamedTemporaryFile()
                temp_file.write(attachment)
                temp_file.flush()
                message.attachments.save(filename, File(temp_file))

            remaining_messages -= 1
            await self.send(text_data=json.dumps({'remaining_messages': remaining_messages}))
            await asyncio.sleep(0.1)
            # Отправка сообщения на фронтенд
            await self.send(text_data=json.dumps({
                'emails': [
                    {
                        'subject': subject,
                        'description': message_content,
                        'received_at': date_receipt
                    }
                ]
            }))
            await asyncio.sleep(0.2)

        # Закрытие соединения
        connection.close()
        connection.logout()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("import", self.channel_name)

    def get_email_subject(self, email_message):
        if 'Subject' in email_message and email_message['Subject'] is not None:
            subject, encoding = decode_header(email_message['Subject'])[0]
            if isinstance(subject, bytes):
                try:
                    subject = subject.decode(encoding)
                except LookupError:
                    try:
                        subject = subject.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            subject = subject.decode('latin-1')
                        except UnicodeDecodeError:
                            subject = subject.decode('ascii', errors='ignore')
        else:
            subject = "No subject"
        return subject

    def get_email_dates(self, email_message):
        date_dispatch = email_message['Date']
        date_receipt = email_message['Received'].split(';')[-1].strip()

        date_dispatch = date_dispatch.split("+")[0]
        if len(date_dispatch.split(",")) > 1:
            date_dispatch = date_dispatch.split(",")[1].strip()
        else:
            date_dispatch = date_dispatch
        date_dispatch = date_dispatch.split("-")[0].strip()
        date_dispatch = date_dispatch.split(" ")
        if date_dispatch[-1] == "GMT":
            date_dispatch = " ".join(date_dispatch[:-1])
        else:
            date_dispatch = " ".join(date_dispatch)
        date_dispatch = datetime.strptime(date_dispatch, '%d %b %Y %H:%M:%S')

        date_receipt = date_receipt.split("+")[0]
        if len(date_receipt.split(",")) > 1:
            date_receipt = date_receipt.split(",")[1].strip()
        else:
            date_receipt = date_receipt
        date_receipt = date_receipt.split("-")[0].strip()
        date_receipt = date_receipt.split(" ")
        if date_receipt[-1] == "GMT":
            date_receipt = " ".join(date_receipt[:-1])
        else:
            date_receipt = " ".join(date_receipt)
        date_receipt = datetime.strptime(date_receipt, '%d %b %Y %H:%M:%S')


        date_dispatch = date_dispatch.strftime('%Y-%m-%d')
        date_receipt = date_receipt.strftime('%Y-%m-%d')

        return date_dispatch, date_receipt

    def get_email_content(self, email_message):
        message_content = ''
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    body = part.get_payload(decode=True)
                    charset = part.get_content_charset()
                    message_content = body.decode(charset)
                    break
                elif content_type == 'text/html':
                    body = part.get_payload(decode=True)
                    charset = part.get_content_charset()
                    text_maker = html2text.HTML2Text()
                    text_maker.ignore_links = True
                    message_content = text_maker.handle(body.decode(charset))
                    break
        else:
            content_type = email_message.get_content_type()
            if content_type == 'text/plain':
                body = email_message.get_payload(decode=True)
                charset = email_message.get_content_charset()
                message_content = body.decode(charset)
            elif content_type == 'text/html':
                body = email_message.get_payload(decode=True)
                charset = email_message.get_content_charset()
                text_maker = html2text.HTML2Text()
                text_maker.ignore_links = True
                message_content = text_maker.handle(body.decode(charset))
        return message_content

    def get_email_attachments(self, email_message):
        attachments = []
        for part in email_message.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            filename = part.get_filename()
            if bool(filename):
                attachment = part.get_payload(decode=True)
                attachments.append((filename, attachment))
        return attachments