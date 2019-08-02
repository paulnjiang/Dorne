from django.db import models
from user.models import User
from project.models import JobTemplate
# Create your models here.


class Job(models.Model):
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=128, null=True, blank=True)
    status = models.CharField(max_length=32, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    extra_variables = models.TextField(null=True)
    result = models.CharField(max_length=256, null=True, blank=True)

    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    job_template = models.ForeignKey(JobTemplate, null=True, on_delete=models.SET_NULL)

    @property
    def status_display(self):
        if self.status == 'running':
            return '正在运行'
        elif self.status == 'pending':
            return '正在提交'
        elif self.status == 'success':
            return '成功'
        elif self.status == 'failed':
            return '失败'
        elif self.status == 'run_failed':
            return '执行playbook失败'


