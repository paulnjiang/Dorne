from django.db import models

from misc.models import Role
from user.models import User


class Organization(models.Model):
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=64, null=True)

    # 与资源相关的角色
    roles = models.ManyToManyField(Role)

    @property
    def users(self):
        return User.objects.filter(roles__organization=self).distinct()
