import gear
import os
import json
import hashlib
import time

from django.db import transaction
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

from misc.api import InternalAPI
from misc.const import *
from .models import Project, JobTemplate
from organization.models import Organization
from inventory.models import Inventory
from job.models import Job


# generate an unique md5 with job id, current time and salt
def gen_job_unique(job_id):
    m = hashlib.md5()
    m.update(str(job_id).encode('utf-8'))
    t = str(time.time()).encode('utf-8')
    m.update(t)
    salt = 'mzsredota2'.encode('utf-8')
    m.update(salt)
    return m.hexdigest()


class ProjectAPI:
    @staticmethod
    def create(user, organization_id, name, url, username, scm_type,
               description=None, branch=None, revision=None):
        try:
            errmsg = list()

            if organization_id == None:
                errmsg.append('组织ID不能为空')
            if name == None or len(name) == 0:
                errmsg.append('项目名字不能为空')
            if url == None or len(url) == 0:
                errmsg.append('URL不能为空')
            if username == None or len(username) == 0:
                errmsg.append('项目的用户名不能为空')
            if scm_type == None:
                errmsg.append('源码管理类型不能为空')
            if len(errmsg) != 0:
                return False, ','.join(errmsg), None

            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_ORG, organization_id
            )

            if not pm_list[PM_CREATE_PROJECT]:
                return False, ARK_ERRMSG_CONTENT[1201]

            org = Organization.objects.get(id=organization_id)



            pro = Project(
                name=name,
                url=url,
                username=username,
                scm_type=scm_type,
                organization=org
            )
            if description is not None and len(description) != 0:
                pro.description = description
            else:
                pro.description = ''

            if branch is not None and len(branch) != 0:
                pro.branch = branch
            else:
                pro.branch = 'master'


            if revision is not None:
                pro.revision = revision

            with transaction.atomic():
                pro.save()
                InternalAPI.update_resource_and_roles_relationship(
                    RS_PRO, pro.id
                )

            return True, None, pro
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete(user, project_id):
        try:
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_PRO, project_id
            )

            if not pm_list[PM_DELETE_PROJECT]:
                return False, ARK_ERRMSG_CONTENT[1201]

            pro = Project.objects.get(id=project_id)

            if pro.jobtemplate_set.exists():
                return False, 'templates belong to project exist'

            Project.objects.filter(id=pro.id).delete()
            # os.rmdir(os.path.join(settings.PROJECT_DIR, str(project_id)))

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update(user, project_id,
               name=None, url=None, username=None, scm_type=None,
               description=None, branch=None, revision=None):
        try:
            errmsg = list()
            if project_id == None:
                errmsg.append('项目ID不能为空')
            if len(errmsg) != 0:
                return False, ','.join(errmsg), None

            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_PRO, project_id
            )

            if not pm_list[PM_UPDATE_PROJECT]:
                return False, ARK_ERRMSG_CONTENT[1201]

            pro = Project.objects.get(id=project_id)

            if name is not None:
                pro.name = name

            if description is not None and len(description) != 0:
                pro.description = description
            else:
                pro.description = ''

            if url is not None and len(url):
                pro.url = url

            if branch is not None and len(branch):
                pro.branch = branch

            if revision is not None and len(revision):
                pro.revision = revision

            if username is not None and len(username):
                pro.username = username

            if scm_type is not None:
                pro.scm_type = scm_type

            pro.save()

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get(user, project_id):
        try:
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_PRO, project_id
            )

            if not pm_list[PM_RETRIEVE_PROJECT]:
                return False, ARK_ERRMSG_CONTENT[1201], None

            pro = Project.objects.get(id=project_id)

            return True, None, pro
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def all(user):
        try:
            pros = InternalAPI.get_user_resources_by_resource_type(
                user, RS_PRO
            )

            return True, None, pros
        except Exception as e:
            return False, str(e), None

    # @staticmethod
    # def filter(user):
    #     pass

    @staticmethod
    def sync(user, project_id, password):
        try:
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_PRO, project_id
            )

            if not pm_list[PM_SYNC_PROJECT]:
                return False, ARK_ERRMSG_CONTENT[1201]

            pro = Project.objects.get(id=project_id)

            # 先在数据库里创建一条job记录，再向gearman发一个任务
            job = Job.objects.create(
                name='update_repo',
                description='sync git',
                status='pending',
                start_time=timezone.now(),
                end_time=timezone.now(),
                result='',
                user=user,
                job_template=None,
            )
            client = gear.Client()
            client.addServer(settings.GEARMAN_SERVER, 4730)
            client.waitForServer()
            job.status = 'running'
            job.save()
            pro.last_sync_job = job
            pro.save()
            job_data = {
                'callback_url': settings.CALLBACK_HOST + reverse('job:remote_update', kwargs={'job_id': job.id}),
                'inventory_file': settings.GIT_SYNC_INVENTORY,
                'playbook_file': settings.GIT_SYNC_PLAYBOOK,
                'args': {
                    'extra_variables': {
                        'gituser': pro.username,
                        'gitpassword': password,
                        'giturl': pro.url.replace('https://', ''),
                        'gitbranch': pro.branch,
                    },
                },
            }
            gearman_job = gear.Job(
                'run_playbook',
                bytes(json.dumps(job_data), 'utf-8')
            )
            client.submitJob(gearman_job, background=True)

            return True, None
        except Exception as e:
            return False, str(e)

    # @staticmethod
    # def duplicate(user):
    #     pass


class TemplateAPI:
    @staticmethod
    def create(user, project_id, inventory_id, name,
               playbook, job_tags, job_type,
               description=None, limit=None, forks=None, verbosity=None,
               extra_variables=None, allow_callback=None):
        try:
            # everybody can create template
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_PRO, project_id
            )

            if not pm_list[PM_USE_PROJECT_IN_JOB]:
                return False, ARK_ERRMSG_CONTENT[1201]

            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_INV, inventory_id
            )

            if not pm_list[PM_USE_INVENTORY_IN_JOB]:
                return False, ARK_ERRMSG_CONTENT[1201]

            pro = Project.objects.get(id=project_id)
            inv = Inventory.objects.get(id=inventory_id)

            if pro.organization != inv.organization:
                return False, 'cannot create template across organizations'

            tem = JobTemplate(
                name=name,
                playbook=playbook,
                job_tags=job_tags,
                job_type=job_type,
                project=pro,
                inventory=inv
            )

            if description is not None:
                tem.description = description

            if limit is not None:
                tem.limit = limit

            if forks is not None:
                tem.forks = forks

            if verbosity is not None:
                tem.verbosity = verbosity

            if extra_variables is not None:
                if extra_variables != '':
                    try:
                        tmp_vars = json.loads(extra_variables)

                        if not isinstance(tmp_vars, dict):
                            return False, '变量必须为对象形式的数据'
                    except json.decoder.JSONDecodeError:
                        return False, '变量必须为JSON格式的数据'
                
                tem.extra_variables = extra_variables

            if allow_callback is not None:
                tem.allow_callback = allow_callback

            with transaction.atomic():
                tem.save()
                InternalAPI.update_resource_and_roles_relationship(
                    RS_TEM, tem.id
                )

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete(user, template_id):
        try:
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_TEM, template_id
            )

            if not pm_list[PM_DELETE_TEMPLATE]:
                return False, ARK_ERRMSG_CONTENT[1201]

            tem = JobTemplate.objects.get(id=template_id)

            if tem.job_set.exists():
                return False, 'jobs belong to template exist'

            JobTemplate.objects.filter(id=tem.id).delete()

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update(user, template_id,
               name=None, description=None, playbook=None, limit=None,
               forks=None, verbosity=None, job_tags=None, extra_variables=None,
               allow_callback=None, job_type=None):
        try:
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_TEM, template_id
            )

            if not pm_list[PM_UPDATE_TEMPLATE]:
                return False, ARK_ERRMSG_CONTENT[1201]

            tem = JobTemplate.objects.get(id=template_id)

            if name is not None:
                tem.name = name

            if description is not None:
                tem.description = description

            if playbook is not None:
                tem.playbook = playbook

            if limit is not None:
                tem.limit = limit

            if forks is not None:
                tem.forks = forks

            if verbosity is not None:
                tem.verbosity = verbosity

            if job_tags is not None:
                tem.job_tags = job_tags

            if extra_variables is not None:
                if extra_variables != '':
                    try:
                        tmp_vars = json.loads(extra_variables)

                        if not isinstance(tmp_vars, dict):
                            return False, '变量必须为对象形式的数据'
                    except json.decoder.JSONDecodeError:
                        return False, '变量必须为JSON格式的数据'
                
                tem.extra_variables = extra_variables

            if allow_callback is not None:
                tem.allow_callback = allow_callback

            if job_type is not None:
                tem.job_type = job_type

            tem.save()

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get(user, template_id):
        try:
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_TEM, template_id
            )

            if not pm_list[PM_RETRIEVE_TEMPLATE]:
                return False, ARK_ERRMSG_CONTENT[1201], None

            tem = JobTemplate.objects.get(id=template_id)

            return True, None, tem
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def all(user):
        try:
            tems = InternalAPI.get_user_resources_by_resource_type(
                user, RS_TEM
            )

            return True, None, tems
        except Exception as e:
            return False, str(e), None

    # @staticmethod
    # def filter(user):
    #     pass

    @staticmethod
    def launch(user, template_id):
        try:
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_TEM, template_id
            )

            if not pm_list[PM_LAUNCH_TEMPLATE]:
                return False, ARK_ERRMSG_CONTENT[1201]

            tem = JobTemplate.objects.get(id=template_id)

            # 先在数据库里创建一条job记录，再向gearman发一个任务
            job = Job.objects.create(
                name=tem.name,
                description='play',
                status='pending',
                start_time=timezone.now(),
                #end_time=timezone.now(),
                extra_variables=tem.extra_variables,
                result='',
                user=user,
                job_template=tem,
            )
            client = gear.Client()
            client.addServer(settings.GEARMAN_SERVER, 4730)
            client.waitForServer()
            job.status = 'running'
            job.save()
            
            inv = tem.inventory
            inv_file = os.path.join(settings.INVENTORY_DIR, str(inv.id) + '_' + str(job.id) + '.yaml')

            with open(inv_file, 'w') as f:
                f.write(inv.gen_content())

            job_data = {
                'callback_url': settings.CALLBACK_HOST + reverse('job:remote_update', kwargs={'job_id': job.id}),
                'inventory_file': inv_file,
                'playbook_file': os.path.join(settings.PROJECT_DIR, str(tem.project.id), tem.playbook),
                'args': {
                    'extra_variables': json.loads(tem.extra_variables),
                    'limit': tem.limit,
                    'forks': str(tem.forks),
                    'job_tags': tem.job_tags if tem.job_tags != '' else None,
                    'verbosity': '2',
                    "check": False,
                },
            }
            gearman_job = gear.Job(
                'run_playbook',
                bytes(json.dumps(job_data), 'utf-8')
            )
            client.submitJob(gearman_job, background=True)

            return True, None
        except Exception as e:
            return False, str(e)

    # @staticmethod
    # def get_all_jobs(user, template_id):
    #     try:
    #         pm_list = InternalAPI.get_user_permissions_on_resource(
    #             user, RS_TEM, template_id
    #         )
    #
    #         if not pm_list[PM_RETRIEVE_JOB]:
    #             return False, ARK_ERRMSG_CONTENT[1201], None
    #
    #         tem = JobTemplate.objects.get(id=template_id)
    #
    #         jobs = tem.job_set.all()
    #
    #         return True, None, jobs
    #     except Exception as e:
    #         return False, str(e), None

    # @staticmethod
    # def duplicate(user):
    #     pass
