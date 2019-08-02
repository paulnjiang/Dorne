from django.db import transaction

from misc.api import InternalAPI
from misc.const import *
from organization.models import Organization
from .models import User, Team


class UserAPI:
    @staticmethod
    def update(user, target_user_id, name=None, chinese_name=None, phone=None):
        try:
            target_user = User.objects.get(id=target_user_id)

            if target_user != user:
                return False, ARK_ERRMSG_CONTENT[1201]

            if name is not None:
                target_user.name = name

            if chinese_name is not None:
                target_user.chinese_name = chinese_name

            if phone is not None:
                target_user.phone = phone

            target_user.save()

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get(user, target_user_id):
        try:
            target_user = User.objects.get(id=target_user_id)

            if user == target_user:
                return True, None, target_user
            elif user.roles.filter(resource_type=RS_SYS, name=RO_SYS_ADMIN)\
                    .exists():
                return True, None, target_user
            # 当两者在一个组织时
            elif target_user.organizations & user.organizations:
                return True, None, target_user

            return False, ARK_ERRMSG_CONTENT[1201], None
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def all(user):
        try:
            if user.roles.filter(
                    resource_type=RS_SYS,
                    name=RO_SYS_ADMIN
            ).exists():
                return True, None, User.objects.all()
            else:
                ret = list()
                user_orgs = user.organizations
                if user_orgs.count() != 0:
                    for user_org in user_orgs:
                        if user.roles.filter(
                            resource_type=RS_ORG,
                            resource_id=user_org.id,
                            name=RO_ORG_ADMIN
                        ).exists():
                            ret.extend(user_org.users)
                        # 组织成员
                        else:
                            users = user_org.users.exclude(
                                roles__name=RO_ORG_ADMIN
                            )
                            ret.extend(users)
                            #ret.extend([user])
                    else:
                        ret_set = set(ret)
                        ret_list = list(ret_set)
                        return True, None, ret_list
                else:
                    return True, None, [user]
        except Exception as e:
            return False, str(e), None

    # @staticmethod
    # def filter(user):
    #     pass


class TeamAPI:
    @staticmethod
    def create(user, organization_id, name, description=None):
        try:
            errmsg = list()
            if organization_id == None:
                errmsg.append('组织ID不能为空')
            if name == None or len(name) == 0:
                errmsg.append('团队名字不能为空')
            if len(errmsg) != 0:
                return False, ','.join(errmsg), None

            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_ORG, organization_id
            )

            if not pm_list[PM_CREATE_TEAM]:
                return False, ARK_ERRMSG_CONTENT[1201]

            org = Organization.objects.get(id=organization_id)
            team = Team(name=name, organization=org)

            if description is not None:
                team.description = description

            with transaction.atomic():
                team.save()
                InternalAPI.update_resource_and_roles_relationship(
                    RS_TEAM, team.id
                )

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete(user, team_id):
        try:
            team = Team.objects.get(id=team_id)
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_TEAM, team.id
            )

            if not pm_list[PM_DELETE_TEAM]:
                return False, ARK_ERRMSG_CONTENT[1201]

            if User.objects.filter(roles__team=team).\
                    exclude(roles__name__in=[RO_ORG_ADMIN, RO_SYS_ADMIN])\
                    .exists():
                return False, '该团队内仍有普通用户存在'

            #if team.user_set.exists():
                #return False, 'users belong to team exist'

            Team.objects.filter(id=team.id).delete()

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update(user, team_id, name=None, description=None):
        try:
            errmsg = list()
            if team_id == None:
                errmsg.append('团队ID不能为空')
            team = Team.objects.get(id=team_id)
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_TEAM, team.id
            )

            if not pm_list[PM_UPDATE_TEAM]:
                return False, ARK_ERRMSG_CONTENT[1201]

            if name is not None:
                team.name = name

            if description is not None:
                team.description = description
            team.save()
            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get(user, team_id):
        try:
            team = Team.objects.get(id=team_id)
            #pm_list = InternalAPI.get_user_permissions_on_resource(
                #user, RS_ORG, team.organization.id
            #)
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_TEAM, team.id
            )
            if not pm_list[PM_RETRIEVE_TEAM]:
                return False, ARK_ERRMSG_CONTENT[1201], None

            return True, None, team
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def all(user):
        # try:
        #     if user.roles.filter(resource_type=RS_SYS, name=RO_SYS_ADMIN).exists():
        #         return True, None, Team.objects.all()
        #     elif user.organization and user.roles.filter(resource_type=RS_ORG,
        #                                                  resource_id=user.organization.id, name=RO_ORG_ADMIN):
        #         return True, None, user.organization.team_set.all()
        #     elif user.team:
        #         teams = [user.team]
        #     else:
        #         teams = []
        #     return True, None, teams
        # except Exception as e:
        #     return False, str(e), None
        try:
            if user.roles.filter(
                    resource_type=RS_SYS,
                    name=RO_SYS_ADMIN
            ).exists():
                return True, None, Team.objects.all()
            else:
                user_teams = user.teams
                return True, None, user_teams
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def get_team_users(user, team_id):
        '''
        返回一个team内的所有用户
        :param user:
        :param team_id:
        :return:
        '''
        try:
            team = Team.objects.get(id=team_id)
            # pm_list = InternalAPI.get_user_permissions_on_resource(
            #         user, RS_ORG, team.organization.id
            #     )
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_TEAM, team.id
            )
            if pm_list[PM_RETRIEVE_TEAM]:
                return True, None, team.users
            return True, None, [user]
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def get_team_permission(user, team_id):
        '''
        用户可以查看所能管理的用户在其他资源上的角色
        :param user: 调用者
        :param target_user_id: 被查看者
        :return:
        '''
        pm_list_sys = InternalAPI.get_user_permissions_on_resource(user, RS_SYS)
        status, errmsg, team = TeamAPI.get(user, team_id)
        if not status:
            return False, '获取团队出错', None
        pm_list_org = []
        if team.organization:
            pm_list_org = InternalAPI.get_user_permissions_on_resource(
                user=user,
                resource_type=RS_ORG,
                resource_id=team.organization.id
            )
        # 系统管理员 或者 组织管理员
        if pm_list_sys[PM_RETRIEVE_SYSTEM_ROLE] or (
                len(pm_list_org) != 0 and
                pm_list_org[PM_RETRIEVE_ORGANIZATION_ROLE]):
            ret = {}
            return True, None, ret
        return False, ARK_ERRMSG_CONTENT[1201], None

    # @staticmethod
    # def filter(user):
    #     pass
