import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse

from misc.decorator import in_team_required
from .api import ProjectAPI, TemplateAPI
from misc.const import *
from misc.utils import Helper
from misc.api import UserAndTeamRoleAPI, InternalAPI
from organization.api import OrganizationAPI
from inventory.api import InventoryAPI
from .forms import ProjectInfoForm
from .models import JobTemplate, Project

project_app = 'projects'
template_app = 'templates'


# 列出所有项目
@csrf_exempt
@login_required
#@in_team_required
def projects_view(request):
    user = request.user
    try:

        is_system_admin = Helper.is_system_admin(request.user)

        status, errmsg, orgs = OrganizationAPI.all(user)
        if not status:
            return render(request, 'error.html', {ARK_ERRMSG: errmsg})

        pm_create_project = False
        for org in orgs:
            pm = InternalAPI.get_user_permissions_on_resource(
                user=request.user,
                resource_type=RS_ORGANIZATION,
                resource_id=org.id
            )
            if PM_CREATE_PROJECT in pm:
                pm_create_project = pm[PM_CREATE_PROJECT]
                if pm_create_project:
                    break
            else:
                pm_create_project = False
        if is_system_admin or pm_create_project:
            pm_create_project = True

        status, errmsg, pros = ProjectAPI.all(user)

        if not status:
            return render(request, 'error.html', {ARK_ERRMSG: errmsg})

        status_dict = {
            'pending': '正在同步',
            'running': '正在同步',
            'success': '同步成功',
            'failed': '同步失败',
            'never': '从未同步',
            'run_failed': '同步失败'
        }

        projects = list()
        for project in pros:
            if project.last_sync_job:
                pro_sync_status = project.last_sync_job.status
            else:
                pro_sync_status = 'never'
            projects.append({
                'project': project,
                'pro_sync_status': status_dict[pro_sync_status],
                'pm': InternalAPI.get_user_permissions_on_resource(
                    user=user,
                    resource_type=RS_PROJECT,
                    resource_id=project.id
                )
            })

        context = {
            'app': project_app,
            'pm_create_project': pm_create_project,
            'projects': projects
        }
        return render(request, 'project/projects.html', context)
    except Exception as e:
        return render(request, 'error.html', {ARK_ERRMSG: str(e)})


# 新建项目
@csrf_exempt
@login_required
#@in_team_required
def project_create_view(request):
    user = request.user
    try:
        if request.method == 'GET':
            status, errmsg, orgs = OrganizationAPI.all(user)
            if not status:
                return render(request, 'error.html', {ARK_ERRMSG: errmsg})
            project_info_form = ProjectInfoForm()
            org_choices = [(org.id, org.name) for org in orgs]
            project_info_form.fields['organization_id'].choices = org_choices
            context = {
                'app': project_app,
                'form': project_info_form
            }
            return render(request, 'project/project_create.html', context)

        if request.method == 'POST':
            project_info_form = ProjectInfoForm(request.POST)
            if project_info_form.is_valid():
                data = project_info_form.cleaned_data
                status, errmsg, pro = ProjectAPI.create(user=user, **data)
                if not status:
                    return render(request, 'error.html', {ARK_ERRMSG: errmsg})
                return HttpResponseRedirect(
                    reverse(
                        'project:project_detail',
                        kwargs={'project_id': pro.id})
                )
            else:
                return render(
                    request, 'error.html',
                    {ARK_ERRMSG: project_info_form.errors}
            )
    except Exception as e:
        return render(request, 'error.html', {ARK_ERRMSG: str(e)})

# 查看项目详情
@csrf_exempt
@login_required
# @in_team_required
def project_detail_view(request, project_id):
    user = request.user
    try:
        status, msg, pro = ProjectAPI.get(request.user, project_id)

        if not status:
            return HttpResponse(msg)
        project_info_form = ProjectInfoForm(
            initial={
                'name': pro.name,
                'description': '' if pro.description == None or pro.description == 'None' else pro.description,
                'url': pro.url,
                'username': pro.username,
                'branch': pro.branch,
                'revision': pro.revision
            }
        )
        project_info_form.fields['organization_id'].choices = \
            [(pro.organization.id, pro.organization.name)]
        # project_info_form.fields['organization_id'].widget.attrs.update(
        #     {
        #         'disabled': 'true'
        #     }
        # )

        pm_list =  InternalAPI.get_user_permissions_on_resource(
            user=user,
            resource_type=RS_PROJECT,
            resource_id=pro.id
        )
        if PM_UPDATE_PROJECT not in pm_list:
            pm_update_project = False
        else:
            pm_update_project = pm_list[PM_UPDATE_PROJECT]

        if not pm_update_project:
            fields = [
                'name', 'organization_id', 'description', 'scm_type',
                'url', 'username', 'branch', 'revision'
            ]
            for field in fields:
                project_info_form.fields[field].widget.attrs.update(
                    {
                        'disabled': 'true'
                    }
                )
        if pro.last_sync_job:
            pro_sync_status = pro.last_sync_job.status
        else:
            pro_sync_status = 'never'
        status_dict = {
            'pending': '正在同步',
            'running': '正在同步',
            'success': '同步成功',
            'failed': '同步失败',
            'never': '从未同步',
            'run_failed': '同步失败'
        }

        context = {
            'app': project_app,
            'form': project_info_form,
            'project': pro,
            'pro_sync_status': status_dict[pro_sync_status],
            'pm': pm_list,
            #'pm_update_project': pm_update_project
        }

        return render(request, 'project/project_detail.html', context)
    except Exception as e:
        return HttpResponse(str(e))


# 修改项目
@csrf_exempt
@login_required
#@in_team_required
def project_edit_view(request, project_id):
    try:
        if request.method == 'POST':
            project_info_form = ProjectInfoForm(request.POST)
            if project_info_form.is_valid():
                data = project_info_form.cleaned_data
                data.pop('organization_id')
                status, errmsg = ProjectAPI.update(
                    request.user, project_id, **data
                )

                if not status:
                    return render(
                        request,
                        'error.html',
                        {ARK_ERRMSG: errmsg}
                    )

                return HttpResponseRedirect(
                    reverse(
                        'project:project_detail',
                        kwargs={'project_id': project_id}
                    )
                )
            else:
                return render(
                    request,
                    'error.html',
                    {ARK_ERRMSG: project_info_form.errors}
                )
        else:
            return render(
                request,
                'error.html',
                {ARK_ERRMSG: 'method is not post'}
            )
    except Exception as e:
        return HttpResponse(str(e))

@csrf_exempt
@login_required
def project_delete_view(request, project_id):
    try:
        if request.is_ajax():
            if request.method == 'POST':
                status, errmsg = ProjectAPI.delete(
                    user=request.user,
                    project_id=project_id
                )
                if not status:
                    return JsonResponse(
                        {ARK_STATUS: False, ARK_ERRMSG: errmsg}
                    )
                return JsonResponse({ARK_STATUS: True})
    except Exception as e:
        return JsonResponse({ARK_STATUS: False, ARK_ERRMSG: str(e)})

# 同步项目
@csrf_exempt
@login_required
#@in_team_required
def project_sync_view(request, project_id):
    try:
        if request.method == 'POST':
            ajax_data = request.POST.get('data')
            data = json.loads(ajax_data)
            password = data.get('password')

            status, errmsg = ProjectAPI.sync(
                user=request.user,
                project_id=project_id,
                password=password
            )

            if not status:
                return JsonResponse(
                    {ARK_STATUS: False, ARK_ERRMSG: errmsg}
                )

            return JsonResponse(
                {ARK_STATUS: True}
            )
    except Exception as e:
        return HttpResponse(str(e))


# 列出所有用户/团队的所有角色
@csrf_exempt
@login_required
def project_roles_view(request, project_id):
    try:
        status, errmsg, pro = ProjectAPI.get(request.user, project_id)
        if not status:
            return render(request, 'error.html', {ARK_ERRMSG: errmsg})

        users = pro.users
        users_with_roles = list()

        for user in users:
            status, errmsg, roles = \
                UserAndTeamRoleAPI.get_user_roles_on_resource(
                    user=request.user,
                    target_user_id=user.id,
                    resource_type=RS_PROJECT,
                    resource_id=project_id
            )

            if status:
                users_with_roles.append([user, roles])
        teams = pro.teams
        teams_with_roles = list()

        for team in teams:
            status, errmsg, roles = \
                UserAndTeamRoleAPI.get_team_roles_on_resource(
                    user=request.user,
                    target_team_id=team.id,
                    resource_type=RS_PROJECT,
                    resource_id=project_id
                )
            if status:
                teams_with_roles.append([team, roles])
        all_users = pro.organization.users

        all_teams = pro.organization.team_set.all()

        pm_list =  InternalAPI.get_user_permissions_on_resource(
            user=request.user,
            resource_type=RS_PROJECT,
            resource_id=pro.id
        )

        context = {
            'app': project_app,
            'project': pro,
            'pm': pm_list,
            'users_with_roles': users_with_roles,
            'teams_with_roles': teams_with_roles,
            'all_users': all_users,
            'all_teams': all_teams,
            'roles': pro.roles.filter(resource_type=RS_PROJECT),
        }
        return render(request, 'project/project_roles.html', context)

    except Exception as e:
        return render(request, 'error.html', {ARK_ERRMSG: str(e)})

@csrf_exempt
@login_required
def project_roles_add_view(request, project_id):
    try:
        if request.method == 'POST':
            data = request.POST
            target = data.get('target')
            role_id = data.get('role_id')

            if target == 'user':
                user_id_list = data.getlist('user_id')

                for user_id in user_id_list:
                    status, errmsg = UserAndTeamRoleAPI.add_role_to_user(
                        request.user, int(user_id), int(role_id)
                    )

                    if not status:
                        return render(
                            request,
                            'error.html',
                            {ARK_ERRMSG: errmsg}
                        )

                return HttpResponseRedirect(
                    reverse(
                        'project:project_roles',
                        kwargs={'project_id': project_id}
                    )
                )
            elif target == 'team':
                team_id_list = data.getlist('team_id')

                for team_id in team_id_list:
                    status, errmsg = UserAndTeamRoleAPI.add_role_to_team(
                        request.user, int(team_id), int(role_id)
                    )

                    if not status:
                        return render(
                            request,
                            'error.html',
                            {ARK_ERRMSG: errmsg}
                        )

                return HttpResponseRedirect(
                    reverse(
                        'project:project_roles',
                        kwargs={'project_id': project_id}
                    )
                )
            else:
                return HttpResponse('404')
    except Exception as e:
        return render(
            request,
            'error.html',
            {ARK_ERRMSG: str(e)}
        )

# 删除用户/团队权限
@csrf_exempt
@login_required
def project_roles_remove_view(request, project_id):
    try:
        if request.is_ajax():
            if request.method == 'POST':
                ajax_data = request.POST.get('data')
                data = json.loads(ajax_data)
                target = data.get('target')
                role_id = int(data.get('role_id'))
                if target == 'user':
                    status, errmsg = UserAndTeamRoleAPI.delete_role_from_user(
                        user=request.user,
                        target_user_id=int(data.get('user_id')),
                        role_id=role_id
                    )

                    if not status:
                        return JsonResponse(
                            {ARK_STATUS: False, ARK_ERRMSG: errmsg}
                        )

                    return JsonResponse({ARK_STATUS: True})
                elif target == 'team':
                    status, errmsg = UserAndTeamRoleAPI.delete_role_from_team(
                        user=request.user,
                        target_team_id=int(data.get('team_id')),
                        role_id=role_id
                    )

                    if not status:
                        return JsonResponse(
                            {ARK_STATUS: False, ARK_ERRMSG: errmsg}
                        )

                    return JsonResponse({ARK_STATUS: True})
                else:
                    return JsonResponse(
                        {ARK_STATUS: False, ARK_ERRMSG: '既不是User也不是Team'}
                    )
            else:
                return render(
                    request,
                    'error.html',
                    {ARK_ERRMSG: 'Method is not post'}
                )
    except Exception as e:
        return JsonResponse(
            {ARK_STATUS: False, ARK_ERRMSG: str(e)}
        )
# 列出所有模板
@csrf_exempt
@login_required
def templates_view(request):
    try:
        status, msg, tems = TemplateAPI.all(request.user)

        if not status:
            return HttpResponse(msg)

        templates = []

        for i in tems:
            templates.append({
                'template': i,
                'pm': InternalAPI.get_user_permissions_on_resource(
                    request.user, RS_TEM, i.id
                ),
            })

        context = {
            'app': template_app,
            'templates': templates,
        }

        return render(request, 'project/templates.html', context)
    except Exception as e:
        return HttpResponse(str(e))


# 新建模板
@csrf_exempt
@login_required
def template_create_view(request):
    try:
        if request.method == 'GET':
            status, msg, pros = ProjectAPI.all(request.user)

            if not status:
                return HttpResponse(msg)

            status, msg, invs = InventoryAPI.all(request.user)

            if not status:
                return HttpResponse(msg)

            context = {
                'app': template_app,
                'projects': pros,
                'inventories': invs,
                'job_type_choices': JobTemplate.JOB_TYPE_CHOICES,
            }

            return render(request, 'project/template_create.html', context)
        elif request.method == 'POST':
            data = request.POST.dict()
            status, msg = TemplateAPI.create(request.user, **data)

            if not status:
                return HttpResponse(msg)

            return HttpResponseRedirect(reverse('project:templates'))
    except Exception as e:
        return HttpResponse(str(e))


# 查看模板详情
@csrf_exempt
@login_required
def template_detail_view(request, template_id):
    try:
        status, msg, tem = TemplateAPI.get(request.user, template_id)

        if not status:
            return HttpResponse(msg)

        context = {
            'app': template_app,
            'template': tem,
            'pm': InternalAPI.get_user_permissions_on_resource(
                request.user, RS_TEM, tem.id
            ),
            'job_type_choices': JobTemplate.JOB_TYPE_CHOICES,
        }

        return render(request, 'project/template_detail.html', context)
    except Exception as e:
        return HttpResponse(str(e))


# 修改模板
@csrf_exempt
@login_required
def template_edit_view(request, template_id):
    try:
        if request.method == 'POST':
            data = request.POST.dict()
            status, msg = TemplateAPI.update(
                request.user, template_id, **data
            )

            if not status:
                return HttpResponse(msg)

            return HttpResponseRedirect(
                reverse(
                    'project:template_detail',
                    kwargs={'template_id': template_id}
                )
            )
        else:
            return HttpResponse('404')
    except Exception as e:
        return HttpResponse(str(e))


# 删除模板
@csrf_exempt
@login_required
def template_delete_view(request, template_id):
    try:
        if request.method == 'POST':
            status, msg = TemplateAPI.delete(request.user, template_id)

            if not status:
                return HttpResponse(msg)

            return HttpResponseRedirect(reverse('project:templates'))
        else:
            return HttpResponse('404')
    except Exception as e:
        return HttpResponse(str(e))


# 发射模板
@csrf_exempt
@login_required
def template_launch_view(request, template_id):
    try:
        if request.method == 'POST':
            status, msg, tem = TemplateAPI.get(request.user, template_id)

            if not status:
                return HttpResponse(msg)
            
            if not tem.inventory:
                return HttpResponse('inventory unavailable')
            
            status, msg = InventoryAPI.sync(request.user, tem.inventory.id)

            if not status:
                return HttpResponse(msg)
            
            status, msg = TemplateAPI.launch(request.user, template_id)

            if not status:
                return HttpResponse(msg)

            return HttpResponseRedirect(
                reverse(
                    'project:template_detail',
                    kwargs={'template_id': template_id}
                )
            )
        else:
            return HttpResponse('404')
    except Exception as e:
        return HttpResponse(str(e))


# # 列出模板中所有任务
# @csrf_exempt
# @login_required
# @in_team_required
# def template_jobs_view(request, template_id):
#     try:
#         result = TemplateAPI.get_all_jobs({'user': request.user, 'template_id': template_id})
#
#         if not result.get(ARK_STATUS):
#             return HttpResponse(result.get(ARK_ERRMSG))
#
#         jobs = result.get('jobs')
#
#         roles_result = UserAndTeamRoleInternalAPI.get_user_and_team_roles({
#             'user': request.user,
#             'organization': request.user.organization,
#             'resource': ALL[RESOURCE],
#             'object': ALL[OBJECT],
#         })
#
#         if not roles_result.get(ARK_STATUS):
#             return HttpResponse(roles_result.get(ARK_ERRMSG))
#
#         user_roles = roles_result.get('user_roles')
#         team_roles = roles_result.get('team_roles')
#
#         context = {
#             'app': template_app,
#             'jobs': jobs,
#             'user_roles': user_roles,
#             'team_roles': team_roles,
#         }
#
#         return render(request, '????', context)
#     except Exception as e:
#         return HttpResponse(str(e))


# 列出所有用户/团队的所有角色
@csrf_exempt
@login_required
def template_roles_view(request, template_id):
    try:
        status, msg, tem = TemplateAPI.get(request.user, template_id)

        if not status:
            return HttpResponse(msg)

        users = tem.users

        users_with_roles = []

        for user in users:
            status, msg, roles = UserAndTeamRoleAPI.get_user_roles_on_resource(
                request.user, user.id, RS_TEM, template_id
            )

            if status:
                users_with_roles.append([user, roles])

        teams = tem.teams

        teams_with_roles = []

        for team in teams:
            status, msg, roles = UserAndTeamRoleAPI.get_team_roles_on_resource(
                request.user, team.id, RS_TEM, template_id
            )

            if status:
                teams_with_roles.append([team, roles])

        all_users = tem.organization.users

        context = {
            'app': template_app,
            'template': tem,
            'pm': InternalAPI.get_user_permissions_on_resource(
                request.user, RS_TEM, tem.id
            ),
            'users_with_roles': users_with_roles,
            'teams_with_roles': teams_with_roles,
            'all_users': all_users,
            'all_teams': tem.organization.team_set.all(),
            'roles': tem.roles.filter(resource_type=RS_TEM),
        }

        return render(request, 'project/template_roles.html', context)
    except Exception as e:
        return HttpResponse(str(e))


# 添加用户/团队角色
@csrf_exempt
@login_required
def template_roles_add_view(request, template_id):
    try:
        if request.method == 'POST':
            data = request.POST
            target = data.get('target')
            role_id = data.get('role_id')

            if target == 'user':
                user_id_list = data.getlist('user_id')

                for user_id in user_id_list:
                    status, msg = UserAndTeamRoleAPI.add_role_to_user(
                        request.user, int(user_id), int(role_id)
                    )

                    if not status:
                        return HttpResponse(msg)

                return HttpResponseRedirect(
                    reverse(
                        'project:template_roles',
                        kwargs={'template_id': template_id}
                    )
                )
            elif target == 'team':
                team_id_list = data.getlist('team_id')

                for team_id in team_id_list:
                    status, msg = UserAndTeamRoleAPI.add_role_to_team(
                        request.user, int(team_id), int(role_id)
                    )

                    if not status:
                        return HttpResponse(msg)

                return HttpResponseRedirect(
                    reverse(
                        'project:template_roles',
                        kwargs={'template_id': template_id}
                    )
                )
            else:
                return HttpResponse('404')
    except Exception as e:
        return HttpResponse(str(e))


# 移除用户/团队角色
@csrf_exempt
@login_required
def template_roles_remove_view(request, template_id):
    try:
        if request.method == 'POST':
            data = request.POST.dict()
            target = data.get('target')
            role_id = data.get('role_id')

            if target == 'user':
                status, msg = UserAndTeamRoleAPI.delete_role_from_user(
                    request.user, int(data.get('user_id')), int(role_id)
                )

                if not status:
                    return HttpResponse(msg)

                return HttpResponseRedirect(
                    reverse(
                        'project:template_roles',
                        kwargs={'template_id': template_id}
                    )
                )
            elif target == 'team':
                status, msg = UserAndTeamRoleAPI.delete_role_from_team(
                    request.user, int(data.get('team_id')), int(role_id)
                )

                if not status:
                    return HttpResponse(msg)

                return HttpResponseRedirect(
                    reverse(
                        'project:template_roles',
                        kwargs={'template_id': template_id}
                    )
                )
            else:
                return HttpResponse('404')
    except Exception as e:
        return HttpResponse(str(e))

