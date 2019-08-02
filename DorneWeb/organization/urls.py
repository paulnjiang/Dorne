from django.urls import path

from . import views

app_name = 'organization'

urlpatterns = [
    # 列出所有组织
    path('list/', views.organizations_view, name='organizations'),
    # 新建组织
    path('create/', views.organizations_create_view, name='organizations_create'),
    # 删除组织
    path('ajax/organization/<int:organization_id>/delete/', views.organization_delete_view, name='organization_delete'),
    # 组织角色
    path('ajax/organization/<int:organization_id>/role/', views.organization_role_view, name='organization_role'),
    # 组织详细信息
    path('<int:organization_id>/detail/', views.organization_detail_view, name='organization_detail'),

    # ========组织用户相关
    # 组织内用户
    path('<int:organization_id>/user/', views.organization_user_view, name='organization_user'),
    # 向组织内新加用户
    path('<int:organization_id>/user/add/', views.organization_user_add_view, name='organization_user_add'),

    # 移除组织用户的角色
    path('ajax/user/role/remove/', views.organization_user_role_remove_view, name='organization_user_role_remove'),

    # ========组织团队相关
    # 组织内团队
    path('<int:organization_id>/team/', views.organization_team_view, name='organization_team'),
    # 团队详情
    path('team/info/<int:team_id>/detail/', views.team_info_detail_view, name='team_info_detail'),
    # 团队内用户
    path('team/info/<int:team_id>/user/', views.team_info_user_view, name='team_info_user'),
    # 向团队内添加用户
    path('team/info/<int:team_id>/user/add/', views.team_info_user_add_view, name='team_info_user_add'),
    # 团队在资源上的角色
    path('team/info/<int:team_id>/role/', views.team_info_role_view, name='team_info_role'),
    # 向团队内添加角色
    path('team/info/<int:team_id>/role/add/', views.team_info_role_add_view, name='team_info_role_add'),
    # 删除团队在资源上的角色
    path('ajax/team/role/remove/', views.team_info_role_remove_view, name='team_info_role_remove_view'),
    # 组织内新建团队
    path('<int:organization_id>/team/create/', views.organization_team_create_view, name='organization_team_create'),
    # 团队角色
    path('ajax/team/<int:team_id>/role/', views.team_role_view, name='team_role'),
    # 删除组织
    path('ajax/team/<int:team_id>/delete/', views.team_delete_view, name='team_delete'),


    # ========组织仓库相关
    # 组织内仓库
    path('<int:organization_id>/inventory/', views.organization_inventory_view, name='organization_inventory'),

    # ========组织项目相关
    # 组织内项目
    path('<int:organization_id>/project/', views.organization_project_view, name='organization_project'),

    # ========组织模板相关
    # 组织内模板
    path('<int:organization_id>/template/', views.organization_template_view, name='organization_template'),



]
