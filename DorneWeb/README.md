# 资源类型规定
- RS_GLOBAL = 10
- RS_ORGANIZATION = 20
- RS_INVENTORY = 30
- RS_PROJECT = 40
- RS_TEMPLATE = 50



# 角色类型规定
- RO_GLOBAL_ADMIN = 1000
- RO_ORGANIZATION_ADMIN = 1000
- RO_INVENTORY_USE = 100
- RO_INVENTORY_ADMIN = 1000
- RO_PROJECT_USE = 100
- RO_PROJECT_ADMIN = 1000
- RO_TEMPLATE_USE = 100
- RO_TEMPLATE_ADMIN = 1000

```json
{
    RS_GLOBAL: {
        RO_GLOBAL_ADMIN: 1000,
    },
    RS_ORGANIZATION: {
        RO_ORGANIZATION_ADMIN: 1000,
    },
    RS_INVENTORY: {
        RO_INVENTORY_USE: 100,
        RO_INVENTORY_ADMIN: 1000,
    },
    RS_PROJECT: {
        RO_PROJECT_USE: 100,
        RO_PROJECT_ADMIN: 1000,
    },
    RS_TEMPLATE: {
        RO_TEMPLATE_USE: 100,
        RO_TEMPLATE_ADMIN: 1000,
    }
}
```

# 错误信息状态码与内容

    1000: 'OK',

    1100: '参数错误',
    1101: '期待一个字典型参数',
    1102: '字典参数缺少必要字段',

    1200: '权限错误',
    1201: '您需要权限来执行此操作',
    1202: '您不在任何团队中',

    1300: '内部错误',
    1301: '未实现',

# 一些约定
- 如果一个用户既不是最高管理员也不是组织管理员，那他就\***必须**\*属于一个团队！万一他不属于一个团队，那他的页面就是一片空白。
- 功能性函数（如RoleManager下的所有函数）只能被api直接调用，不能被views直接调用。而且这些函数里不处理非必要异常（举一个必要异常的例子：UAC.objects.filter(...).first，如果抛出NotExist我们才能断定没有记录，所以NotExist是必要异常），而是全交给api处理。

# 共识
1. 所有api，入参时直接把触发这个api的user对象传入
2. Project、Inventory、Host、Group、JobTemplate、Job、Team、Organization这些资源都暂时不支持删除
3. **尽量考虑所有一切触发api的场景，加上所有有必要的判断**
4. 对RoleManager的使用：只能被api使用，view里不能使用。规定api中一切获取用户角色的操作都通过get_user_roles完成，api中一切获取团队角色的操作都通过get_team_roles完成，api中所有获取资源列表的操作都通过get_resources完成
5. UserAndTeamRole模块的使用：直接在基类里实现，其他所有继承类都不用自己实现。所有增加、删除、查看用户角色的场景都调用UserAndTeamRole模块。要注意，这里是指一个用户要操作**别的用户**的角色
6. 有时系统也需要查询调用api的用户的权限，但是views又不能直接调用RoleManager，那怎么办呢？解决办法就是新建一个UserAndTeamRoleInternalAPI类，专门用户系统查询用户权限
7. 超级管理员和组织管理员不需要有team，但是平民必须要有team
8. 关于用户能否查看当前view，需要判断角色，这个统一放到views里判断
9. 所有api都改成staticmethod
10. 所有API在status是True的时候不用返回errmsg
11. 判断用户是否有团队都放在views判断
12. 任何用户都可以进入到创建模板页面（除了没有团队的用户）





# ansible result
```json
{
	"fatal": "",
	"host_ok": {},
	"host_unreachable": {
		"3001.abc": {
			"msg": "Failed to connect to the host via ssh: ssh: connect to host 10.10.0.1 port 22: Connection timed out\r\n",
			"unreachable": true,
			"changed": false
		},
		"3002.abc": {
			"msg": "Failed to connect to the host via ssh: ssh: connect to host 10.10.0.2 port 22: Connection timed out\r\n",
			"unreachable": true,
			"changed": false
		},
		"asdfsad": {
			"msg": "Failed to connect to the host via ssh: Host key verification failed.\r\n",
			"unreachable": true,
			"changed": false
		}
	},
	"host_failed": {}
}

{
	"fatal": "",
	"host_ok": {},
	"host_unreachable": {},
	"host_failed": {
		"127.0.0.1": {
			"_ansible_parsed": true,
			"cmd": ["/usr/bin/git", "fetch", "--tags", "origin"],
			"_ansible_no_log": false,
			"invocation": {
				"module_args": {
					"force": false,
					"track_submodules": false,
					"reference": null,
					"dest": "/home/dev/dorne_data/projects/1",
					"umask": null,
					"clone": true,
					"update": true,
					"ssh_opts": null,
					"repo": "https://zhangsan:123123123123123@code.abc.com/Sothoryos/monitor_playbook.git",
					"bare": false,
					"verify_commit": false,
					"archive": null,
					"recursive": true,
					"executable": null,
					"remote": "origin",
					"refspec": null,
					"separate_git_dir": null,
					"accept_hostkey": false,
					"depth": null,
					"version": "master",
					"key_file": null
				}
			},
			"changed": false,
			"msg": "Failed to download remote objects and refs:  remote: HTTP Basic: Access denied\nfatal: Authentication failed for 'https://zhangsan:123123123123123@code.abc.com/Sothoryos/monitor_playbook.git/'\n"
		}
	}
}
```