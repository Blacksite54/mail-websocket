from django.db import models

from api.users.models import User


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(blank=True, null=True)
    date_dispatch = models.DateField()
    date_receipt = models.DateField()
    description = models.CharField(blank=True, null=True)
    attachments = models.FileField(upload_to='attachments/', null=True, blank=True)
    user = models.ForeignKey(User, related_name="email_messages", on_delete=models.CASCADE)
