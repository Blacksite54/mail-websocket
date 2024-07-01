from django.db import models


class User(models.Model):
    login = models.CharField()
    password = models.CharField()