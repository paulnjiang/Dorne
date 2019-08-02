import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse

from .api import OrganizationAPI
from .models import Organization
from user.api import UserAPI, TeamAPI
from user.models import User, Team
from project.api import ProjectAPI, TemplateAPI
from inventory.api import InventoryAPI
from user.forms import TeamInfoForm
from .forms import OrganizationInfoForm
from misc.api import InternalAPI, UserAndTeamRoleAPI
from misc.const import *
from misc.models import Role
from misc.utils import Helper

app = 'organizations'

# 列出所有组织
@csrf_exempt
@login_required
def organizations_view(request):

    user = request.user
    try:
        status, errmsg, orgs = OrganizationAPI.all(user=user)
        if not status:
            return render(request, 'error.html', {ARK_ERRMSG: errmsg})
        pm_list = InternalAPI.get_user_permissions_on_resource(
            user=user,
            resource_type=RS_SYS
        )
        if PM_CREATE_ORGANIZATION not in pm_list:
            pm_create_org = False
        else:
            pm_create_org = pm_list[PM_CREATE_ORGANIZATION]

        if PM_DELETE_ORGANIZATION not in pm_list:
            pm_delete_org = False
        else:
            pm_delete_org = pm_list[PM_DELETE_ORGANIZATION]
        context = {
            'app': app,
            'pm_create_org': pm_create_org,
            'pm_delete_org': pm_delete_org,
            'organizations': orgs,
        }
        return render(request, 'organization/organization_list.html', context)
    except Exception as e:
        return render(request, 'error.html', {ARK_ERRMSG: str(e)})

@csrf_exempt
@login_required
def organization_delete_view(request, organization_id):
    try:
        if request.is_ajax():
            if request.method == 'POST':
                status, errmsg = OrganizationAPI.delete(
                    user=request.user,
                    organization_id=organization_id
                )
                if not status:
                    return JsonResponse(
                        {ARK_STATUS: False, ARK_ERRMSG: errmsg}
                    )
                return JsonResponse(
                    {ARK_STATUS: True}
                )
    except Exception as e:
        return JsonResponse(
            {ARK_STATUS: False, ARK_ERRMSG: str(e)}
        )


# 新建组织
@csrf_exempt
@login_required
def organizations_create_view(request):
    user = request.user
    try:
        if request.method == 'GET':
            org_info_form = OrganizationInfoForm()

            context = {
                'app': app,
                'org_info_form': org_info_form,
            }
            return render(
                request,
                'organization/organization_create.html',
                context
            )
        elif request.method == 'POST':
            org_info_form = OrganizationInfoForm(request.POST)
            if org_info_form.is_valid():
                org_info_form = org_info_form.cleaned_data
                org_info_form['user'] = request.user
                status, errmsg, org_id = OrganizationAPI.create(
                    user=user,
                    name=org_info_form.get('name'),
                    description=org_info_form.get('description')
                )
                if not status:
                    return HttpResponse(errmsg)
                return HttpResponseRedirect(
                    reverse(
                        'organization:organization_detail',
                        kwargs={'organization_id': org_id}
                    )
                )
            else:
                return HttpResponse(org_info_form.errors)
    except Exception as e:
        return HttpResponse(str(e))


# 组织信息
@csrf_exempt
@login_required
def organization_detail_view(request, organization_id):
    user = request.user
    try:
        if request.method == 'GET':
            status, errmsg, organization = OrganizationAPI.get(
                user=user,
                organization_id=organization_id
            )
            if not status:
                return HttpResponse(errmsg)
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_ORG, organization_id
            )
            if PM_UPDATE_ORGANIZATION not in pm_list:
                pm_update_org = False
            else:
                pm_update_org = pm_list[PM_UPDATE_ORGANIZATION]
            # 组织信息
            org_info_form = OrganizationInfoForm(initial={
                'name': organization.name,
                'description': organization.description
            })
            if not pm_update_org:
                org_info_form.fields['name'].widget.attrs.update({
                    'disabled': 'true'
                })
                org_info_form.fields['description'].widget.attrs.update({
                    'disabled': 'true'
                })
            context = {
                'app': app,
                'org_info_form': org_info_form,
                'organization': organization,
                'pm_update_org': pm_update_org,
                'organization_id': organization_id,

            }
            return render(
                request,
                'organization/organization_info_detail.html',
                context
            )
        elif request.method == 'POST':
            data = request.POST
            org_info_form = OrganizationInfoForm(data)
            if org_info_form.is_valid():
                data = org_info_form.cleaned_data
                name = data.get('name')
                description = data.get('description')
                status, errmsg = OrganizationAPI.update(
                    user=user,
                    organization_id=organization_id,
                    name=name,
                    description=description
                )
                if not status:
                    return HttpResponse(errmsg)
                return HttpResponseRedirect(
                    reverse(
                        'organization:organization_detail',
                        kwargs={
                            'organization_id': organization_id
                        })
                )
            else:
                return HttpResponse(org_info_form.errors)
    except Exception as e:
        return HttpResponse(str(e))

@csrf_exempt
@login_required
def organization_user_view(request, organization_id):
    '''
    组织内用户view
    :param request:
    :param organization_id:
    :return:
    '''
    user = request.user
    try:
        if request.method == 'GET':
            status, errmsg, organization = OrganizationAPI.get(
                user=user,
                organization_id=organization_id
            )
            if not status:
                return render(request, 'error.html', {'errmsg': errmsg})
            # 获取组织内该用户有查看权限的用户
            status, errmsg, users = OrganizationAPI.get_all_users(
                user=user,
                organization_id=organization_id
            )
            if not status:
                return render(request, 'error.html', {'errmsg':errmsg})
            # if not isinstance(users, list):
            #     users = users.filter(roles__organization=organization)
            #     users = users.distinct()
            # 拥有组织管理员以及以上权限的人
            users_with_oa_role = list()
            # 拥有组织成员权限的人
            users_with_om_role = list()
            for user_item in users:
                org_role = InternalAPI.get_user_roles_on_resource(
                    user=user_item,
                    resource_type=RS_ORG,
                    resource_id=organization_id
                )
                if org_role.filter(name__in=[RO_SYS_ADMIN, RO_ORG_ADMIN])\
                        .exists():
                    users_with_oa_role.append([user_item, org_role])
                else:
                    users_with_om_role.append([user_item,org_role])
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user=user,
                resource_type=RS_ORG,
                resource_id=organization_id
            )
            if PM_ADD_ORGANIZATION_ROLE not in pm_list:
                pm_add_organization_role = False
            else:
                pm_add_organization_role = pm_list[PM_ADD_ORGANIZATION_ROLE]
            if PM_REMOVE_ORGANIZATION_ROLE not in pm_list:
                pm_remove_organization_role = False
            else:
                pm_remove_organization_role = pm_list[PM_REMOVE_ORGANIZATION_ROLE]
            system_admin = Helper.is_system_admin(user)
            context = {
                'app': app,
                'organization': organization,
                'organization_id': organization_id,
                'users_with_oa_role': users_with_oa_role,
                'users_with_om_role': users_with_om_role,
                'pm_add_organization_role': pm_add_organization_role,
                'pm_remove_organization_role': pm_remove_organization_role,
                'system_admin': system_admin,
            }
            return render(
                request,
                'organization/organization_info_user.html',
                context
            )
    except Exception as e:
        return HttpResponse(str(e))

@csrf_exempt
@login_required
def organization_user_add_view(request, organization_id):
    user = request.user
    try:
        if request.method == 'GET':
            status, errmsg, organization = OrganizationAPI.get(
                user=user,
                organization_id=organization_id
            )
            if not status:
                return HttpResponse(errmsg)
            org_users = organization.users
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user=user,
                resource_type=RS_ORG,
                resource_id=organization.id
            )
            if PM_ADD_ORGANIZATION_ROLE not in pm_list:
                pm_add_organization_role = False
            else:
                pm_add_organization_role = pm_list[PM_ADD_ORGANIZATION_ROLE]

            # 列出没有组织的普通用户
            users_not_has_org = None
            all_orgs = Organization.objects.all()
            if pm_add_organization_role:
                users_not_has_org = User.objects.\
                    exclude(roles__organization__in=all_orgs).\
                    exclude(roles__name=RO_SYS_ADMIN).all().distinct()
            else:
                return HttpResponse(ARK_ERRMSG_CONTENT[1201])

            context = {
                'app': app,
                'organization': organization,
                'organization_id': organization_id,
                'org_users': org_users,
                'users_not_has_org': users_not_has_org
            }
            return render(
                request,
                'organization/organization_info_user_add.html',
                context
            )
        else:
            if request.is_ajax() and request.method == 'POST':
                ajax_data = request.POST.get('data')
                data = json.loads(ajax_data)
                user_ids = data.get('user_ids')
                org_role = int(data.get('org_role'))
                for user_id in user_ids:
                    status, errmsg, = UserAndTeamRoleAPI.add_role_to_user(
                        user=user,
                        target_user_id=int(user_id),
                        role_id=org_role
                    )
                    if not status:
                        return JsonResponse({
                            ARK_STATUS: False,
                            ARK_ERRMSG: errmsg
                        })
                else:
                    return JsonResponse({
                        ARK_STATUS: True
                    })
    except Exception as e:
        return HttpResponse(str(e))

@csrf_exempt
@login_required
def organization_user_role_remove_view(request):
    try:
        if request.is_ajax() and request.method == 'POST':
            user = request.user
            ajax_data = request.POST.get('data')
            data = json.loads(ajax_data)
            target_user_id = int(data.get('user_id'))
            role_id = int(data.get('role_id'))
            status, errmsg = UserAndTeamRoleAPI.delete_role_from_user(
                user=user,
                target_user_id=target_user_id,
                role_id=role_id
            )
            if not status:
                return JsonResponse({ARK_STATUS: False, ARK_ERRMSG: errmsg})
            return JsonResponse({ARK_STATUS: True})
    except Exception as e:
        return JsonResponse({ARK_STATUS: False, ARK_ERRMSG: str(e)})



@csrf_exempt
@login_required
def organization_team_view(request, organization_id):
    '''
    组织内团队view
    :param request:
    :param organization_id:
    :return:
    '''
    user = request.user
    try:
        if request.method == 'GET':
            status, errmsg, organization = OrganizationAPI.get(
                user=user,
                organization_id=organization_id
            )
            if not status:
                return HttpResponse(errmsg)
            # 获取组织内该登录用户拥有查看权限的团队
            #teams = organization.team_set.all()
            status, errmsg, teams = OrganizationAPI.get_teams_user_can_retrieve(
                user=user,
                organization_id=organization_id
            )
            if not status:
                return HttpResponse(errmsg)
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user=user,
                resource_type=RS_ORG,
                resource_id=organization_id
            )
            if PM_CREATE_TEAM in pm_list:
                pm_create_team = pm_list[PM_CREATE_TEAM]
            else:
                pm_create_team = False

            context = {
                'app': app,
                'organization': organization,
                'pm_create_team': pm_create_team,
                'organization_id': organization_id,
                'teams': teams
            }
            return render(
                request,
                'organization/organization_info_team.html',
                context
            )
    except Exception as e:
        return HttpResponse(str(e))

#新建团队
@csrf_exempt
@login_required
def organization_team_create_view(request, organization_id):
    user = request.user
    try:
        if request.method == 'POST':
            team_info_form = TeamInfoForm(request.POST)
            if team_info_form.is_valid():
                team_info_form = team_info_form.cleaned_data
                name = team_info_form.get('name')
                description = team_info_form.get('description')
                status, errmsg = TeamAPI.create(
                    user=user,
                    organization_id=organization_id,
                    name=name,
                    description=description
                )
                if not status:
                    return HttpResponse(errmsg)
                return HttpResponseRedirect(
                    reverse(
                        'organization:organization_team',
                        kwargs={'organization_id': organization_id}
                    )
                )
            else:
                return HttpResponse(team_info_form.errors)
        elif request.method == 'GET':
            team_info_form = TeamInfoForm()
            status, errmsg, org = OrganizationAPI.get(
                user=user,
                organization_id=organization_id
            )
            if not status:
                return HttpResponse(errmsg)
            org_array = [(org.id, org.name)]
            org_choices = org_array
            team_info_form.fields['organization'].choices = org_choices
            context = {
                'app': app,
                'organization': org,
                'organization_id': organization_id,
                'team_info_form': team_info_form,
            }
            return render(
                request,
                'organization/organization_info_team_create.html',
                context
            )
    except Exception as e:
        return HttpResponse(str(e))


@csrf_exempt
@login_required
def team_info_detail_view(request, team_id):
    context = dict()
    user = request.user
    try:
        if request.method == 'GET':
            status, errmsg, team = TeamAPI.get(user=user, team_id=team_id)
            if not status:
                return HttpResponse(errmsg)
            choices = [(team.organization.id, team.organization.name)]

            team_info_form = TeamInfoForm(initial={
                'name': team.name,
                'description': team.description
            })
            team_info_form.fields['organization'].choices = choices

            pm_list = InternalAPI.get_user_permissions_on_resource(
                user=user,
                resource_type=RS_TEAM,
                resource_id=team.id
            )
            if PM_UPDATE_TEAM not in pm_list:
                pm_update_team = False
            else:
                pm_update_team = pm_list[PM_UPDATE_TEAM]
            if not pm_update_team:
                fields = ['name', 'description', 'organization']
                for field in fields:
                    team_info_form.fields[field].widget.attrs.update({
                        'disabled': 'true'
                    })
            context = {
                'app': app,
                'team': team,
                'team_info_form': team_info_form,
                'pm_update_team': pm_update_team
            }
            return render(request, 'organization/team_info_detail.html', context)
        elif request.method == 'POST':
            team_info_form = TeamInfoForm(request.POST)
            if team_info_form.is_valid():
                team_info_form = team_info_form.cleaned_data
                name = team_info_form.get('name')
                description = team_info_form.get('description')
                status, errmsg = TeamAPI.update(
                    user=user,
                    team_id=team_id,
                    name=name,
                    description=description
                )
                if not status:
                    return HttpResponse(errmsg)
                else:
                    return HttpResponseRedirect(
                        reverse(
                            'organization:team_info_detail',
                            kwargs={'team_id': team_id}
                        )
                    )
            else:
                context[ARK_ERRMSG] = team_info_form.errors
                return render(request, 'error.html', context)
    except Exception as e:
        context[ARK_ERRMSG] = str(e)
        return render(request, 'error.html', context)


@csrf_exempt
@login_required
def team_info_user_view(request, team_id):
    '''
    团队内用户的view
    :param request:
    :param team_id:
    :return:
    '''
    user = request.user
    try:
        if request.method == 'GET':
            status, errmsg, team = TeamAPI.get(user=user, team_id=team_id)
            if not status:
                return HttpResponse(errmsg)

            status, errmsg, team_users = TeamAPI.get_team_users(user, team_id)
            if not status:
                return HttpResponse(errmsg)

            pm_list = InternalAPI.get_user_permissions_on_resource(
                user=user,
                resource_type=RS_TEAM,
                resource_id=team.id
            )
            if PM_ADD_TEAM_ROLE not in pm_list:
                pm_add_team_role = False
            else:
                pm_add_team_role = pm_list[PM_ADD_TEAM_ROLE]

            # 不能添加团队角色 相当于不能给团队添加用户 也就是该user是个普通用户
            if not pm_add_team_role:
                team_users = team_users.exclude(
                    roles__name__in=[RO_SYS_ADMIN, RO_ORG_ADMIN]
                )
            team_users_with_role = list()

            for user_item in team_users:
                user_role_on_team = InternalAPI.get_user_roles_on_resource(
                    user=user_item,
                    resource_type=RS_TEAM,
                    resource_id=team_id
                )
                team_users_with_role.append([user_item, user_role_on_team])

            system_admin = Helper.is_system_admin(user)
            context = {
                'app': app,
                'team': team,
                'pm_add_team_role': pm_add_team_role,
                'team_users': team_users_with_role,
                'system_admin': system_admin
            }
            return render(request, 'organization/team_info_user.html', context)
    except Exception as e:
        return HttpResponse(str(e))

@csrf_exempt
@login_required
def team_info_role_view(request, team_id):
    context = dict()
    user = request.user
    try:
        if request.method == 'GET':
            status, errmsg, result = UserAndTeamRoleAPI.get_team_role(
                user=user,
                team_id=team_id
            )

            if not status:
                context = {
                    'errmsg': errmsg
                }
                return render(request, 'error.html', context)

            status, errmsg, team = TeamAPI.get(
                user=user,
                team_id=team_id
            )
            if not status:
                context = {
                    'errmsg': errmsg
                }
                return render(request, 'error.html', context)
            # is_system_admin = Helper.is_system_admin(target_user)

            pm_list = InternalAPI.get_user_permissions_on_resource(
                user=user,
                resource_type=RS_SYS
            )
            if PM_ADD_SYSTEM_ROLE in pm_list:
                pm_add_system_role = pm_list[PM_ADD_SYSTEM_ROLE]
            else:
                pm_add_system_role = False

            pm_add_team_role = False
            team_pm_list = InternalAPI.get_user_permissions_on_resource(
                user=user,
                resource_type=RS_TEAM,
                resource_id=team_id
            )
            if PM_ADD_TEAM_ROLE in team_pm_list:
                pm_add_team_role = team_pm_list[PM_ADD_TEAM_ROLE]
            context = {
                'app': app,
                'team_role': result,
                'team': team,
                'pm_add_system_role': pm_add_system_role,
                'pm_add_team_role': pm_add_team_role
            }
            return render(request, 'organization/team_info_role.html', context)
    except Exception as e:
        context[ARK_ERRMSG] = str(e)
        return render(request, 'error.html', context)

@csrf_exempt
@login_required
def team_info_role_add_view(request, team_id):
    user = request.user
    context =dict()
    try:
        if request.method == 'GET':
            status, errmsg, team = TeamAPI.get(
                user=user,
                team_id=team_id
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
            projects = projects.filter(organization=team.organization).distinct()

            # 仓库
            status, errmsg, inventories = InventoryAPI.all(user)
            if not status:
                context = {
                    'errmsg': errmsg
                }
                return render(request, 'error.html', context)

            inventories = inventories.filter(organization=team.organization).\
                distinct()

            # 模板
            status, errmsg, templates = TemplateAPI.all(user)
            if not status:
                context = {
                    'errmsg': errmsg
                }
                return render(request, 'error.html', context)
            templates = templates.filter(project__organization=team.organization).\
                distinct()

            context = {
                'app': app,
                'projects': projects,
                'inventories': inventories,
                'templates': templates,
                'team': team
            }
            return render(request, 'organization/team_info_role_add.html', context)
        if request.is_ajax():
            if request.method == 'POST':
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
                    status, errmsg = UserAndTeamRoleAPI.add_role_to_team(
                        user, team_id, role.id
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
                    status, errmsg = UserAndTeamRoleAPI.add_role_to_team(
                        user, team_id, role.id
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
                    status, errmsg = UserAndTeamRoleAPI.add_role_to_team(
                        user, team_id, role.id
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
def team_info_role_remove_view(request):
    user = request.user
    try:
        if request.is_ajax():
            if request.method == 'POST':
                ajax_data = request.POST.get('data')
                data = json.loads(ajax_data)
                target_team_id = int(data.get('target_team_id'))
                role_id = int(data.get('role_id'))
                status, errmsg = UserAndTeamRoleAPI.delete_role_from_team(
                    user=user,
                    target_team_id=target_team_id,
                    role_id=role_id
                )
                if not status:
                    return JsonResponse(
                        {ARK_STATUS: False, ARK_ERRMSG: '权限不足'}
                    )
                return JsonResponse({ARK_STATUS: True})
    except Exception as e:
        return JsonResponse({ARK_STATUS: False, ARK_ERRMSG: str(e)})



@csrf_exempt
@login_required
def team_info_user_add_view(request, team_id):
    '''
    向团队内添加用户的view
    :param request:
    :param team_id:
    :return:
    '''
    user = request.user
    try:
        if request.method == 'GET':
            status, errmsg, team = TeamAPI.get(
                user=user,
                team_id=team_id
            )
            if not status:
                return HttpResponse(errmsg)
            org_users = team.organization.users
            # 列出该组织内没有团队的用户
            all_teams = Team.objects.all()
            org_users_not_has_team = org_users.exclude(
                roles__team__in=all_teams).all()
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user=user,
                resource_type=RS_TEAM,
                resource_id=team.id
            )
            if PM_ADD_TEAM_ROLE not in pm_list:
                pm_add_team_role = False
            else:
                pm_add_team_role = pm_list[PM_ADD_TEAM_ROLE]

            if not pm_add_team_role:
                return HttpResponse(ARK_ERRMSG_CONTENT[1201])

            context = {
                'app': app,
                'organization': team.organization,
                'organization_id': team.organization.id,
                'team': team,
                'org_users_not_has_team': org_users_not_has_team,
            }
            return render(
                request,
                'organization/team_info_user_add.html',
                context
            )
        else:
            if request.is_ajax() and request.method == 'POST':
                ajax_data = request.POST.get('data')
                data = json.loads(ajax_data)
                user_ids = data.get('user_ids')
                team_role = int(data.get('team_role'))
                for user_id in user_ids:
                    status, errmsg = UserAndTeamRoleAPI.add_role_to_user(
                        user=user,
                        target_user_id=int(user_id),
                        role_id=team_role
                    )
                    if not status:
                        return JsonResponse({
                            ARK_STATUS: False,
                            ARK_ERRMSG: errmsg
                        })
                else:
                    return JsonResponse({
                        ARK_STATUS: True
                    })
    except Exception as e:
        return HttpResponse(str(e))

@csrf_exempt
@login_required
def team_delete_view(request, team_id):
    try:
        if request.is_ajax():
            if request.method == 'POST':
                status, errmsg = TeamAPI.delete(
                    user=request.user,
                    team_id=team_id
                )
                if not status:
                    return JsonResponse(
                        {ARK_STATUS: False, ARK_ERRMSG: errmsg}
                    )
                return JsonResponse(
                    {ARK_STATUS: True}
                )
    except Exception as e:
        return JsonResponse(
            {ARK_STATUS: False, ARK_ERRMSG: str(e)}
        )


@csrf_exempt
@login_required
def organization_inventory_view(request, organization_id):
    '''
    组织内仓库view
    :param request:
    :param organization_id:
    :return:
    '''
    user = request.user
    try:
        if request.method == 'GET':
            status, errmsg, organization = OrganizationAPI.get(
                user=user,
                organization_id=organization_id
            )
            if not status:
                return HttpResponse(errmsg)
            # 组织内仓库
            status, errmsg, inventories = InventoryAPI.all(user=user)
            if not status:
                return HttpResponse(errmsg)
            inventories = inventories.filter(organization=organization).\
                distinct()
            context = {
                'app': app,
                'organization': organization,
                'organization_id': organization_id,
                'inventories': inventories
            }
            return render(
                request,
                'organization/organization_info_inventory.html',
                context
            )
    except Exception as e:
        return HttpResponse(str(e))

@csrf_exempt
@login_required
def organization_project_view(request, organization_id):
    '''
    组织内项目view
    :param request:
    :param organization_id:
    :return:
    '''
    user = request.user
    try:
        if request.method == 'GET':
            status, errmsg, organization = OrganizationAPI.get(
                user=user,
                organization_id=organization_id
            )
            if not status:
                return HttpResponse(errmsg)
                # 组织内项目
            status, errmsg, projects = ProjectAPI.all(user=user)
            if not status:
                return HttpResponse(errmsg)
            projects = projects.filter(organization=organization).distinct()
            context = {
                'app': app,
                'organization': organization,
                'organization_id': organization_id,
                'projects': projects
            }
            return render(
                request,
                'organization/organization_info_project.html',
                context
            )
    except Exception as e:
        return HttpResponse(str(e))

@csrf_exempt
@login_required
def organization_template_view(request, organization_id):
    '''
    组织内模板view
    :param request:
    :param organization_id:
    :return:
    '''
    user = request.user
    try:
        if request.method == 'GET':
            status, errmsg, organization = OrganizationAPI.get(
                user=user,
                organization_id=organization_id
            )
            if not status:
                return HttpResponse(errmsg)
            # 组织内模板
            status, errmsg, templates = TemplateAPI.all(user=user)
            if not status:
                return HttpResponse(errmsg)
            final_templates = []
            templates = templates.distinct()
            for template in templates:
                if template.organization == organization:
                    final_templates.append(template)
            context = {
                'app': app,
                'organization': organization,
                'organization_id': organization_id,
                'templates': templates
            }
            return render(
                request,
                'organization/organization_info_template.html',
                context
            )
    except Exception as e:
        return HttpResponse(str(e))





@csrf_exempt
@login_required
def organization_role_view(request, organization_id):
    '''
    获取一个组织的角色
    :param request:
    :param organization_id:
    :return:
    '''
    user = request.user
    try:
        if request.is_ajax():
            if request.method == 'GET':
                status, errmsg, org = OrganizationAPI.get(
                    user=user,
                    organization_id=organization_id
                )
                if not status:
                    return JsonResponse(
                        {ARK_STATUS: False, ARK_ERRMSG: errmsg}
                    )
                org_roles = Role.objects.filter(organization=org)
                org_roles_array = list()
                for role in org_roles:
                    if role.name == RO_SYS_ADMIN:
                        continue
                    org_roles_array.append(role.to_json())
                return JsonResponse(
                    {
                        ARK_STATUS: True,
                        'org_roles': org_roles_array
                    }
                )
    except Exception as e:
        return JsonResponse(
            {ARK_STATUS: False, ARK_ERRMSG: str(e)}
        )

@csrf_exempt
@login_required
def team_role_view(request, team_id):
    '''
    获取一个团队的角色
    :param request:
    :param team_id:
    :return:
    '''
    user = request.user
    try:
        if request.is_ajax():
            if request.method == 'GET':
                status, errmsg, team = TeamAPI.get(
                    user=user,
                    team_id=team_id
                )
                if not status:
                    return JsonResponse(
                        {ARK_STATUS: False, ARK_ERRMSG: errmsg}
                    )
                team_roles = team.roles.filter(resource_type=RS_TEAM)
                team_roles_array = list()
                for team_role in team_roles:
                    team_roles_array.append(team_role.to_json())
                return JsonResponse(
                    {
                        ARK_STATUS: True,
                        'team_roles': team_roles_array
                    }
                )
    except Exception as e:
        return JsonResponse(
            {ARK_STATUS: False, ARK_ERRMSG: str(e)}
        )


