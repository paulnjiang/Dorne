import os

from django.db import models
from django.conf import settings

from misc.models import Role
from organization.models import Organization
from inventory.models import Inventory
from user.models import User, Team


class Project(models.Model):
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=128, null=True, blank=True)
    url = models.URLField()
    branch = models.CharField(
        max_length=32, null=True, blank=True, default='master'
    )
    revision = models.CharField(max_length=32, null=True, blank=True)
    username = models.CharField(max_length=32, blank=True)

    SCM_TYPE_CHOICES = (
        (1, 'git'),
    )
    scm_type = models.IntegerField(choices=SCM_TYPE_CHOICES)

    playbook_files = models.TextField(null=True, blank=True, default='')

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    last_sync_job = models.ForeignKey(
        'job.Job',
        null=True,
        on_delete=models.SET_NULL
    )
    # 与资源相关的角色
    roles = models.ManyToManyField(Role)

    @property
    def teams(self):
        return Team.objects.filter(owned_roles__project=self).distinct()

    @property
    def users(self):
        return User.objects.filter(roles__project=self).distinct()

    @property
    def playbooks(self):
        # path = os.path.join(settings.PROJECT_DIR, str(self.id))
        # yamls = []
        #
        # if os.path.isdir(path):
        #     for f in os.listdir(path):
        #         if not os.path.isdir(os.path.join(path, f)):
        #             if os.path.splitext(f)[1] in ['.yml', '.yaml']:
        #                 yamls.append(f)
        #
        # self.playbook_files = ','.join(yamls)

        return [i for i in self.playbook_files.split(',') if i != '']


class JobTemplate(models.Model):
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=128, null=True, blank=True)
    playbook = models.CharField(max_length=128)
    limit = models.CharField(max_length=64, null=True, blank=True)
    forks = models.IntegerField(default=5)
    verbosity = models.IntegerField(default=2)
    job_tags = models.CharField(max_length=128)
    extra_variables = models.TextField()
    allow_callback = models.BooleanField(default=False)

    JOB_TYPE_CHOICES = (
        (1, '实际执行'),
        (2, '伪执行'),
    )
    job_type = models.IntegerField(choices=JOB_TYPE_CHOICES)

    # Project被删，Template会随之删除
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    inventory = models.ForeignKey(Inventory, null=True, on_delete=models.SET_NULL)

    # 与资源相关的角色
    roles = models.ManyToManyField(Role)

    @property
    def organization(self):
        return self.project.organization

    @property
    def teams(self):
        return Team.objects.filter(owned_roles__jobtemplate=self).distinct()

    @property
    def users(self):
        return User.objects.filter(roles__jobtemplate=self).distinct()

from job.models import Job