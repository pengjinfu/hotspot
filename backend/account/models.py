from django.contrib.auth.models import AbstractUser
from django.db import models
from django_extensions.db.models import BasicModel


class User(AbstractUser, BasicModel):
    """
    name: 用户
    desc: 用户相关信息
    is_made: False
    """
    name = models.CharField(max_length=32, blank=True, help_text='用户姓名')

    class Meta:
        db_table = 'system_user'
