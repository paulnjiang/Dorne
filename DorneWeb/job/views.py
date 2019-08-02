import json

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse

from .api import JobAPI
from .apps import JobConfig
from misc.decorator import in_team_required
from misc.api import InternalAPI
from misc.const import *


app = 'jobs'


# 列出所有任务
@csrf_exempt
@login_required
#@in_team_required
def jobs_view(request):
    try:
        status, errmsg, jobs = JobAPI.all(request.user)

        if not status:
            return render(request, 'error.html', {ARK_ERRMSG:errmsg})

        jobs_with_role = list()
        for job in jobs:
            pm = InternalAPI.get_user_permissions_on_resource(
                user=request.user,
                resource_type=RS_TEM,
                resource_id=job.job_template.id
            )
            jobs_with_role.append([job, pm])


        context = {
            'app': app,
            'jobs_with_role': jobs_with_role
        }

        return render(request, 'job/jobs.html', context)

    except Exception as e:
        return render(request, 'error.html', {ARK_ERRMSG: str(e)})


# 查看任务详情
@csrf_exempt
@login_required
#@in_team_required
def job_detail_view(request, job_id):
    try:
        status, errmsg, job = JobAPI.get(
            user=request.user,
            job_id=job_id,
        )

        if not status:
            return render(request, 'error.html', {ARK_ERRMSG:errmsg})

        pm = InternalAPI.get_user_permissions_on_resource(
            user=request.user,
            resource_type=RS_TEM,
            resource_id=job.job_template.id
        )
        if PM_DELETE_JOB in pm:
            pm_delete_job = pm[PM_DELETE_JOB]
        else:
            pm_delete_job = False

        if job.result:
            with open(job.result, 'r') as f:
                job_log = f.read()
                job_log = json.loads(job_log)
        else:
            job_log = dict()

        context = {
            'app': app,
            'job': job,
            'pm_delete_job': pm_delete_job,
            'job_log': job_log,
        }

        return render(request, 'job/job_detail.html', context)
    except Exception as e:
        return HttpResponse(str(e))

@csrf_exempt
@login_required
def job_delete_view(request):
    try:
        if request.is_ajax():
            if request.method == 'POST':
                ajax_data = request.POST.get('data')
                data = json.loads(ajax_data)
                job_id = int(data.get('job_id'))
                status, errmsg = JobAPI.delete(
                    user=request.user,
                    job_id=job_id
                )
                if not status:
                    return JsonResponse({ARK_STATUS: False, ARK_ERRMSG: errmsg})
                else:
                    return JsonResponse({ARK_STATUS: True})
    except Exception as e:
        return JsonResponse({ARK_STATUS: False, ARK_ERRMSG: str(e)})


# 远程更新任务
@csrf_exempt
def jobs_remote_update_view(request, job_id):
    try:
        if request.method == 'POST':
            data = request.POST.dict()
            if len(data) == 0:
                data = json.loads(request.body.decode('utf-8'))
            data.update({'job_id': job_id})
            status, msg = JobAPI.remote_update(data)

            if not status:
                return HttpResponse(msg)

            return HttpResponse('OK')
    except Exception as e:
        return HttpResponse(str(e))
