from django.db import models


# 角色表，是整个权限系统的核心，由他将用户和资源联系起来
class Role(models.Model):
    # 资源类型，目前有系统、组织、仓库、项目、模板5种
    resource_type = models.CharField(max_length=32)

    # 资源ID，除了系统之外，其他都对应到一个资源实体上
    resource_id = models.IntegerField(null=True)

    # 角色名，代表资源上的实际角色，如管理员、使用者等
    name = models.CharField(max_length=32)

    # 显示名，用于在界面上显示角色名称
    display_name = models.CharField(max_length=32)

    # 描述，用于介绍该角色在该资源上的权限
    description = models.CharField(max_length=128)

    class Meta:
        unique_together = [
            'resource_type',
            'resource_id',
            'name',
        ]
    def to_json(self):
        return {
            'id': self.id,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description
        }
