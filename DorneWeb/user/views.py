import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.urls import reverse
from django.views.decorators.csrf import  csrf_exempt

from misc.const import *
from misc.api import UserAndTeamRoleAPI
from misc.utils import Helper
from project.api import ProjectAPI, TemplateAPI
from inventory.api import InventoryAPI
from .forms import LoginUserForm, UserInfoForm
from .api import UserAPI, TeamAPI
from .api import InternalAPI

# Create your views here.

@csrf_exempt
def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('job:jobs'))
    if request.method == 'POST':
        form = LoginUserForm(request, data=request.POST)
        if form.is_valid():
            auth.login(request, form.get_user())
            return HttpResponseRedirect(
                request.GET.get('next', reverse('job:jobs'))
            )
        else:
            context = {
                'form': form,
                'errmsg': form.errors['password'][0]
            }
            return render(request, 'user/login.html', context)
    else:
        form = LoginUserForm()
        context = {
            'form': form
        }
        return render(request, 'user/login.html', context)


@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('user:login'))


@csrf_exempt
@login_required
def users_view(request):
    context = dict()
    user = request.user
    try:
        if request.method == 'GET':
            status, errmsg, users = UserAPI.all(user)
            if not status:
                return HttpResponse(errmsg)
            context['users'] = users
            return render(request, 'user/users.html', context)
    except Exception as e:
        context[ARK_ERRMSG] = str(e)
        return render(request, 'error.html', context)

@csrf_exempt
@login_required
def user_detail_view(request, target_user_id):
    '''
    用户详细信息view
    :param request:
    :param target_user_id:
    :return:
    '''
    user = request.user
    try:
        if request.method == 'GET':
            status, errmsg, target_user = UserAPI.get(
                user=user,
                target_user_id=target_user_id
            )
            if not status:
                return HttpResponse(errmsg)
            user_info_form = UserInfoForm(
                initial={
                    'name': target_user.name,
                    'chinese_name': target_user.chinese_name,
                    'email': target_user.email
                }
            )
            context = {
                'target_user': target_user,
                'user_info_form': user_info_form
            }
            return render(request, 'user/user_info_detail.html', context)
    except Exception as e:
        return HttpResponse(str(e))

@csrf_exempt
@login_required
def user_organization_view(request, target_user_id):
    '''
    用户所属组织的view
    :param request:
    :param target_user_id:
    :return:
    '''
    user = request.user
    try:
        if request.method == 'GET':
            status, errmsg, target_user = UserAPI.get(
                user=user,
                target_user_id=target_user_id
            )
            if not status:
                return HttpResponse(errmsg)

            is_system_admin = Helper.is_system_admin(target_user)

            context = {
                'is_system_admin': is_system_admin,
                'target_user': target_user
            }
            return render(request, 'user/user_info_organization.html', context)
    except Exception as e:
        return HttpResponse(str(e))

@csrf_exempt
@login_required
def user_team_view(request, target_user_id):
    '''
    用户所属团队的view
    :param request:
    :param target_user_id:
    :return:
    '''
    user = request.user
    try:
        if request.method == 'GET':
            status, errmsg, target_user = UserAPI.get(
                user=user,
                target_user_id=target_user_id
            )

            if not status:
                return HttpResponse(errmsg)

            is_system_admin = Helper.is_system_admin(target_user)

            context = {
                'target_user': target_user,
                'is_system_admin': is_system_admin
            }
            return render(request, 'user/user_info_team.html', context)
    except Exception as e:
        return HttpResponse(str(e))


@csrf_exempt
@login_required
def user_role_view(request, target_user_id):
    context = dict()
    user = request.user
    try:
        if request.method == 'GET':
            status, errmsg, result = UserAndTeamRoleAPI.get_user_role(
                user=user,
                target_user_id=target_user_id
            )
            if not status:
                context = {
                    'errmsg': errmsg
                }
                return render(request, 'error.html', context)
            status, errmsg, target_user = UserAPI.get(
                user=user,
                target_user_id=target_user_id
            )
            if not status:
                context = {
                    'errmsg': errmsg
                }
                return render(request, 'error.html', context)
            is_login_user_system_admin = Helper.is_system_admin(user)
            is_target_user_system_admin = Helper.is_system_admin(target_user)

            pm_list = InternalAPI.get_user_permissions_on_resource(
                user=user,
                resource_type=RS_SYS
            )
            if PM_ADD_SYSTEM_ROLE in pm_list:
                pm_add_system_role = pm_list[PM_ADD_SYSTEM_ROLE]
            else:
                pm_add_system_role = False

            pm_add_organization_role = False
            for org in user.organizations:
                org_pm_list = InternalAPI.get_user_permissions_on_resource(
                    user=user,
                    resource_type=RS_ORGANIZATION,
                    resource_id=org.id
                )
                if PM_ADD_ORGANIZATION_ROLE in org_pm_list:
                    pm_add_organization_role = org_pm_list[PM_ADD_ORGANIZATION_ROLE]
                else:
                    pm_add_organization_role = False

            context = {
                'user_role': result,
                'target_user': target_user,
                'is_login_user_system_admin': is_login_user_system_admin,
                'is_target_user_system_admin': is_target_user_system_admin,
                'pm_add_system_role': pm_add_system_role,
                'pm_add_organization_role': pm_add_organization_role
            }
            return render(request, 'user/user_info_role.html', context)
    except Exception as e:
        context[ARK_ERRMSG] = str(e)
        return render(request, 'error.html', context)

@csrf_exempt
@login_required
def user_role_add_view(request, target_user_id):
    user = request.user
    context = dict()
    try:
        if request.method == 'GET':
            status, errmsg, target_user = UserAPI.get(
                user=user,
                target_user_id=target_user_id
            )
            if not status:
                context = {
                    'errmsg': errmsg
                }
                return render(request, 'error.html', context)

            # 项目
            status, errmsg, projects = ProjectAPI.all(user)
            if not status:
                context = {
                    'errmsg': errmsg
                }
                return render(request, 'error.html', context)
            for org in target_user.organizations:
                projects = projects.filter(organization=org).distinct()

            # 仓库
            status, errmsg, inventories = InventoryAPI.all(user)
            if not status:
                context = {
                    'errmsg': errmsg
                }
                return render(request, 'error.html', context)
            for org in target_user.organizations:
                inventories = inventories.filter(organization=org).distinct()

            # 模板
            status, errmsg, templates = TemplateAPI.all(user)
            if not status:
                context = {
                    'errmsg': errmsg
                }
                return render(request, 'error.html', context)
            for org in target_user.organizations:
                templates = templates.filter(project__organization=org).distinct()

            # 系统
            is_system_admin = Helper.is_system_admin(user)

            context = {
                'is_system_admin': is_system_admin,
                'projects': projects,
                'inventories': inventories,
                'templates': templates,
                'target_user': target_user
            }
            return render(request, 'user/user_info_role_add.html', context)
        if request.is_ajax():
            if request.method == 'POST':
                status, errmsg, target_user = UserAPI.get(
                    user=user,
                    target_user_id=target_user_id
                )
                if not status:
                    return JsonResponse({ARK_STATUS: False, ARK_ERRMSG: errmsg})
                ajax_data = request.POST.get('data')
                data = json.loads(ajax_data)

                project_ids = data.get('project_ids')
                project_role = data.get('project_role')
                for project_id in project_ids:
                    role = InternalAPI.get_role(
                        resource_type=RS_PROJECT,
                        resource_name=project_role,
                        resource_id=int(project_id)
                    )
                    status, errmsg = UserAndTeamRoleAPI.add_role_to_user(
                        user, target_user_id, role.id
                    )
                    if not status:
                        return JsonResponse(
                            {ARK_STATUS: False, ARK_ERRMSG: errmsg}
                        )
                inventory_ids = data.get('inventory_ids')
                inventory_role = data.get('inventory_role')
                for inventory_id in inventory_ids:
                    role = InternalAPI.get_role(
                        resource_type=RS_INVENTORY,
                        resource_name=inventory_role,
                        resource_id=int(inventory_id)
                    )
                    status, errmsg = UserAndTeamRoleAPI.add_role_to_user(
                        user, target_user_id, role.id
                    )
                    if not status:
                        return JsonResponse(
                            {ARK_STATUS: False, ARK_ERRMSG: errmsg}
                        )
                template_ids = data.get('template_ids')
                template_role = data.get('template_role')
                for template_id in template_ids:
                    role = InternalAPI.get_role(
                        resource_type=RS_TEMPLATE,
                        resource_name=template_role,
                        resource_id=int(template_id)
                    )
                    status, errmsg = UserAndTeamRoleAPI.add_role_to_user(
                        user, target_user_id, role.id
                    )
                    if not status:
                        return JsonResponse(
                            {ARK_STATUS: False, ARK_ERRMSG: errmsg}
                        )

                system_admin = bool(data.get('system_admin'))
                if system_admin:
                    role = InternalAPI.get_role(
                        resource_type=RS_SYSTEM,
                        resource_name=RO_SYSTEM_ADMIN
                    )
                    status, errmsg = UserAndTeamRoleAPI.add_role_to_user(
                        user, target_user_id, role.id
                    )
                    if not status:
                        return JsonResponse(
                            {ARK_STATUS: False, ARK_ERRMSG: errmsg}
                        )
                return JsonResponse({ARK_STATUS: True})
    except Exception as e:
        context['errmsg'] = str(e)
        return render(request, 'error.html', context)


@csrf_exempt
@login_required
def user_role_remove_view(request):
    user = request.user
    try:
        if request.is_ajax():
            if request.method == 'POST':
                ajax_data = request.POST.get('data')
                data = json.loads(ajax_data)
                target_user_id = int(data.get('target_user_id'))
                role_id = int(data.get('role_id'))
                status, errmsg = UserAndTeamRoleAPI.delete_role_from_user(
                    user=user,
                    target_user_id=target_user_id,
                    role_id=role_id
                )
                if not status:
                    return JsonResponse({ARK_STATUS: False, ARK_ERRMSG: '权限不足'})
                return JsonResponse({ARK_STATUS: True})
    except Exception as e:
        return JsonResponse({ARK_STATUS: False, ARK_ERRMSG: str(e)})
