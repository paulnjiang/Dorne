from django.db import transaction
from django.db.models import QuerySet
from misc.api import InternalAPI
from misc.const import *
from .models import Organization


class OrganizationAPI:
    @staticmethod
    def create(user, name, description=None):
        try:
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_SYS
            )

            if not pm_list[PM_CREATE_ORGANIZATION]:
                return False, ARK_ERRMSG_CONTENT[1201]

            if name == None or len(name) == 0:
                return False, '组织名字不能为空'

            org = Organization(name=name)

            if description is not None:
                org.description = description

            with transaction.atomic():
                org.save()
                InternalAPI.update_resource_and_roles_relationship(
                    RS_ORG, org.id
                )

            return True, None, org.id
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete(user, organization_id):
        try:
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_ORG, organization_id
            )

            if not pm_list[PM_DELETE_ORGANIZATION]:
                return False, ARK_ERRMSG_CONTENT[1201]

            org = Organization.objects.get(id=organization_id)

            if org.inventory_set.exists():
                return False, 'inventories exist'

            if org.project_set.exists():
                return False, 'projects exist'

            if org.team_set.exists():
                return False, 'teams exist'

            Organization.objects.filter(id=org.id).delete()

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update(user, organization_id, name=None, description=None):
        try:
            if organization_id == None:
                return False, '组织id传入不合法'
            if name == None or len(name) == 0:
                return False, '组织名字不能为空'
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_ORG, organization_id
            )

            if not pm_list[PM_UPDATE_ORGANIZATION]:
                return False, ARK_ERRMSG_CONTENT[1201]

            org = Organization.objects.get(id=organization_id)

            if name is not None:
                org.name = name

            if description is not None:
                org.description = description

            org.save()

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get(user, organization_id):
        try:
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_ORG, organization_id
            )

            if not pm_list[PM_RETRIEVE_ORGANIZATION]:
                return False, ARK_ERRMSG_CONTENT[1201], None

            org = Organization.objects.get(id=organization_id)

            return True, None, org
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def all(user):
        try:
            orgs = InternalAPI.get_user_resources_by_resource_type(
                user, RS_ORG
            )
            orgs = orgs.distinct()
            return True, None, orgs
        except Exception as e:
            return False, str(e), None

    # @staticmethod
    # def filter(user):
    #     pass

    @staticmethod
    def get_all_teams(user, organization_id):
        try:
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_ORG, organization_id
            )

            if not pm_list[PM_RETRIEVE_TEAM]:
                return False, ARK_ERRMSG_CONTENT[1201], None

            org = Organization.objects.get(id=organization_id)

            return True, None, org.team_set.all()
        except Exception as e:
            return False, str(e), None


    @staticmethod
    def get_teams_user_can_retrieve(user, organization_id):
        try:
            status, errmsg, org = OrganizationAPI.get(
                user=user,
                organization_id=organization_id
            )
            if not status:
                return False, ARK_ERRMSG_CONTENT[1201], None
            teams = org.team_set.all()
            teams_user_can_retrieve = list()
            for team in teams:
                pm_list = InternalAPI.get_user_permissions_on_resource(
                    user=user,
                    resource_type=RS_TEAM,
                    resource_id=team.id
                )
                if PM_RETRIEVE_TEAM not in pm_list:
                    continue
                if pm_list[PM_RETRIEVE_TEAM]:
                    teams_user_can_retrieve.append(team)
            else:
                return True, None, teams_user_can_retrieve
        except Exception as e:
            print('here')
            return False, str(e), None

    @staticmethod
    def get_all_users(user, organization_id):
        '''
        获取组织内用户
        :param user:
        :param organization_id:
        :return:
        '''
        try:
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user, RS_ORG, organization_id
            )

            if not pm_list[PM_RETRIEVE_ORGANIZATION]:
                return False, ARK_ERRMSG_CONTENT[1201], None

            org = Organization.objects.get(id=organization_id)

            return True, None, org.users
        except Exception as e:
            return False, str(e), None