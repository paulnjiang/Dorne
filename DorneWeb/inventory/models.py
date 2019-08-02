import json
import yaml

from django.db import models

from misc.models import Role
from organization.models import Organization
from user.models import User, Team


class Inventory(models.Model):
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=128, null=True, blank=True)
    vars = models.TextField(null=True, blank=True)

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    # 与资源相关的角色
    roles = models.ManyToManyField(Role)

    @property
    def teams(self):
        return Team.objects.filter(owned_roles__inventory=self).distinct()

    @property
    def users(self):
        return User.objects.filter(roles__inventory=self).distinct()

    def gen_content(self):
        content = {}
        group_all = {}
        hosts = {}

        for i in self.host_set.all():
            if not i.groups.exists():
                hosts[i.name] = i.gen_dict()
        
        if hosts:
            group_all['hosts'] = hosts
        
        groups = {}

        for i in self.group_set.all():
            if not i.parent_groups.exists():
                groups[i.name] = i.gen_dict()
        
        if groups:
            group_all['children'] = groups
        
        if self.vars:
            group_all['vars'] = json.loads(self.vars)
        
        content['all'] = group_all
        
        return yaml.dump(content)


class Group(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128, null=True)
    vars = models.TextField(null=True)

    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    parent_groups = models.ManyToManyField('self', symmetrical=False)

    @property
    def ancestors(self):
        result = self.parent_groups.all()
        to_visit = set()
        visited = set()

        for i in result:
            to_visit.add(i)

        while to_visit:
            g = to_visit.pop()
            sub_result = g.parent_groups.all()
            visited.add(g)

            for i in sub_result:
                if i in to_visit or i in visited:
                    continue

                to_visit.add(i)

            result = result | sub_result

        result = result.distinct()

        return result

    @property
    def descendants(self):
        result = self.group_set.all()
        to_visit = set()
        visited = set()

        for i in result:
            to_visit.add(i)

        while to_visit:
            g = to_visit.pop()
            sub_result = g.group_set.all()
            visited.add(g)

            for i in sub_result:
                if i in to_visit or i in visited:
                    continue

                to_visit.add(i)

            result = result | sub_result

        result = result.distinct()

        return result
    
    def gen_dict(self):
        result = {}

        hosts = {}

        for i in self.host_set.all():
            hosts[i.name] = i.gen_dict()
        
        if hosts:
            result['hosts'] = hosts
        
        if self.vars:
            result['vars'] = json.loads(self.vars)
        
        groups = {}

        for i in self.group_set.all():
            groups[i.name] = i.gen_dict()
        
        if groups:
            result['children'] = groups

        return result


class Host(models.Model):
    name = models.CharField(max_length=64)
    ip = models.GenericIPAddressField()
    description = models.CharField(max_length=128, null=True, blank=True)
    status = models.BooleanField(default=True)
    vars = models.TextField(null=True, blank=True, default='')

    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group)

    def gen_dict(self):
        result = {}

        if self.vars:
            result = json.loads(self.vars)
        
        result['ansible_ssh_host'] = self.ip

        return result
