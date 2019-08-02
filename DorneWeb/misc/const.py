# ARK代表api return key
ARK_STATUS = 'status'
ARK_ERRMSG = 'errmsg'
ARK_MSG = 'msg'
ARK_RESULT = 'result'
# 错误码与错误信息
ARK_ERRMSG_CONTENT = {
    1000: 'OK',

    1100: '参数错误',
    1101: '期待一个字典型参数',
    1102: '字典参数缺少必要字段',

    1200: '权限错误',
    1201: '您需要权限来执行此操作',
    1202: '您不在任何团队中',

    1300: '内部错误',
    1301: '未实现',

    1400: '数据库相关错误',
}

# 资源类型与角色类型
RS_SYSTEM = 'system'
RS_ORGANIZATION = 'organization'
RS_TEAM = 'team'
RS_INVENTORY = 'inventory'
RS_PROJECT = 'project'
RS_TEMPLATE = 'template'

RO_SYSTEM_ADMIN = 'system_admin'

RO_ORGANIZATION_ADMIN = 'organization_admin'
RO_ORGANIZATION_MEMBER = 'organization_member'

RO_TEAM_MEMBER = 'team_member'

RO_INVENTORY_ADMIN = 'inventory_admin'
RO_INVENTORY_USER = 'inventory_user'

RO_PROJECT_ADMIN = 'project_admin'
RO_PROJECT_USER = 'project_user'

RO_TEMPLATE_ADMIN = 'template_admin'
RO_TEMPLATE_USER = 'template_user'

# key
ROLE_DISPLAY_KEY = 'display_name'
ROLE_DESCRIPTION_KEY = 'description'

# 角色列表
ROLE_LIST = {
    RS_SYSTEM: {
        RO_SYSTEM_ADMIN: {
            ROLE_DISPLAY_KEY: '系统管理员',
            ROLE_DESCRIPTION_KEY: '拥有系统中所有权限',
        },
    },
    RS_ORGANIZATION: {
        RO_ORGANIZATION_ADMIN: {
            ROLE_DISPLAY_KEY: '组织管理员',
            ROLE_DESCRIPTION_KEY: '拥有组织中所有权限，但不能删除组织',
        },
        RO_ORGANIZATION_MEMBER: {
            ROLE_DISPLAY_KEY: '组织成员',
            ROLE_DESCRIPTION_KEY: '可以查看组织',
        },
    },
    RS_TEAM: {
        RO_TEAM_MEMBER: {
            ROLE_DISPLAY_KEY: '团队成员',
            ROLE_DESCRIPTION_KEY: '可以查看团队',
        },
    },
    RS_INVENTORY: {
        RO_INVENTORY_ADMIN: {
            ROLE_DISPLAY_KEY: '仓库管理员',
            ROLE_DESCRIPTION_KEY: '可以管理仓库，包括其中的主机和组',
        },
        RO_INVENTORY_USER: {
            ROLE_DISPLAY_KEY: '仓库使用者',
            ROLE_DESCRIPTION_KEY: '可以查看仓库，使用仓库创建模板',
        },
    },
    RS_PROJECT: {
        RO_PROJECT_ADMIN: {
            ROLE_DISPLAY_KEY: '项目管理员',
            ROLE_DESCRIPTION_KEY: '可以管理项目',
        },
        RO_PROJECT_USER: {
            ROLE_DISPLAY_KEY: '项目使用者',
            ROLE_DESCRIPTION_KEY: '可以查看项目，使用项目创建模板',
        },
    },
    RS_TEMPLATE: {
        RO_TEMPLATE_ADMIN: {
            ROLE_DISPLAY_KEY: '模板管理员',
            ROLE_DESCRIPTION_KEY: '可以管理模板，但对相关任务仅可查看',
        },
        RO_TEMPLATE_USER: {
            ROLE_DISPLAY_KEY: '模板使用者',
            ROLE_DESCRIPTION_KEY: '可以查看模板，从模板发送任务，查看相关任务',
        },
    },
}

# 简称
RS_SYS = RS_SYSTEM
RS_ORG = RS_ORGANIZATION
RS_INV = RS_INVENTORY
RS_PRO = RS_PROJECT
RS_TEM = RS_TEMPLATE

RO_SYS_ADMIN = RO_SYSTEM_ADMIN

RO_ORG_ADMIN = RO_ORGANIZATION_ADMIN
RO_ORG_MEMBER = RO_ORGANIZATION_MEMBER

RO_INV_ADMIN = RO_INVENTORY_ADMIN
RO_INV_USER = RO_INVENTORY_USER

RO_PRO_ADMIN = RO_PROJECT_ADMIN
RO_PRO_USER = RO_PROJECT_USER

RO_TEM_ADMIN = RO_TEMPLATE_ADMIN
RO_TEM_USER = RO_TEMPLATE_USER

ROLE_DIS_KEY = ROLE_DISPLAY_KEY
ROLE_DES_KEY = ROLE_DESCRIPTION_KEY

# 权限
PM_RETRIEVE_SYSTEM_ROLE = 'retrieve_system_role'
PM_ADD_SYSTEM_ROLE = 'add_system_role'
PM_REMOVE_SYSTEM_ROLE = 'remove_system_role'

PM_CREATE_ORGANIZATION = 'create_organization'
PM_DELETE_ORGANIZATION = 'delete_organization'
PM_UPDATE_ORGANIZATION = 'update_organization'
PM_RETRIEVE_ORGANIZATION = 'retrieve_organization'
PM_RETRIEVE_ORGANIZATION_ROLE = 'retrieve_organization_role'
PM_ADD_ORGANIZATION_ROLE = 'add_organization_role'
PM_REMOVE_ORGANIZATION_ROLE = 'remove_organization_role'

PM_CREATE_TEAM = 'create_team'
PM_DELETE_TEAM = 'delete_team'
PM_UPDATE_TEAM = 'update_team'
PM_RETRIEVE_TEAM = 'retrieve_team'
PM_RETRIEVE_TEAM_ROLE = 'retrieve_team_role'
PM_ADD_TEAM_ROLE = 'add_team_role'
PM_REMOVE_TEAM_ROLE = 'remove_team_role'

PM_CREATE_INVENTORY = 'create_inventory'
PM_DELETE_INVENTORY = 'delete_inventory'
PM_UPDATE_INVENTORY = 'update_inventory'
PM_RETRIEVE_INVENTORY = 'retrieve_inventory'
PM_USE_INVENTORY_IN_JOB = 'use_inventory_in_job'
PM_SYNC_INVENTORY = 'sync_inventory'
PM_RETRIEVE_INVENTORY_ROLE = 'retrieve_inventory_role'
PM_ADD_INVENTORY_ROLE = 'add_inventory_role'
PM_REMOVE_INVENTORY_ROLE = 'remove_inventory_role'

PM_CREATE_HOST = 'create_host'
PM_DELETE_HOST = 'delete_host'
PM_UPDATE_HOST = 'update_host'
PM_RETRIEVE_HOST = 'retrieve_host'
PM_ADD_HOST_INTO_GROUP = 'add_host_into_group'
PM_REMOVE_HOST_FROM_GROUP = 'remove_host_from_group'

PM_CREATE_GROUP = 'create_group'
PM_DELETE_GROUP = 'delete_group'
PM_UPDATE_GROUP = 'update_group'
PM_RETRIEVE_GROUP = 'retrieve_group'
PM_ADD_GROUP_INTO_GROUP = 'add_group_into_group'
PM_REMOVE_GROUP_FROM_GROUP = 'remove_group_from_group'

PM_CREATE_PROJECT = 'create_project'
PM_DELETE_PROJECT = 'delete_project'
PM_UPDATE_PROJECT = 'update_project'
PM_RETRIEVE_PROJECT = 'retrieve_project'
PM_USE_PROJECT_IN_JOB = 'use_project_in_job'
PM_SYNC_PROJECT = 'sync_project'
PM_RETRIEVE_PROJECT_ROLE = 'retrieve_project_role'
PM_ADD_PROJECT_ROLE = 'add_project_role'
PM_REMOVE_PROJECT_ROLE = 'remove_project_role'

PM_CREATE_TEMPLATE = 'create_template'
PM_DELETE_TEMPLATE = 'delete_template'
PM_UPDATE_TEMPLATE = 'update_template'
PM_RETRIEVE_TEMPLATE = 'retrieve_template'
PM_LAUNCH_TEMPLATE = 'launch_template'
PM_RETRIEVE_TEMPLATE_ROLE = 'retrieve_template_role'
PM_ADD_TEMPLATE_ROLE = 'add_template_role'
PM_REMOVE_TEMPLATE_ROLE = 'remove_template_role'

PM_DELETE_JOB = 'delete_job'
PM_RETRIEVE_JOB = 'retrieve_job'

PM_LIST = {
    RS_SYSTEM: {
        RS_SYSTEM: {
            RO_SYSTEM_ADMIN: [
                PM_RETRIEVE_SYSTEM_ROLE,
                PM_ADD_SYSTEM_ROLE,
                PM_REMOVE_SYSTEM_ROLE,
                PM_CREATE_ORGANIZATION,
                # wjj add 超管可以删除组织
                PM_DELETE_ORGANIZATION,
            ],
        },
    },
    RS_ORGANIZATION: {
        RS_SYSTEM: {
            RO_SYSTEM_ADMIN: [
                PM_DELETE_ORGANIZATION,
                PM_UPDATE_ORGANIZATION,
                PM_RETRIEVE_ORGANIZATION,
                PM_RETRIEVE_ORGANIZATION_ROLE,
                PM_ADD_ORGANIZATION_ROLE,
                PM_REMOVE_ORGANIZATION_ROLE,
                PM_CREATE_TEAM,
                PM_CREATE_INVENTORY,
                PM_CREATE_PROJECT,
            ],
        },
        RS_ORGANIZATION: {
            RO_ORGANIZATION_ADMIN: [
                PM_UPDATE_ORGANIZATION,
                PM_RETRIEVE_ORGANIZATION,
                PM_RETRIEVE_ORGANIZATION_ROLE,
                PM_ADD_ORGANIZATION_ROLE,
                PM_REMOVE_ORGANIZATION_ROLE,
                PM_CREATE_TEAM,
                PM_CREATE_INVENTORY,
                PM_CREATE_PROJECT,
            ],
            RO_ORGANIZATION_MEMBER: [
                PM_RETRIEVE_ORGANIZATION,
            ],
        },
    },
    RS_TEAM: {
        RS_SYSTEM: {
            RO_SYSTEM_ADMIN: [
                PM_DELETE_TEAM,
                PM_UPDATE_TEAM,
                PM_RETRIEVE_TEAM,
                PM_RETRIEVE_TEAM_ROLE,
                PM_ADD_TEAM_ROLE,
                PM_REMOVE_TEAM_ROLE,
            ],
        },
        RS_ORGANIZATION: {
            RO_ORGANIZATION_ADMIN: [
                PM_DELETE_TEAM,
                PM_UPDATE_TEAM,
                PM_RETRIEVE_TEAM,
                PM_RETRIEVE_TEAM_ROLE,
                PM_ADD_TEAM_ROLE,
                PM_REMOVE_TEAM_ROLE,
            ],
        },
        RS_TEAM: {
            RO_TEAM_MEMBER: [
                PM_RETRIEVE_TEAM,
            ],
        },
        RS_PROJECT: {
            RO_PROJECT_ADMIN: [
                PM_RETRIEVE_TEAM,
                PM_UPDATE_PROJECT,
                PM_RETRIEVE_PROJECT,
                PM_USE_PROJECT_IN_JOB,
                PM_SYNC_PROJECT,
                PM_RETRIEVE_PROJECT_ROLE,
            ],
            RO_PROJECT_USER: [
                PM_RETRIEVE_TEAM,
                PM_RETRIEVE_PROJECT,
                PM_USE_PROJECT_IN_JOB,
                PM_RETRIEVE_PROJECT_ROLE,
            ],
        },
    },
    RS_INVENTORY: {
        RS_SYSTEM: {
            RO_SYSTEM_ADMIN: [
                PM_DELETE_INVENTORY,
                PM_UPDATE_INVENTORY,
                PM_RETRIEVE_INVENTORY,
                PM_USE_INVENTORY_IN_JOB,
                PM_RETRIEVE_INVENTORY_ROLE,
                PM_ADD_INVENTORY_ROLE,
                PM_REMOVE_INVENTORY_ROLE,
                PM_CREATE_HOST,
                PM_DELETE_HOST,
                PM_UPDATE_HOST,
                PM_RETRIEVE_HOST,
                PM_ADD_HOST_INTO_GROUP,
                PM_REMOVE_HOST_FROM_GROUP,
                PM_CREATE_GROUP,
                PM_DELETE_GROUP,
                PM_UPDATE_GROUP,
                PM_RETRIEVE_GROUP,
                PM_ADD_GROUP_INTO_GROUP,
                PM_REMOVE_GROUP_FROM_GROUP,
            ],
        },
        RS_ORGANIZATION: {
            RO_ORGANIZATION_ADMIN: [
                PM_DELETE_INVENTORY,
                PM_UPDATE_INVENTORY,
                PM_RETRIEVE_INVENTORY,
                PM_USE_INVENTORY_IN_JOB,
                PM_RETRIEVE_INVENTORY_ROLE,
                PM_ADD_INVENTORY_ROLE,
                PM_REMOVE_INVENTORY_ROLE,
                PM_CREATE_HOST,
                PM_DELETE_HOST,
                PM_UPDATE_HOST,
                PM_RETRIEVE_HOST,
                PM_ADD_HOST_INTO_GROUP,
                PM_REMOVE_HOST_FROM_GROUP,
                PM_CREATE_GROUP,
                PM_DELETE_GROUP,
                PM_UPDATE_GROUP,
                PM_RETRIEVE_GROUP,
                PM_ADD_GROUP_INTO_GROUP,
                PM_REMOVE_GROUP_FROM_GROUP,
            ],
        },
        RS_INVENTORY: {
            RO_INVENTORY_ADMIN: [
                PM_UPDATE_INVENTORY,
                PM_RETRIEVE_INVENTORY,
                PM_USE_INVENTORY_IN_JOB,
                PM_CREATE_HOST,
                PM_DELETE_HOST,
                PM_UPDATE_HOST,
                PM_RETRIEVE_HOST,
                PM_ADD_HOST_INTO_GROUP,
                PM_REMOVE_HOST_FROM_GROUP,
                PM_CREATE_GROUP,
                PM_DELETE_GROUP,
                PM_UPDATE_GROUP,
                PM_RETRIEVE_GROUP,
                PM_ADD_GROUP_INTO_GROUP,
                PM_REMOVE_GROUP_FROM_GROUP,
            ],
            RO_INVENTORY_USER: [
                PM_RETRIEVE_INVENTORY,
                PM_USE_INVENTORY_IN_JOB,
                PM_RETRIEVE_HOST,
                PM_RETRIEVE_GROUP,
                # wjj add
                PM_RETRIEVE_INVENTORY_ROLE,
            ],
        },
    },
    RS_PROJECT: {
        RS_SYSTEM: {
            RO_SYSTEM_ADMIN: [
                PM_DELETE_PROJECT,
                PM_UPDATE_PROJECT,
                PM_RETRIEVE_PROJECT,
                PM_USE_PROJECT_IN_JOB,
                PM_SYNC_PROJECT,
                PM_RETRIEVE_PROJECT_ROLE,
                PM_ADD_PROJECT_ROLE,
                PM_REMOVE_PROJECT_ROLE,
            ],
        },
        RS_ORGANIZATION: {
            RO_ORGANIZATION_ADMIN: [
                PM_DELETE_PROJECT,
                PM_UPDATE_PROJECT,
                PM_RETRIEVE_PROJECT,
                PM_USE_PROJECT_IN_JOB,
                PM_SYNC_PROJECT,
                PM_RETRIEVE_PROJECT_ROLE,
                PM_ADD_PROJECT_ROLE,
                PM_REMOVE_PROJECT_ROLE,
            ],
        },
        RS_PROJECT: {
            RO_PROJECT_ADMIN: [
                PM_UPDATE_PROJECT,
                PM_RETRIEVE_PROJECT,
                PM_USE_PROJECT_IN_JOB,
                PM_SYNC_PROJECT,
                PM_RETRIEVE_PROJECT_ROLE,
            ],
            RO_PROJECT_USER: [
                PM_RETRIEVE_PROJECT,
                PM_USE_PROJECT_IN_JOB,
                # wjj add
                PM_RETRIEVE_PROJECT_ROLE,
            ],
        },
    },
    RS_TEMPLATE: {
        RS_SYSTEM: {
            RO_SYSTEM_ADMIN: [
                PM_DELETE_TEMPLATE,
                PM_UPDATE_TEMPLATE,
                PM_RETRIEVE_TEMPLATE,
                PM_LAUNCH_TEMPLATE,
                PM_RETRIEVE_TEMPLATE_ROLE,
                PM_ADD_TEMPLATE_ROLE,
                PM_REMOVE_TEMPLATE_ROLE,
                PM_DELETE_JOB,
                PM_RETRIEVE_JOB,
            ],
        },
        RS_ORGANIZATION: {
            RO_ORGANIZATION_ADMIN: [
                PM_DELETE_TEMPLATE,
                PM_UPDATE_TEMPLATE,
                PM_RETRIEVE_TEMPLATE,
                PM_LAUNCH_TEMPLATE,
                PM_RETRIEVE_TEMPLATE_ROLE,
                PM_ADD_TEMPLATE_ROLE,
                PM_REMOVE_TEMPLATE_ROLE,
                PM_RETRIEVE_JOB,
            ],
        },
        RS_TEMPLATE: {
            RO_TEMPLATE_ADMIN: [
                PM_UPDATE_TEMPLATE,
                PM_RETRIEVE_TEMPLATE,
                PM_LAUNCH_TEMPLATE,
                PM_RETRIEVE_JOB,
            ],
            RO_TEMPLATE_USER: [
                PM_RETRIEVE_TEMPLATE,
                PM_LAUNCH_TEMPLATE,
                PM_RETRIEVE_JOB,
                # wjj add
                PM_RETRIEVE_TEMPLATE_ROLE,
            ],
        },
    },
}
