# Dorne2 Job Worker 

#### 部署

- 编辑 ansible.cfg 文件

```ini
# 定义输出
stdout_callback = dense
# dorne 加入 callback 白名单
callback_whitelist = httpapi
# 指定自定义callback的目录 
callback_plugins = /usr/share/ansible/plugins/callback

# 关闭 gather 让 playbook 控制
gathering = explicit
forks = 10
```

- 拷贝 plugins/callback/httpapi.py 到自定义 callback_plugins 目录

- 编辑dorne_worker.conf



#### 数据格式

> 除 extra_variables 传原始值，boolean值不变，其他都要用值都是 string

- client 发送执行playbook的任务(run_playbook)
```json
{
  "callback_url": "http://cb.host.com/job/10203",
  "inventory_file": "/data/git_home/inventory/01/hosts",
  "playbook_file": "/data/git_home/09/01/any.yml",
  "args": {
    "extra_variables": {
      "MZID": 6785,
      "HOSTNAME": "test.test",
      "target": "terrane_hosts"
    },
    "limit": "1.2.3.4",
    "forks": "10",
    "job_tags": "install, restart",
    "verbosity": "2",
    "check": false 
  }
}
```

- 同步git仓库的任务(update_repo)
```json
{
  "job_id": "123",
  "project_id": "234",
  "args": {
    "extra_variables": {
      "gituser": "zhangsan",
      "gitpassword": "1qqa2ssd",
      "giturl": "code.mzsvn.com/Sothoryos/monitor_playbook",
      "gitbranch": "master"     
    }
  }
}
```

- callback 接口格式
```json
{
  # 0 playbook正常执行
  # 1 playbook执行失败
  status: 0 | 1，
  msg: {
    error: "message" | ansible stdout
  }
  
}
```
