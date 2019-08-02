from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from misc.models import Role


class Team(models.Model):
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=64, null=True, blank=True)

    organization = models.ForeignKey(
        'organization.Organization', on_delete=models.CASCADE
    )

    # 团队相关的角色
    roles = models.ManyToManyField(Role)

    # 团队拥有的角色
    owned_roles = models.ManyToManyField(Role, related_name='owner_teams')

    @property
    def inventories(self):
        return Inventory.objects.filter(roles__owner_teams=self).distinct()

    @property
    def projects(self):
        return Project.objects.filter(roles__owner_teams=self).distinct()

    @property
    def templates(self):
        return JobTemplate.objects.filter(roles__owner_teams=self).distinct()

    @property
    def users(self):
        return User.objects.filter(roles__team=self).distinct()


class UserManager(BaseUserManager):
    def create_user(self, email, chinese_name, password=None):
        if not chinese_name:
            raise ValueError('用户中文名字必须录入')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=self.email_to_username(email),
            chinese_name=chinese_name
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, chinese_name, password):
        user = self.create_user(
            email=email,
            chinese_name=chinese_name,
            password=password
        )
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def email_to_username(self, email):
        username = email.split('@')[0].replace('.', '_')
        return username


class User(AbstractBaseUser):
    email = models.EmailField(
        max_length=64,
        unique=True
    )
    name = models.CharField(max_length=32)
    chinese_name = models.CharField(max_length=32)

    # 用户的Access ID
    access_user_id = models.CharField(max_length=64, db_index=True, null=True, blank=True)

    phone = models.CharField(max_length=11, null=True, blank=True)

    # 用户拥有的角色
    roles = models.ManyToManyField(Role)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['chinese_name']

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'chinese_name': self.chinese_name,
            'email': self.email,
            'phone': self.phone,
        }

    @property
    def organizations(self):
        return Organization.objects.filter(roles__user=self).distinct()

    @property
    def teams(self):
        return Team.objects.filter(roles__user=self).distinct()

    @property
    def inventories(self):
        return Inventory.objects.filter(roles__user=self).distinct()

    @property
    def projects(self):
        return Project.objects.filter(roles__user=self).distinct()

    @property
    def templates(self):
        return JobTemplate.objects.filter(roles__user=self).distinct()


from organization.models import Organization
from inventory.models import Inventory
from project.models import Project, JobTemplate
