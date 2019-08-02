import hashlib
import json
import os

from django.conf import settings
from django.utils import timezone

from misc.api import InternalAPI
from misc.utils import Checker
from .models import Job
from misc.const import *


class JobAPI:
    @staticmethod
    def delete(user, job_id):
        try:
            job = Job.objects.get(id=job_id)
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_TEM, job.job_template.id
            )

            if not pm_list[PM_DELETE_JOB]:
                return False, ARK_ERRMSG_CONTENT[1201]

            Job.objects.filter(id=job.id).delete()
            #os.remove(os.path.join(settings.JOB_LOG_DIR, str(job_id)))

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get(user, job_id):
        try:
            job = Job.objects.get(id=job_id)
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_TEM, job.job_template.id
            )

            if not pm_list[PM_RETRIEVE_JOB]:
                return False, ARK_ERRMSG_CONTENT[1201], None

            return True, None, job
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def all(user):
        try:
            tems = InternalAPI.get_user_resources_by_resource_type(
                user, RS_TEM
            )
            jobs = Job.objects.filter(job_template__in=tems)

            return True, None, jobs
        except Exception as e:
            return False, str(e), None

    # @staticmethod
    # def filter(user):
    #     pass

    @staticmethod
    def remote_update(data):
        """
        用于gearman worker更新任务状态
        data成员:
        {
            "job_id": 任务的id
            "status": 0 成功 1 失败
            "msg": {
                "error": "errmsg" #status = 1 也就是playbook执行失败的情况下会有这个
                # status = 0 也就是playbook执行成功时候有下面三个
                "custom_stats": {},
                "plays": {},
                "stats": {}
            }
        }
        """
        try:
            job_id = int(data.get('job_id'))

            job = Job.objects.get(id=job_id)

            # m = hashlib.md5()
            # m.update(str(job_id).encode('utf-8'))
            # m.update('mzsredota2'.encode('utf-8'))
            #
            # if check != m.hexdigest():
            #     return False, '校验错误'

            status = int(data.get('status'))
            if status == 1:
                job_status = 'run_failed'
            else:
                job_status = 'success'
                stats = data.get('msg').get('stats')
                for host, stat in stats.items():
                    failures = int(stat.get('failures'))
                    unreachable = int(stat.get('unreachable'))
                    if failures != 0 or unreachable != 0:
                        job_status = 'failed'
                        break

            job.status = job_status

            job_log_file = os.path.join(settings.JOB_LOG_DIR, str(job.id))

            with open(job_log_file, 'w') as f:
                f.write(json.dumps(data.get('msg')))

            job.result = job_log_file
            job.end_time = timezone.now()
            job.save()

            if job.name == 'update_repo':
                pro = job.project_set.all().first()
                path = os.path.join(settings.PROJECT_DIR, str(pro.id))
                yamls = []
                if os.path.isdir(path):
                    for f in os.listdir(path):
                        if not os.path.isdir(os.path.join(path, f)):
                            if os.path.splitext(f)[1] in ['.yml', '.yaml']:
                                yamls.append(f)

                pro.playbook_files = ','.join(yamls)
                pro.save()

            return True, None
        except Exception as e:
            return False, str(e)
