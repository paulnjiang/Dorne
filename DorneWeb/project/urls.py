from django.urls import path

from . import views

app_name = 'project'

urlpatterns = [
    # 列出项目
    path('projects/', views.projects_view, name='projects'),

    # 新建项目
    path('projects/create/', views.project_create_view, name='project_create'),

    # 项目详情
    path('projects/<int:project_id>/', views.project_detail_view, name='project_detail'),

    # 修改项目
    path('projects/<int:project_id>/edit/', views.project_edit_view, name='project_edit'),

    # 删除项目
    path('projects/ajax/<int:project_id>/delete/', views.project_delete_view, name='project_delete'),

    ##############
    # 列出所有用户/团队的所有角色
    path('projects/<int:project_id>/roles/', views.project_roles_view, name='project_roles'),

    # 添加用户/团队角色
    path('projects/<int:project_id>/roles/add/', views.project_roles_add_view, name='project_roles_add'),

    # 移除用户/团队角色
    path('projects/ajax/<int:project_id>/roles/remove/', views.project_roles_remove_view, name='project_roles_remove'),

    # 同步项目
    path('projects/ajax/<int:project_id>/sync/', views.project_sync_view, name='project_sync'),

    # 列出所有任务模板
    path('templates/', views.templates_view, name='templates'),

    # 新建任务模板
    path('templates/create/', views.template_create_view, name='template_create'),

    # 查看任务模板详情
    path('templates/<int:template_id>/', views.template_detail_view, name='template_detail'),

    # 修改任务模板
    path('templates/<int:template_id>/edit/', views.template_edit_view, name='template_edit'),

    # 删除任务模板
    path('templates/<int:template_id>/delete/', views.template_delete_view, name='template_delete'),

    # 发射任务模板
    path('templates/<int:template_id>/launch/', views.template_launch_view, name='template_launch'),

    ################################
    # 列出所有用户/团队的所有角色
    path('templates/<int:template_id>/roles/', views.template_roles_view, name='template_roles'),

    # 添加用户/团队角色
    path('templates/<int:template_id>/roles/add/', views.template_roles_add_view, name='template_roles_add'),

    # 移除用户/团队角色
    path('templates/<int:template_id>/roles/remove/', views.template_roles_remove_view, name='template_roles_remove'),
]
