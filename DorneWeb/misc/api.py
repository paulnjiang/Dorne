from .const import *
from .models import Role
from inventory.models import Inventory
from project.models import Project
from project.models import JobTemplate
from user.models import User, Team
from organization.models import Organization


class UserAndTeamRoleAPI:
    @staticmethod
    def add_role_to_user(user, target_user_id, role_id):
        try:
            role = Role.objects.get(id=role_id)

            target_user = User.objects.get(id=target_user_id)

            if role.resource_type == RS_SYS:
                pm_list = InternalAPI.get_user_permissions_on_resource(
                    user, RS_SYS
                )

                if not pm_list[PM_ADD_SYSTEM_ROLE]:
                    return False, ARK_ERRMSG_CONTENT[1201]
            elif role.resource_type == RS_ORG:
                pm_list = InternalAPI.get_user_permissions_on_resource(
                    user, RS_ORG, role.resource_id
                )

                if not pm_list[PM_ADD_ORGANIZATION_ROLE]:
                    return False, ARK_ERRMSG_CONTENT[1201]
            elif role.resource_type in [RS_TEAM, RS_INV, RS_PRO, RS_TEM]:
                model_dict = {
                    RS_TEAM: Team,
                    RS_INV: Inventory,
                    RS_PRO: Project,
                    RS_TEM: JobTemplate,
                }

                # resource = model_dict[role.resource_type].objects.get(
                #     id=role.resource_id
                # )

                # if resource.organization not in target_user.organizations:
                #     return False, 'user and resource are not ' \
                #                   'in the same organization'

                pm_dict = {
                    RS_TEAM: PM_ADD_TEAM_ROLE,
                    RS_INV: PM_ADD_INVENTORY_ROLE,
                    RS_PRO: PM_ADD_PROJECT_ROLE,
                    RS_TEM: PM_ADD_TEMPLATE_ROLE,
                }
                pm_list = InternalAPI.get_user_permissions_on_resource(
                    user, role.resource_type, role.resource_id
                )

                if not pm_list[pm_dict[role.resource_type]]:
                    return False, ARK_ERRMSG_CONTENT[1201]

            if not target_user.roles.filter(id=role.id).exists():
                target_user.roles.add(role)

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete_role_from_user(user, target_user_id, role_id):
        try:
            role = Role.objects.get(id=role_id)

            target_user = User.objects.get(id=target_user_id)

            if role.resource_type == RS_SYS:
                pm_list = InternalAPI.get_user_permissions_on_resource(
                    user, RS_SYS
                )

                if not pm_list[PM_REMOVE_SYSTEM_ROLE]:
                    return False, ARK_ERRMSG_CONTENT[1201]
            elif role.resource_type in [
                RS_ORG, RS_TEAM, RS_INV, RS_PRO, RS_TEM
            ]:
                pm_dict = {
                    RS_ORG: PM_REMOVE_ORGANIZATION_ROLE,
                    RS_TEAM: PM_REMOVE_TEAM_ROLE,
                    RS_INV: PM_REMOVE_INVENTORY_ROLE,
                    RS_PRO: PM_REMOVE_PROJECT_ROLE,
                    RS_TEM: PM_REMOVE_TEMPLATE_ROLE,
                }
                pm_list = InternalAPI.get_user_permissions_on_resource(
                    user, role.resource_type, role.resource_id
                )

                if not pm_list[pm_dict[role.resource_type]]:
                    return False, ARK_ERRMSG_CONTENT[1201]

            if not target_user.roles.filter(id=role.id).exists():
                return False, 'user does not have this role'

            target_user.roles.remove(role)

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_user_roles_on_resource(
            user, target_user_id, resource_type, resource_id=None
    ):
        try:
            target_user = User.objects.get(id=target_user_id)

            if resource_type == RS_SYS:
                pm_list = InternalAPI.get_user_permissions_on_resource(
                    user, RS_SYS
                )

                if not pm_list[PM_RETRIEVE_SYSTEM_ROLE]:
                    return False, ARK_ERRMSG_CONTENT[1201], None
            elif resource_type in [RS_ORG, RS_TEAM, RS_INV, RS_PRO, RS_TEM]:
                pm_dict = {
                    RS_ORG: PM_RETRIEVE_ORGANIZATION_ROLE,
                    RS_TEAM: PM_RETRIEVE_TEAM_ROLE,
                    RS_INV: PM_RETRIEVE_INVENTORY_ROLE,
                    RS_PRO: PM_RETRIEVE_PROJECT_ROLE,
                    RS_TEM: PM_RETRIEVE_TEMPLATE_ROLE,
                }
                pm_list = InternalAPI.get_user_permissions_on_resource(
                    user, resource_type, resource_id
                )

                if not pm_list[pm_dict[resource_type]]:
                    return False, ARK_ERRMSG_CONTENT[1201], None

            return True, None, InternalAPI.get_user_roles_on_resource(
                target_user, resource_type, resource_id
            )
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def add_role_to_team(user, target_team_id, role_id):
        try:
            role = Role.objects.get(id=role_id)

            target_team = Team.objects.get(id=target_team_id)

            if role.resource_type in [RS_INV, RS_PRO, RS_TEM]:
                model_dict = {
                    RS_INV: Inventory,
                    RS_PRO: Project,
                    RS_TEM: JobTemplate,
                }

                resource = model_dict[role.resource_type].objects.get(
                    id=role.resource_id
                )

                if resource.organization != target_team.organization:
                    return False, 'team and resource are not ' \
                                  'in the same organization'

                pm_dict = {
                    RS_INV: PM_ADD_INVENTORY_ROLE,
                    RS_PRO: PM_ADD_PROJECT_ROLE,
                    RS_TEM: PM_ADD_TEMPLATE_ROLE,
                }
                pm_list = InternalAPI.get_user_permissions_on_resource(
                    user, role.resource_type, role.resource_id
                )

                if not pm_list[pm_dict[role.resource_type]]:
                    return False, ARK_ERRMSG_CONTENT[1201]

            if not target_team.owned_roles.filter(id=role.id).exists():
                target_team.owned_roles.add(role)

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete_role_from_team(user, target_team_id, role_id):
        try:
            role = Role.objects.get(id=role_id)

            target_team = Team.objects.get(id=target_team_id)

            if role.resource_type in [RS_INV, RS_PRO, RS_TEM]:
                pm_dict = {
                    RS_INV: PM_REMOVE_INVENTORY_ROLE,
                    RS_PRO: PM_REMOVE_PROJECT_ROLE,
                    RS_TEM: PM_REMOVE_TEMPLATE_ROLE,
                }
                pm_list = InternalAPI.get_user_permissions_on_resource(
                    user, role.resource_type, role.resource_id
                )

                if not pm_list[pm_dict[role.resource_type]]:
                    return False, ARK_ERRMSG_CONTENT[1201]

            if not target_team.owned_roles.filter(id=role.id).exists():
                return False, 'team does not have this role'

            target_team.owned_roles.remove(role)

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_team_roles_on_resource(
            user, target_team_id, resource_type, resource_id
    ):
        try:
            target_team = Team.objects.get(id=target_team_id)

            if resource_type in [RS_INV, RS_PRO, RS_TEM]:
                pm_dict = {
                    RS_INV: PM_RETRIEVE_INVENTORY_ROLE,
                    RS_PRO: PM_RETRIEVE_PROJECT_ROLE,
                    RS_TEM: PM_RETRIEVE_TEMPLATE_ROLE,
                }
                pm_list = InternalAPI.get_user_permissions_on_resource(
                    user, resource_type, resource_id
                )

                if not pm_list[pm_dict[resource_type]]:
                    return False, ARK_ERRMSG_CONTENT[1201], None

            return True, None, InternalAPI.get_team_roles_on_resource(
                target_team, resource_type, resource_id
            )
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def get_user_role(user, target_user_id):
        '''
        用户可以查看所能管理的用户在其他资源上的角色
        :param user: 调用者
        :param target_user_id: 被查看者
        :return:
        '''
        #
        pm_list_sys = InternalAPI.get_user_permissions_on_resource(user, RS_SYS)
        target_user = User.objects.get(id=target_user_id)
        ret = {}

        # 查看者是系统管理员
        if len(pm_list_sys) != 0 and PM_RETRIEVE_SYSTEM_ROLE in pm_list_sys and \
                pm_list_sys[PM_RETRIEVE_SYSTEM_ROLE]:
            ret[RS_SYS] = InternalAPI.get_user_roles_on_resource(
                user=target_user,
                resource_type=RS_SYS
            )

        # 被查看者在组织上的角色
        ret[RS_ORG] = list()
        org_resources = InternalAPI.get_user_resources_by_resource_type(
            user=target_user,
            resource_type=RS_ORG
        )
        for org in org_resources:
            org_roles = InternalAPI.get_user_roles_on_resource(
                user=target_user,
                resource_type=RS_ORG,
                resource_id=org.id
            )
            if org_roles.count() != 0:
                item = [org, org_roles]
                ret[RS_ORG].append(item)
        # 被查看者在inventory的角色
        ret[RS_INV] = list()
        inventories = InternalAPI.get_user_resources_by_resource_type(
            user=target_user,
            resource_type=RS_INV
        )
        for inventory in inventories:
            inv_roles = InternalAPI.get_user_roles_on_resource(
                user=target_user,
                resource_type=RS_INV,
                resource_id=inventory.id
            )
            if inv_roles.count() != 0:
                item = [inventory, inv_roles]
                ret[RS_INV].append(item)

        # 被查看者在project的角色
        ret[RS_PRO] = list()
        projects = InternalAPI.get_user_resources_by_resource_type(
            user=target_user,
            resource_type=RS_PRO
        )
        for project in projects:
            project_roles = InternalAPI.get_user_roles_on_resource(
                user=target_user,
                resource_type=RS_PRO,
                resource_id=project.id
            )
            if project_roles.count() != 0:
                item = [project, project_roles]
                ret[RS_PRO].append(item)

        # 被查看者在job template的角色
        ret[RS_TEMPLATE] = list()
        templates = InternalAPI.get_user_resources_by_resource_type(
            user=target_user,
            resource_type=RS_TEM
        )
        for template in templates:
            template_roles = InternalAPI.get_user_roles_on_resource(
                user=target_user,
                resource_type=RS_TEM,
                resource_id=template.id
            )
            if template_roles.count() != 0:
                item = [template, template_roles]
                ret[RS_TEM].append(item)

        # 被查看者在team上的角色
        ret[RS_TEAM] = list()
        teams = InternalAPI.get_user_resources_by_resource_type(
            user=target_user,
            resource_type=RS_TEAM
        )
        for team in teams:
            team_roles = InternalAPI.get_user_roles_on_resource(
                user=target_user,
                resource_type=RS_TEAM,
                resource_id=team.id
            )
            if team_roles.count() != 0:
                item = [team, team_roles]
                ret[RS_TEAM].append(item)

        #print('roles', ret)
        return True, None, ret
        # return False, ARK_ERRMSG_CONTENT[1201], None

    @staticmethod
    def get_team_role(user, team_id):
        '''
        用户可以查看所能管理的团队在其他资源上的角色
        :param user: 调用者
        :param target_user_id: 被查看者
        :return:
        '''
        #pm_list_sys = InternalAPI.get_user_permissions_on_resource(user, RS_SYS)
        team = Team.objects.get(id=team_id)
        ret = {}

        # 被查看者在inventory的角色
        ret[RS_INV] = list()
        inventories = InternalAPI.get_team_resources_by_resource_type(
            team=team,
            resource_type=RS_INV
        )
        for inventory in inventories:
            inv_roles = InternalAPI.get_team_roles_on_resource(
                team=team,
                resource_type=RS_INV,
                resource_id=inventory.id
            )
            inv_roles = inv_roles.exclude(
                resource_type__in=[RS_SYSTEM, RS_ORGANIZATION]
            ).distinct()
            if inv_roles.count() != 0:
                item = [inventory, inv_roles]
                ret[RS_INV].append(item)

        # 被查看者在project的角色
        ret[RS_PRO] = list()
        projects = InternalAPI.get_team_resources_by_resource_type(
            team=team,
            resource_type=RS_PRO
        )
        for project in projects:
            project_roles = InternalAPI.get_team_roles_on_resource(
                team=team,
                resource_type=RS_PRO,
                resource_id=project.id
            )
            project_roles = project_roles.exclude(
                resource_type__in=[RS_SYSTEM, RS_ORGANIZATION]
            ).distinct()
            if project_roles.count() != 0:
                item = [project, project_roles]
                ret[RS_PRO].append(item)

        # 被查看者在job template的角色
        ret[RS_TEMPLATE] = list()
        templates = InternalAPI.get_team_resources_by_resource_type(
            team=team,
            resource_type=RS_TEM
        )
        for template in templates:
            template_roles = InternalAPI.get_team_roles_on_resource(
                team=team,
                resource_type=RS_TEM,
                resource_id=template.id
            )
            template_roles = template_roles.exclude(
                resource_type__in=[RS_SYSTEM, RS_ORGANIZATION]
            ).distinct()
            if template_roles.count() != 0:
                item = [template, template_roles]
                ret[RS_TEM].append(item)
        return True, None, ret



class ResourceTypeError(RuntimeError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return 'bad resource type: ' + str(self.value)


class InternalAPI:
    # 获得指定用户在指定资源上的所有相关角色，可能包括系统角色和组织角色
    @staticmethod
    def get_user_roles_on_resource(user, resource_type, resource_id=None):
        if resource_type == RS_SYS:
            return user.roles.filter(resource_type=resource_type)
        elif resource_type in [RS_ORG, RS_TEAM, RS_INV, RS_PRO, RS_TEM]:
            model_dict = {
                RS_ORG: Organization,
                RS_TEAM: Team,
                RS_INV: Inventory,
                RS_PRO: Project,
                RS_TEM: JobTemplate,
            }
            resource = model_dict[resource_type].objects.get(id=resource_id)

            return resource.roles.filter(user=user)
        else:
            raise ResourceTypeError(resource_type)

    # 获得指定团队在指定资源上的所有相关角色
    # 现阶段，团队是没有系统角色和组织角色的，所以一定要传入resource_id
    @staticmethod
    def get_team_roles_on_resource(team, resource_type, resource_id):
        if resource_type in [RS_INV, RS_PRO, RS_TEM]:
            model_dict = {
                RS_INV: Inventory,
                RS_PRO: Project,
                RS_TEM: JobTemplate,
            }
            resource = model_dict[resource_type].objects.get(id=resource_id)

            return resource.roles.filter(owner_teams=team)
        else:
            raise ResourceTypeError(resource_type)

    # 根据资源类型与角色，更新权限列表
    @staticmethod
    def __update_pm_list_by_roles(pm_list, resource_type, roles):
        for role in roles:
            for pm in PM_LIST[resource_type][role.resource_type][role.name]:
                if pm not in pm_list:
                    pm_list[pm] = True

        return pm_list

    # 获得指定用户在指定资源上的所有权限
    # 权限在misc/const.py中定义
    @staticmethod
    def get_user_permissions_on_resource(
            user, resource_type, resource_id=None
    ):
        if resource_type == RS_SYS:
            roles = InternalAPI.get_user_roles_on_resource(user, resource_type)
            pm_list = {}
            pm_list = InternalAPI.__update_pm_list_by_roles(
                pm_list, resource_type, roles
            )

            return pm_list
        elif resource_type in [RS_ORG, RS_TEAM]:
            roles = InternalAPI.get_user_roles_on_resource(
                user, resource_type, resource_id
            )
            pm_list = {}
            pm_list = InternalAPI.__update_pm_list_by_roles(
                pm_list, resource_type, roles
            )
            return pm_list
        elif resource_type in [RS_INV, RS_PRO, RS_TEM]:
            user_roles = InternalAPI.get_user_roles_on_resource(
                user, resource_type, resource_id
            )
            pm_list = {}
            pm_list = InternalAPI.__update_pm_list_by_roles(
                pm_list, resource_type, user_roles
            )

            skip_team_roles = False

            for role in user_roles:
                if role.resource_type == resource_type:
                    skip_team_roles = True
                    break

            if not skip_team_roles:
                for team in user.teams:
                    team_roles = InternalAPI.get_team_roles_on_resource(
                        team, resource_type, resource_id
                    )
                    pm_list = InternalAPI.__update_pm_list_by_roles(
                        pm_list, resource_type, team_roles
                    )

            return pm_list
        else:
            raise ResourceTypeError(resource_type)

    # 获得与指定用户相关的所有指定类型的资源
    @staticmethod
    def get_user_resources_by_resource_type(user, resource_type):
        if resource_type in [RS_ORG, RS_TEAM]:
            model_dict = {
                RS_ORG: Organization,
                RS_TEAM: Team,
            }
            resources = model_dict[resource_type].objects.filter(
                roles__user=user
            ).distinct()

            return resources
        elif resource_type in [RS_INV, RS_PRO, RS_TEM]:
            model_dict = {
                RS_INV: Inventory,
                RS_PRO: Project,
                RS_TEM: JobTemplate,
            }
            resources = model_dict[resource_type].objects.filter(
                roles__user=user
            )

            for team in user.teams:
                rt = model_dict[resource_type].objects.filter(
                    roles__owner_teams=team
                )
                resources = resources | rt
            return resources.distinct()
        else:
            raise ResourceTypeError(resource_type)

    @staticmethod
    def get_team_resources_by_resource_type(team, resource_type):
        if resource_type in [RS_INV, RS_PRO, RS_TEM]:
            model_dict = {
                RS_INV: Inventory,
                RS_PRO: Project,
                RS_TEM: JobTemplate,
            }
            resources = model_dict[resource_type].objects.filter(
                roles__owner_teams=team,
            )
            return resources.distinct()
        else:
            raise ResourceTypeError(resource_type)

    # 获得与指定资源相关的所有用户
    @staticmethod
    def get_resource_users(resource_type, resource_id=None):
        if resource_type == RS_SYS:
            users = User.objects.filter(roles__resource_type=resource_type)

            return users.distinct()
        elif resource_type in [RS_ORG, RS_TEAM, RS_INV, RS_PRO, RS_TEM]:
            model_dict = {
                RS_ORG: Organization,
                RS_TEAM: Team,
                RS_INV: Inventory,
                RS_PRO: Project,
                RS_TEM: JobTemplate,
            }
            resource = model_dict[resource_type].objects.get(id=resource_id)
            roles = resource.roles.all()
            users = User.objects.filter(roles__in=roles).distinct()

            return users
        else:
            raise ResourceTypeError(resource_type)

    # 获得与指定资源相关的所有团队
    @staticmethod
    def get_resource_teams(resource_type, resource_id):
        if resource_type in [RS_INV, RS_PRO, RS_TEM]:
            model_dict = {
                RS_INV: Inventory,
                RS_PRO: Project,
                RS_TEM: JobTemplate,
            }
            resource = model_dict[resource_type].objects.get(id=resource_id)

            return resource.teams
        else:
            raise ResourceTypeError(resource_type)

    # 获得与指定资源相关的所有角色
    @staticmethod
    def get_resource_roles(resource_type, resource_id=None):
        if resource_type == RS_SYS:
            roles = Role.objects.filter(resource_type=resource_type)

            return roles
        elif resource_type in [RS_ORG, RS_TEAM, RS_INV, RS_PRO, RS_TEM]:
            model_dict = {
                RS_ORG: Organization,
                RS_TEAM: Team,
                RS_INV: Inventory,
                RS_PRO: Project,
                RS_TEM: JobTemplate,
            }
            resource = model_dict[resource_type].objects.get(id=resource_id)
            roles = resource.roles.all()

            return roles
        else:
            raise ResourceTypeError(resource_type)

    # 生成与指定资源相关的角色
    @staticmethod
    def __gen_roles_by_resource(resource_type, resource_id=None):
        if resource_type == RS_SYS:
            for role_name in ROLE_LIST[resource_type]:
                if not Role.objects.filter(
                        resource_type=resource_type, name=role_name
                ).exists():
                    role_detail = ROLE_LIST[resource_type][role_name]
                    Role.objects.create(
                        resource_type=resource_type,
                        name=role_name,
                        display_name=role_detail[ROLE_DIS_KEY],
                        description=role_detail[ROLE_DES_KEY]
                    )
        elif resource_type in [RS_ORG, RS_TEAM, RS_INV, RS_PRO, RS_TEM]:
            assert isinstance(resource_id, int)

            for role_name in ROLE_LIST[resource_type]:
                if not Role.objects.filter(
                        resource_type=resource_type,
                        resource_id=resource_id,
                        name=role_name
                ).exists():
                    role_detail = ROLE_LIST[resource_type][role_name]
                    Role.objects.create(
                        resource_type=resource_type,
                        resource_id=resource_id,
                        name=role_name,
                        display_name=role_detail[ROLE_DIS_KEY],
                        description=role_detail[ROLE_DES_KEY]
                    )
        else:
            raise ResourceTypeError(resource_type)

    # 更新指定资源和相关角色的关联关系
    # 在创建资源时调用
    @staticmethod
    def update_resource_and_roles_relationship(resource_type, resource_id):
        if resource_type == RS_ORG:
            resource = Organization.objects.get(id=resource_id)

            InternalAPI.__gen_roles_by_resource(RS_SYS)
            system_admin = Role.objects.get(
                resource_type=RS_SYS, name=RO_SYS_ADMIN
            )

            if not resource.roles.filter(id=system_admin.id).exists():
                resource.roles.add(system_admin)

            InternalAPI.__gen_roles_by_resource(resource_type, resource_id)

            for role_name in ROLE_LIST[resource_type]:
                role = Role.objects.get(
                    resource_type=resource_type,
                    resource_id=resource_id,
                    name=role_name
                )

                if not resource.roles.filter(id=role.id).exists():
                    resource.roles.add(role)
        elif resource_type in [RS_TEAM, RS_INV, RS_PRO, RS_TEM]:
            model_dict = {
                RS_TEAM: Team,
                RS_INV: Inventory,
                RS_PRO: Project,
                RS_TEM: JobTemplate,
            }
            resource = model_dict[resource_type].objects.get(id=resource_id)

            InternalAPI.__gen_roles_by_resource(RS_SYS)
            system_admin = Role.objects.get(
                resource_type=RS_SYS, name=RO_SYS_ADMIN
            )

            if not resource.roles.filter(id=system_admin.id).exists():
                resource.roles.add(system_admin)

            org = resource.organization
            InternalAPI.__gen_roles_by_resource(RS_ORG, int(org.id))
            org_admin = Role.objects.get(
                resource_type=RS_ORG,
                resource_id=org.id,
                name=RO_ORG_ADMIN
            )

            if not resource.roles.filter(id=org_admin.id).exists():
                resource.roles.add(org_admin)

            InternalAPI.__gen_roles_by_resource(resource_type, resource_id)

            for role_name in ROLE_LIST[resource_type]:
                role = Role.objects.get(
                    resource_type=resource_type,
                    resource_id=resource_id,
                    name=role_name
                )

                if not resource.roles.filter(id=role.id).exists():
                    resource.roles.add(role)
        else:
            raise ResourceTypeError(resource_type)

    @staticmethod
    def get_role(resource_type, resource_name, resource_id=None):
        if resource_name == RO_SYSTEM_ADMIN:
            return Role.objects.filter(
                resource_type=resource_type,
                name=resource_name,
            ).first()
        else:
            return Role.objects.filter(
                resource_type=resource_type,
                name=resource_name,
                resource_id=resource_id
            ).first()

