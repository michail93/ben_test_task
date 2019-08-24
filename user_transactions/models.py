from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    inn = models.CharField(max_length=12, verbose_name="ИНН")
    balance = models.FloatField(verbose_name="счет пользователя в рублях с точностью до копеек", default=0)
