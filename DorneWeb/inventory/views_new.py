from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.conf import settings

from .api import InventoryAPI, HostAPI, GroupAPI
from misc.decorator import in_team_required
from misc.const import *
from misc.api import UserAndTeamRoleAPI, InternalAPI
from organization.api import OrganizationAPI


app = 'inventory'


# 列出所有仓库
@csrf_exempt
@login_required
def inventories_view(request):
    try:
        status, msg, orgs = OrganizationAPI.all(request.user)

        if not status:
            return HttpResponse(msg)
        
        filted_orgs = []

        for org in orgs:
            if InternalAPI.get_user_permissions_on_resource(
                request.user, RS_ORG, org.id
            ).get(PM_CREATE_INVENTORY):
                filted_orgs.append(org)

        context = {
            'app': app,
            'organizations': filted_orgs,
            'path_api_inventories': reverse('inventory:api_inventories'),
            'path_api_inventory_create': reverse('inventory:api_inventory_create')
        }

        return render(request, 'inventory/inventories.html', context)
    except Exception as e:
        return HttpResponse(str(e))


# 查看仓库详情
@csrf_exempt
@login_required
def inventory_detail_view(request, inventory_id):
    try:
        status, msg, inv = InventoryAPI.get(request.user, inventory_id)

        if not status:
            return HttpResponse(msg)

        context = {
            'app': app,
            'inventory': inv,
            'pm': InternalAPI.get_user_permissions_on_resource(
                request.user, RS_INV, inv.id
            ),
            'path_api_inventory_hosts': reverse(
                'inventory:api_inventory_hosts',
                kwargs={'inventory_id': inv.id}
            ),
            'path_api_host_create': reverse('inventory:api_host_create')
        }

        return render(request, 'inventory/inventory_base.html', context)
    except Exception as e:
        return HttpResponse(str(e))


# 列出所有用户/团队的所有角色
@csrf_exempt
@login_required
def inventory_roles_view(request, inventory_id):
    try:
        status, msg, inv = InventoryAPI.get(request.user, inventory_id)

        if not status:
            return HttpResponse(msg)

        users = inv.users

        users_with_roles = []

        for user in users:
            status, msg, roles = UserAndTeamRoleAPI.get_user_roles_on_resource(
                request.user, user.id, RS_INV, inventory_id
            )

            if status:
                users_with_roles.append([user, roles])

        teams = inv.teams

        teams_with_roles = []

        for team in teams:
            status, msg, roles = UserAndTeamRoleAPI.get_team_roles_on_resource(
                request.user, team.id, RS_INV, inventory_id
            )

            if status:
                teams_with_roles.append([team, roles])

        all_users = inv.organization.users

        context = {
            'app': app,
            'inventory': inv,
            'pm': InternalAPI.get_user_permissions_on_resource(
                request.user, RS_INV, inv.id
            ),
            'users_with_roles': users_with_roles,
            'teams_with_roles': teams_with_roles,
            'all_users': all_users,
            'all_teams': inv.organization.team_set.all(),
            'roles': inv.roles.filter(resource_type=RS_INV),
        }

        return render(request, 'inventory/inventory_roles.html', context)
    except Exception as e:
        return HttpResponse(str(e))


# 添加用户/团队角色
@csrf_exempt
@login_required
def inventory_roles_add_view(request, inventory_id):
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
                        'inventory:inventory_roles',
                        kwargs={'inventory_id': inventory_id}
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
                        'inventory:inventory_roles',
                        kwargs={'inventory_id': inventory_id}
                    )
                )
            else:
                return HttpResponse('404')
    except Exception as e:
        return HttpResponse(str(e))


# 移除用户/团队角色
@csrf_exempt
@login_required
def inventory_roles_remove_view(request, inventory_id):
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
                        'inventory:inventory_roles',
                        kwargs={'inventory_id': inventory_id}
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
                        'inventory:inventory_roles',
                        kwargs={'inventory_id': inventory_id}
                    )
                )
            else:
                return HttpResponse('404')
    except Exception as e:
        return HttpResponse(str(e))


################################ API接口 ################################
# 列出所有仓库
@csrf_exempt
@login_required
def api_inventories_view(request):
    try:
        if request.is_ajax() and request.method == 'GET':
            status, msg, invs = InventoryAPI.all(request.user)

            if not status:
                return JsonResponse({
                    ARK_STATUS: status,
                    ARK_MSG: msg
                })

            inventories = []

            for i in invs:
                inventories.append({
                    'id': i.id,
                    'name': i.name,
                    'description': i.description,
                    'organization': {
                        'name': i.organization.name,
                        'path': reverse(
                            'organization:organization_detail',
                            kwargs={'organization_id': i.organization.id}
                        )
                    },
                    'pm': InternalAPI.get_user_permissions_on_resource(
                        request.user, RS_INV, i.id
                    ),
                    'path': reverse('inventory:inventory_detail', kwargs={'inventory_id': i.id}),
                    'path_api_delete': reverse('inventory:api_inventory_delete')
                })

            return JsonResponse({
                ARK_STATUS: True,
                'invs': inventories,
            })
        else:
            return JsonResponse({
                ARK_STATUS: False,
                # ARK_MSG: 'Unknown operation'
                ARK_MSG: '未知的操作'
            })
    except Exception as e:
        return JsonResponse({
            ARK_STATUS: False,
            # ARK_MSG: 'Unknown error'
            ARK_MSG: str(e) if settings.DEBUG else '未知的错误'
        })


# 新建仓库
@csrf_exempt
@login_required
def api_inventory_create_view(request):
    try:
        if request.is_ajax() and request.method == 'POST':
            data = request.POST.dict()
            status, msg = InventoryAPI.create(request.user, **data)

            return JsonResponse({
                ARK_STATUS: status,
                ARK_MSG: msg
            })
        else:
            return JsonResponse({
                ARK_STATUS: False,
                # ARK_MSG: 'Unknown operation'
                ARK_MSG: '未知的操作'
            })
    except Exception as e:
        return JsonResponse({
            ARK_STATUS: False,
            # ARK_MSG: 'Unknown error'
            ARK_MSG: str(e) if settings.DEBUG else '未知的错误'
        })


# 删除仓库
@csrf_exempt
@login_required
def api_inventory_delete_view(request):
    try:
        if request.is_ajax() and request.method == 'POST':
            data = request.POST.dict()
            status, msg = InventoryAPI.delete(request.user, data.get('inventory_id'))

            return JsonResponse({
                ARK_STATUS: status,
                ARK_MSG: msg
            })
        else:
            return JsonResponse({
                ARK_STATUS: False,
                # ARK_MSG: 'Unknown operation'
                ARK_MSG: '未知的操作'
            })
    except Exception as e:
        return JsonResponse({
            ARK_STATUS: False,
            # ARK_MSG: 'Unknown error'
            ARK_MSG: str(e) if settings.DEBUG else '未知的错误'
        })


# 修改仓库
@csrf_exempt
@login_required
def api_inventory_edit_view(request, inventory_id):
    try:
        if request.is_ajax() and request.method == 'POST':
            data = request.POST.dict()
            status, msg = InventoryAPI.update(
                request.user, inventory_id, **data
            )

            return JsonResponse({
                ARK_STATUS: status,
                ARK_MSG: msg
            })
        else:
            return JsonResponse({
                ARK_STATUS: False,
                # ARK_MSG: 'Unknown operation'
                ARK_MSG: '未知的操作'
            })
    except Exception as e:
        return JsonResponse({
            ARK_STATUS: False,
            # ARK_MSG: 'Unknown error'
            ARK_MSG: str(e) if settings.DEBUG else '未知的错误'
        })


# 列出仓库中所有主机
@csrf_exempt
@login_required
def api_inventory_hosts_view(request, inventory_id):
    try:
        if request.is_ajax() and request.method == 'GET':
            status, msg, inv = InventoryAPI.get(request.user, inventory_id)

            if not status:
                return JsonResponse({
                    ARK_STATUS: status,
                    ARK_MSG: msg
                })
            
            hosts = []

            for i in inv.host_set.all():
                hosts.append({
                    'id': i.id,
                    'name': i.name,
                    'ip': i.ip,
                    'description': i.description,
                    'pm': InternalAPI.get_user_permissions_on_resource(
                        request.user, RS_INV, inv.id
                    ),
                    'path_api_detail': reverse('inventory:api_host_detail', kwargs={'host_id': i.id}),
                    'path_api_delete': reverse('inventory:api_host_delete')
                })

            return JsonResponse({
                ARK_STATUS: True,
                'hosts': hosts,
            })
        else:
            return JsonResponse({
                ARK_STATUS: False,
                # ARK_MSG: 'Unknown operation'
                ARK_MSG: '未知的操作'
            })
    except Exception as e:
        return JsonResponse({
            ARK_STATUS: False,
            # ARK_MSG: 'Unknown error'
            ARK_MSG: str(e) if settings.DEBUG else '未知的错误'
        })


# 新建主机
@csrf_exempt
@login_required
def api_host_create_view(request):
    try:
        if request.is_ajax() and request.method == 'POST':
            data = request.POST.dict()
            status, msg = HostAPI.create(request.user, **data)

            return JsonResponse({
                ARK_STATUS: status,
                ARK_MSG: msg
            })
        else:
            return JsonResponse({
                ARK_STATUS: False,
                # ARK_MSG: 'Unknown operation'
                ARK_MSG: '未知的操作'
            })
    except Exception as e:
        return JsonResponse({
            ARK_STATUS: False,
            # ARK_MSG: 'Unknown error'
            ARK_MSG: str(e) if settings.DEBUG else '未知的错误'
        })


# 查看主机详情
@csrf_exempt
@login_required
def api_host_detail_view(request, host_id):
    try:
        if request.is_ajax() and request.method == 'GET':
            status, msg, host = HostAPI.get(request.user, host_id)

            if not status:
                return JsonResponse({
                    ARK_STATUS: status,
                    ARK_MSG: msg
                })

            return JsonResponse({
                ARK_STATUS: True,
                'host': {
                    'name': host.name,
                    'ip': host.ip,
                    'description': host.description,
                    'vars': host.vars,
                    'path_api_edit': reverse(
                        'inventory:api_host_edit',
                        kwargs={'host_id': host.id}
                    )
                }
            })
        else:
            return JsonResponse({
                ARK_STATUS: False,
                # ARK_MSG: 'Unknown operation'
                ARK_MSG: '未知的操作'
            })
    except Exception as e:
        return JsonResponse({
            ARK_STATUS: False,
            # ARK_MSG: 'Unknown error'
            ARK_MSG: str(e) if settings.DEBUG else '未知的错误'
        })


# 修改主机
@csrf_exempt
@login_required
def api_host_edit_view(request, host_id):
    try:
        if request.is_ajax and request.method == 'POST':
            data = request.POST.dict()
            status, msg = HostAPI.update(
                request.user, host_id, **data
            )

            return JsonResponse({
                ARK_STATUS: status,
                ARK_MSG: msg
            })
        else:
            return JsonResponse({
                ARK_STATUS: False,
                # ARK_MSG: 'Unknown operation'
                ARK_MSG: '未知的操作'
            })
    except Exception as e:
        return JsonResponse({
            ARK_STATUS: False,
            # ARK_MSG: 'Unknown error'
            ARK_MSG: str(e) if settings.DEBUG else '未知的错误'
        })


# 删除主机
@csrf_exempt
@login_required
def api_host_delete_view(request):
    try:
        if request.is_ajax and request.method == 'POST':
            data = request.POST.dict()
            status, msg = HostAPI.delete(request.user, data.get('host_id'))

            return JsonResponse({
                ARK_STATUS: status,
                ARK_MSG: msg
            })
        else:
            return JsonResponse({
                ARK_STATUS: False,
                # ARK_MSG: 'Unknown operation'
                ARK_MSG: '未知的操作'
            })
    except Exception as e:
        return JsonResponse({
            ARK_STATUS: False,
            # ARK_MSG: 'Unknown error'
            ARK_MSG: str(e) if settings.DEBUG else '未知的错误'
        })


# 列出仓库中所有组
@csrf_exempt
@login_required
def api_inventory_groups_view(request, inventory_id):
    try:
        if request.is_ajax() and request.method == 'GET':
            status, msg, inv = InventoryAPI.get(request.user, inventory_id)

            if not status:
                return JsonResponse({
                    ARK_STATUS: status,
                    ARK_MSG: msg
                })
            
            groups = []

            for i in inv.group_set.all():
                groups.append({
                    'id': i.id,
                    'name': i.name,
                    'description': i.description,
                    'pm': InternalAPI.get_user_permissions_on_resource(
                        request.user, RS_INV, inv.id
                    ),
                    'path_api_detail': reverse('inventory:api_group_detail', kwargs={'group_id': i.id}),
                    'path_api_delete': reverse('inventory:api_group_delete')
                })

            return JsonResponse({
                ARK_STATUS: True,
                'groups': groups,
            })
        else:
            return JsonResponse({
                ARK_STATUS: False,
                # ARK_MSG: 'Unknown operation'
                ARK_MSG: '未知的操作'
            })
    except Exception as e:
        return JsonResponse({
            ARK_STATUS: False,
            # ARK_MSG: 'Unknown error'
            ARK_MSG: str(e) if settings.DEBUG else '未知的错误'
        })


# 新建组
@csrf_exempt
@login_required
def api_group_create_view(request):
    try:
        if request.is_ajax() and request.method == 'POST':
            data = request.POST.dict()
            status, msg = GroupAPI.create(request.user, **data)

            return JsonResponse({
                ARK_STATUS: status,
                ARK_MSG: msg
            })
        else:
            return JsonResponse({
                ARK_STATUS: False,
                # ARK_MSG: 'Unknown operation'
                ARK_MSG: '未知的操作'
            })
    except Exception as e:
        return JsonResponse({
            ARK_STATUS: False,
            # ARK_MSG: 'Unknown error'
            ARK_MSG: str(e) if settings.DEBUG else '未知的错误'
        })


# 查看组详情
@csrf_exempt
@login_required
def api_group_detail_view(request, group_id):
    try:
        if request.is_ajax() and request.method == 'GET':
            status, msg, group = GroupAPI.get(request.user, group_id)

            if not status:
                return JsonResponse({
                    ARK_STATUS: status,
                    ARK_MSG: msg
                })
            
            candidate_hosts = []

            for i in group.inv.host_set.all():
                candidate_hosts.append({
                    'id': i.id,
                    'name': i.name,
                    'ip': i.ip
                })
            
            candidate_groups = []

            for i in group.inv.group_set.all():
                candidate_groups.append({
                    'id': i.id,
                    'name': i.name
                })
            
            group_hosts = []

            for i in group.host_set.all():
                group_hosts.append({
                    'id': i.id,
                    'name': i.name,
                    'ip': i.ip
                })
            
            group_groups = []

            for i in group.group_set.all():
                group_groups.append({
                    'id': i.id,
                    'name': i.name
                })

            return JsonResponse({
                ARK_STATUS: True,
                'group': {
                    'name': group.name,
                    'description': group.description,
                    'vars': group.vars,
                    'path_api_edit': reverse('inventory:api_group_edit', kwargs={'group_id': group.id}),
                    'path_api_add_host_into_group': reverse('inventory:api_add_host_into_group'),
                    'path_api_add_group_into_group': reverse('inventory:api_add_group_into_group')
                    'has_hosts': bool(group_hosts),
                    'has_groups': bool(group_groups),
                    'hosts': group_hosts,
                    'groups': group_groups
                }
                'candidate_hosts': candidate_hosts,
                'candidate_groups': candidate_groups
            })
        else:
            return JsonResponse({
                ARK_STATUS: False,
                # ARK_MSG: 'Unknown operation'
                ARK_MSG: '未知的操作'
            })
    except Exception as e:
        return JsonResponse({
            ARK_STATUS: False,
            # ARK_MSG: 'Unknown error'
            ARK_MSG: str(e) if settings.DEBUG else '未知的错误'
        })


# 修改组
@csrf_exempt
@login_required
def inventory_group_edit_view(request, inventory_id, group_id):
    try:
        if request.method == 'POST':
            data = request.POST.dict()
            status, msg, inv = InventoryAPI.get(request.user, inventory_id)

            if not status:
                return HttpResponse(msg)

            status, msg, group = GroupAPI.get(request.user, group_id)

            if not status:
                return HttpResponse(msg)

            if group.inventory != inv:
                return HttpResponse(ARK_ERRMSG_CONTENT[1201])

            status, msg = GroupAPI.update(request.user, group_id, **data)

            if not status:
                return HttpResponse(msg)

            return HttpResponseRedirect(
                reverse(
                    'inventory:inventory_group_detail',
                    kwargs={'inventory_id': inventory_id, 'group_id': group_id}
                )
            )
    except Exception as e:
        return HttpResponse(str(e))


# 删除组
@csrf_exempt
@login_required
def inventory_group_delete_view(request, inventory_id, group_id):
    try:
        if request.method == 'POST':
            status, msg, inv = InventoryAPI.get(request.user, inventory_id)

            if not status:
                return HttpResponse(msg)

            status, msg, group = GroupAPI.get(request.user, group_id)

            if not status:
                return HttpResponse(msg)

            if group.inventory != inv:
                return HttpResponse(ARK_ERRMSG_CONTENT[1201])

            status, msg = GroupAPI.delete(request.user, group_id)

            if not status:
                return HttpResponse(msg)

            return HttpResponseRedirect(
                reverse(
                    'inventory:inventory_groups',
                    kwargs={'inventory_id': inventory_id}
                )
            )
        else:
            return HttpResponse('404')
    except Exception as e:
        return HttpResponse(str(e))


# 将主机加入组
@csrf_exempt
@login_required
def add_host_into_group_view(request, group_id):
    try:
        if request.method == 'POST':
            data = request.POST
            host_id_list = data.getlist('host_id')

            for host_id in host_id_list:
                status, msg = HostAPI.add_into_group(
                    request.user, int(host_id), group_id
                )

                if not status:
                    return HttpResponse(msg)

            status, msg, group = GroupAPI.get(request.user, group_id)

            if not status:
                return HttpResponse(msg)

            return HttpResponseRedirect(
                reverse(
                    'inventory:inventory_group_detail',
                    kwargs={
                        'inventory_id': group.inventory.id,
                        'group_id': group_id,
                    }
                )
            )
    except Exception as e:
        return HttpResponse(str(e))


# 将主机移出组
@csrf_exempt
@login_required
def remove_host_from_group_view(request, group_id):
    try:
        if request.method == 'POST':
            data = request.POST.dict()

            status, msg = HostAPI.remove_from_group(
                request.user, group_id=group_id, **data
            )

            if not status:
                return HttpResponse(msg)

            status, msg, group = GroupAPI.get(request.user, group_id)

            if not status:
                return HttpResponse(msg)

            return HttpResponseRedirect(
                reverse(
                    'inventory:inventory_group_detail',
                    kwargs={
                        'inventory_id': group.inventory.id,
                        'group_id': group_id,
                    }
                )
            )
    except Exception as e:
        return HttpResponse(str(e))


# 将组加入组
@csrf_exempt
@login_required
def add_group_into_group_view(request, group_id):
    try:
        if request.method == 'POST':
            data = request.POST
            cgid_list = data.getlist('cgid')

            for cgid in cgid_list:
                status, msg = GroupAPI.add_into_group(
                    request.user, int(cgid), group_id
                )

                if not status:
                    return HttpResponse(msg)

            status, msg, group = GroupAPI.get(request.user, group_id)

            if not status:
                return HttpResponse(msg)

            return HttpResponseRedirect(
                reverse(
                    'inventory:inventory_group_detail',
                    kwargs={
                        'inventory_id': group.inventory.id,
                        'group_id': group_id,
                    }
                )
            )
    except Exception as e:
        return HttpResponse(str(e))


# 将组移出组
@csrf_exempt
@login_required
def remove_group_from_group_view(request, group_id):
    try:
        if request.method == 'POST':
            data = request.POST.dict()

            status, msg = GroupAPI.remove_from_group(
                request.user, pgid=group_id, **data
            )

            if not status:
                return HttpResponse(msg)

            status, msg, group = GroupAPI.get(request.user, group_id)

            if not status:
                return HttpResponse(msg)

            return HttpResponseRedirect(
                reverse(
                    'inventory:inventory_group_detail',
                    kwargs={
                        'inventory_id': group.inventory.id,
                        'group_id': group_id,
                    }
                )
            )
    except Exception as e:
        return HttpResponse(str(e))
