import os
import json
import socket

from django.db import transaction
from django.conf import settings

from misc.api import InternalAPI
from misc.const import *
from organization.models import Organization
from .models import Inventory, Host, Group


class InventoryAPI:
    @staticmethod
    def create(user, organization_id, name, description=None, vars=None):
        try:
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_ORG, organization_id
            )

            if not pm_list.get(PM_CREATE_INVENTORY):
                return False, ARK_ERRMSG_CONTENT[1201]

            org = Organization.objects.get(id=organization_id)

            if not name or len(name)<4 or len(name)>32:
                return False, '名称长度必须为4～32个字符'

            if Inventory.objects.filter(name=name, organization=org).exists():
                return False, '组织中已存在同名仓库'

            inv = Inventory(name=name, organization=org)

            if description is not None:
                if len(description) > 128:
                    return False, '描述长度必须小于等于128个字符'
                
                inv.description = description

            if vars is not None:
                if vars != '':
                    try:
                        tmp_vars = json.loads(vars)

                        if not isinstance(tmp_vars, dict):
                            return False, '变量必须为对象形式的数据'
                    except json.decoder.JSONDecodeError:
                        return False, '变量必须为JSON格式的数据'
                
                inv.vars = vars

            with transaction.atomic():
                inv.save()
                InternalAPI.update_resource_and_roles_relationship(
                    RS_INV, inv.id
                )

            return True, None
        except Exception as e:
            return False, str(e) if settings.DEBUG else '未知的错误'

    @staticmethod
    def delete(user, inventory_id):
        try:
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_INV, inventory_id
            )

            if not pm_list.get(PM_DELETE_INVENTORY):
                return False, ARK_ERRMSG_CONTENT[1201]

            inv = Inventory.objects.get(id=inventory_id)

            if inv.host_set.exists():
                return False, '仓库中存在主机'

            if inv.group_set.exists():
                return False, '仓库中存在组'

            Inventory.objects.filter(id=inv.id).delete()

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update(user, inventory_id, name=None, description=None, vars=None):
        try:
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_INV, inventory_id
            )

            if not pm_list.get(PM_UPDATE_INVENTORY):
                return False, ARK_ERRMSG_CONTENT[1201]

            inv = Inventory.objects.get(id=inventory_id)

            if name is not None:
                if len(name)<4 or len(name)>32:
                    return False, '名称长度必须为4～32个字符'
                
                if Inventory.objects.filter(name=name, organization=inv.organization).exclude(id=inv.id).exists():
                    return False, '组织中已存在同名仓库'
                
                inv.name = name

            if description is not None:
                if len(description) > 128:
                    return False, '描述长度必须小于等于128个字符'
                
                inv.description = description

            if vars is not None:
                if vars != '':
                    try:
                        tmp_vars = json.loads(vars)

                        if not isinstance(tmp_vars, dict):
                            return False, '变量必须为对象形式的数据'
                    except json.decoder.JSONDecodeError:
                        return False, '变量必须为JSON格式的数据'
                
                inv.vars = vars

            inv.save()

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get(user, inventory_id):
        try:
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_INV, inventory_id
            )

            if not pm_list.get(PM_RETRIEVE_INVENTORY):
                return False, ARK_ERRMSG_CONTENT[1201], None

            inv = Inventory.objects.get(id=inventory_id)

            return True, None, inv
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def all(user):
        try:
            invs = InternalAPI.get_user_resources_by_resource_type(
                user, RS_INV
            )

            return True, None, invs
        except Exception as e:
            return False, str(e), None

    # @staticmethod
    # def filter(user):
    #     pass

    # @staticmethod
    # def get_all_jobs(user):
    #     pass

    # @staticmethod
    # def duplicate(user):
    #     pass

    @staticmethod
    def sync(user, inventory_id):
        try:
            # pm_list = InternalAPI.get_user_permissions_on_resource(
            #     user, RS_INV, inventory_id
            # )

            # if not pm_list[PM_USE_INVENTORY_IN_JOB]:
            #     return False, ARK_ERRMSG_CONTENT[1201]

            inv = Inventory.objects.get(id=inventory_id)

            with open(os.path.join(settings.INVENTORY_DIR, str(inv.id)), 'w') as f:
                f.write(inv.gen_content())

            return True, None
        except Exception as e:
            return False, str(e)


def is_valid_ip_address(ip):
    try:
        socket.inet_pton(socket.AF_INET, ip)
    except Exception:
        try:
            socket.inet_pton(socket.AF_INET6, ip)
        except Exception:
            return False
    
    return True


class HostAPI:
    @staticmethod
    def create(
        user, inventory_id, name, ip,
        description=None, status=None, vars=None
    ):
        try:
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_INV, inventory_id
            )

            if not pm_list.get(PM_CREATE_HOST):
                return False, ARK_ERRMSG_CONTENT[1201]

            inv = Inventory.objects.get(id=inventory_id)

            if not name or len(name)<4 or len(name)>64:
                return False, '名称长度必须为4～64个字符'

            if Host.objects.filter(name=name, inventory=inv).exists():
                return False, '仓库中已存在同名主机'
            
            if not ip:
                return False, '必须填写IP地址'
            
            if not is_valid_ip_address(ip):
                return False, 'IP地址非法'
            
            if Host.objects.filter(ip=ip, inventory=inv).exists():
                return False, '仓库中已存在相同IP地址'
            
            host = Host(name=name, ip=ip, inventory=inv)

            if description is not None:
                if len(description) > 128:
                    return False, '描述长度必须小于等于128个字符'
                
                host.description = description

            if vars is not None:
                if vars != '':
                    try:
                        tmp_vars = json.loads(vars)

                        if not isinstance(tmp_vars, dict):
                            return False, '变量必须为对象形式的数据'
                    except json.decoder.JSONDecodeError:
                        return False, '变量必须为JSON格式的数据'
                
                host.vars = vars

            if status is not None:
                host.status = status

            host.save()

            return True, None
        except Exception as e:
            return False, str(e) if settings.DEBUG else '未知的错误'

    @staticmethod
    def delete(user, host_id):
        try:
            host = Host.objects.get(id=host_id)

            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_INV, host.inventory.id
            )

            if not pm_list.get(PM_DELETE_HOST):
                return False, ARK_ERRMSG_CONTENT[1201]

            Host.objects.filter(id=host.id).delete()

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update(
            user, host_id,
            name=None, ip=None, description=None, status=None, vars=None
    ):
        try:
            host = Host.objects.get(id=host_id)

            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_INV, host.inventory.id
            )

            if not pm_list.get(PM_UPDATE_HOST):
                return False, ARK_ERRMSG_CONTENT[1201]

            if name is not None:
                if len(name)<4 or len(name)>64:
                    return False, '名称长度必须为4～64个字符'

                if Host.objects.filter(name=name, inventory=host.inventory).exclude(id=host.id).exists():
                    return False, '仓库中已存在同名主机'
                
                host.name = name

            if ip is not None:
                if not ip:
                    return False, '必须填写IP地址'
                
                if not is_valid_ip_address(ip):
                    return False, 'IP地址非法'
                
                host.ip = ip

            if description is not None:
                if len(description) > 128:
                    return False, '描述长度必须小于等于128个字符'
                
                host.description = description

            if status is not None:
                host.status = status

            if vars is not None:
                if vars != '':
                    try:
                        tmp_vars = json.loads(vars)

                        if not isinstance(tmp_vars, dict):
                            return False, '变量必须为对象形式的数据'
                    except json.decoder.JSONDecodeError:
                        return False, '变量必须为JSON格式的数据'
                
                host.vars = vars

            host.save()

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get(user, host_id):
        try:
            host = Host.objects.get(id=host_id)

            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_INV, host.inventory.id
            )

            if not pm_list.get(PM_RETRIEVE_HOST):
                return False, ARK_ERRMSG_CONTENT[1201], None

            return True, None, host
        except Exception as e:
            return False, str(e), None

    # @staticmethod
    # def all(user):
    #     pass

    # @staticmethod
    # def filter(user):
    #     pass

    @staticmethod
    def add_into_group(user, host_id, group_id):
        try:
            host = Host.objects.get(id=host_id)

            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_INV, host.inventory.id
            )

            if not pm_list.get(PM_ADD_HOST_INTO_GROUP):
                return False, ARK_ERRMSG_CONTENT[1201]

            group = Group.objects.get(id=group_id)

            if host.inventory != group.inventory:
                return False, 'host and group are not in the same inventory'

            # 判断是否是一个叶子组
            if not GroupAPI._can_be_leaf_group(group):
                return False, '主机不能加入加入到非叶子组'

            if not group.host_set.filter(id=host.id).exists():
                group.host_set.add(host)

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def remove_from_group(user, host_id, group_id):
        try:
            host = Host.objects.get(id=host_id)

            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_INV, host.inventory.id
            )

            if not pm_list.get(PM_REMOVE_HOST_FROM_GROUP):
                return False, ARK_ERRMSG_CONTENT[1201]

            group = Group.objects.get(id=group_id)

            if host.inventory != group.inventory:
                return False, 'host and group are not in the same inventory'

            if not group.host_set.filter(id=host.id).exists():
                return False, 'host does not belong to group'

            group.host_set.remove(host)

            return True, None
        except Exception as e:
            return False, str(e)


class GroupAPI:
    @staticmethod
    def create(user, inventory_id, name, description=None, vars=None):
        try:
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_INV, inventory_id
            )

            if not pm_list.get(PM_CREATE_GROUP):
                return False, ARK_ERRMSG_CONTENT[1201]

            inv = Inventory.objects.get(id=inventory_id)

            if not name or len(name)<4 or len(name)>64:
                return False, '名称长度必须为4～64个字符'

            if Group.objects.filter(name=name, inventory=inv).exists():
                return False, '仓库中已存在同名组'

            group = Group(name=name, inventory=inv)

            if description is not None:
                if len(description) > 128:
                    return False, '描述长度必须小于等于128个字符'
                
                group.description = description

            if vars is not None:
                if vars != '':
                    try:
                        tmp_vars = json.loads(vars)

                        if not isinstance(tmp_vars, dict):
                            return False, '变量必须为对象形式的数据'
                    except json.decoder.JSONDecodeError:
                        return False, '变量必须为JSON格式的数据'
                
                group.vars = vars

            group.save()

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete(user, group_id):
        try:
            group = Group.objects.get(id=group_id)

            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_INV, group.inventory.id
            )

            if not pm_list.get(PM_DELETE_GROUP):
                return False, ARK_ERRMSG_CONTENT[1201]

            if group.host_set.exists():
                return False, 'hosts belong to group exist'

            if group.group_set.exists():
                return False, 'groups belong to group exist'

            Group.objects.filter(id=group.id).delete()

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update(user, group_id, name=None, description=None, vars=None):
        try:
            group = Group.objects.get(id=group_id)

            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_INV, group.inventory.id
            )

            if not pm_list.get(PM_UPDATE_GROUP):
                return False, ARK_ERRMSG_CONTENT[1201]

            if name is not None:
                if len(name)<4 or len(name)>64:
                    return False, '名称长度必须为4～64个字符'

                if Group.objects.filter(name=name, inventory=group.inventory).exclude(id=group.id).exists():
                    return False, '仓库中已存在同名组'
                
                group.name = name

            if description is not None:
                if len(description) > 128:
                    return False, '描述长度必须小于等于128个字符'
                
                group.description = description

            if vars is not None:
                if vars != '':
                    try:
                        tmp_vars = json.loads(vars)

                        if not isinstance(tmp_vars, dict):
                            return False, '变量必须为对象形式的数据'
                    except json.decoder.JSONDecodeError:
                        return False, '变量必须为JSON格式的数据'
                
                group.vars = vars

            group.save()

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get(user, group_id):
        try:
            group = Group.objects.get(id=group_id)

            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_INV, group.inventory.id
            )

            if not pm_list.get(PM_RETRIEVE_GROUP):
                return False, ARK_ERRMSG_CONTENT[1201], None

            return True, None, group
        except Exception as e:
            return False, str(e), None

    # @staticmethod
    # def all(user):
    #     pass

    # @staticmethod
    # def filter(user):
    #     pass

    @staticmethod
    def add_into_group(user, cgid, pgid):
        try:
            cg = Group.objects.get(id=cgid)

            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_INV, cg.inventory.id
            )

            if not pm_list.get(PM_ADD_GROUP_INTO_GROUP):
                return False, ARK_ERRMSG_CONTENT[1201]

            pg = Group.objects.get(id=pgid)

            if cg.inventory != pg.inventory:
                return False, 'child group and parent group' \
                              'are not in the same inventory'

            if cg == pg:
                return False, 'cannot add group to itself'

            if GroupAPI.__is_leaf_group(pg):
                return False, 'parent主机组不能是叶子主机组'

            if cg.parent_groups.filter(id=pg.id).exists():
                return True, None

            if cg in pg.ancestors:
                return False, '形成环了'

            cg.parent_groups.add(pg)

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def remove_from_group(user, cgid, pgid):
        try:
            cg = Group.objects.get(id=cgid)

            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_INV, cg.inventory.id
            )

            if not pm_list.get(PM_REMOVE_GROUP_FROM_GROUP):
                return False, ARK_ERRMSG_CONTENT[1201]

            pg = Group.objects.get(id=pgid)

            if cg.inventory != pg.inventory:
                return False, 'child group and parent group' \
                              'are not in the same inventory'

            if cg == pg:
                return False, 'cannot delete group from itself'

            if not cg.parent_groups.filter(id=pg.id).exists():
                return False, 'child group does not belong to parent group'

            cg.parent_groups.remove(pg)

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def _can_be_leaf_group(group):
        if group.group_set.exists():
            return False
        return True

    @staticmethod
    def __is_leaf_group(group):
        if group.host_set.exists():
            return True
        return False
