from django.http import HttpResponse

from .api import InternalAPI
from .const import *


# 用户如果既不是超级管理员，又不是组织管理员，那么必须属于一个团队，否则返回空白
def in_team_required(func):
    def wrapper(request, *args, **kwargs):
        # 超级管理员
        if InternalAPI.get_user_roles_on_resource(request.user, RS_SYS)\
                .filter(resource_type=RS_SYS, name=RO_SYS_ADMIN).exists():
            return func(request, *args, **kwargs)

        # 组织管理员
        if (request.user.organization
                and InternalAPI.get_user_roles_on_resource(
                    request.user, RS_ORG, request.user.organization.id
                ).filter(resource_type=RS_ORG, name=RO_ORG_ADMIN).exists()):
            return func(request, *args, **kwargs)

        if not request.user.team:
            return HttpResponse('请属于一个团队。')

        return func(request, *args, **kwargs)

    return wrapper
