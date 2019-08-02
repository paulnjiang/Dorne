from .const import *
from .api import InternalAPI
class Checker:
    @staticmethod
    def dict_fields_check(require_fields, input_dict):
        '''
        检查dict参数是否缺少必要字段
        :param require_fields: 需要的字段
        :param input_dict: 输入的字典
        :return: 缺少的字段
        '''
        missed_fields = []
        for field in require_fields:
            if field not in input_dict:
                missed_fields.append(field)
        return missed_fields

    @staticmethod
    def dict_args_check(require_fields, input_data):
        if not isinstance(input_data, dict):
            return {
                ARK_STATUS: False,
                ARK_ERRMSG: ARK_ERRMSG_CONTENT[1101]
            }
        missed_fields = Checker.dict_fields_check(require_fields, input_data)
        if len(missed_fields) != 0:
            return {
                ARK_STATUS: False,
                ARK_ERRMSG: ARK_ERRMSG_CONTENT[1102] + ':' + ','.join(missed_fields)
            }
        else:
            return {
                ARK_STATUS: True
            }

class Helper:
    @staticmethod
    def is_system_admin(user):
        try:
            pm_list = InternalAPI.get_user_permissions_on_resource(
                user=user,
                resource_type=RS_SYS
            )
            if pm_list[PM_RETRIEVE_SYSTEM_ROLE]:
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def is_organization_admin(role):
        pass

    @staticmethod
    def has_access(expected_roles, user_roles, team_roles=None):
        """
        :param expected_roles: 你希望用户拥有的最低角色，三元组
        :param user_roles: 用户实际拥有的角色，三元组
        :param team_roles: 用户所属团队实际拥有的角色，三元组，如果没有就传None
        :return: True or False
        """
        if expected_roles[0] is not None:
            for i in user_roles[0]:
                if i >= expected_roles[0]:
                    return True

        if expected_roles[1] is not None:
            for i in user_roles[1]:
                if i >= expected_roles[1]:
                    return True

        if expected_roles[2] is not None:
            for i in user_roles[2]:
                if i >= expected_roles[2]:
                    return True

            if not user_roles[2] and team_roles:
                for i in team_roles[2]:
                    if i >= expected_roles[2]:
                        return True

        return False
