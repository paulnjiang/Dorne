from django.urls import path

from . import views


app_name = 'inventory'


urlpatterns = [
    # 列出所有仓库
    path('', views.inventories_view, name='inventories'),

    # 查看仓库详情
    path('<int:inventory_id>/', views.inventory_detail_view, name='inventory_detail'),

    ################################
    # 列出所有用户/团队的所有角色
    path('<int:inventory_id>/roles/', views.inventory_roles_view, name='inventory_roles'),

    # 添加用户/团队角色
    path('<int:inventory_id>/roles/add/', views.inventory_roles_add_view, name='inventory_roles_add'),

    # 移除用户/团队角色
    path('<int:inventory_id>/roles/remove/', views.inventory_roles_remove_view, name='inventory_roles_remove'),

    ################################ API接口 ################################
    # 列出所有仓库
    path('api/inventories/', views.api_inventories_view, name='api_inventories'),

    # 新建仓库
    path('api/inventories/create/', views.api_inventory_create_view, name='api_inventory_create'),

    # 删除仓库
    path('api/inventories/delete/', views.api_inventory_delete_view, name='api_inventory_delete'),

    # 修改仓库
    path('api/inventories/<int:inventory_id>/edit/', views.api_inventory_edit_view, name='api_inventory_edit'),

    # 列出仓库中所有主机
    path('api/inventories/<int:inventory_id>/hosts/', views.api_inventory_hosts_view, name='api_inventory_hosts'),

    # 新建主机
    path('api/hosts/create/', views.api_host_create_view, name='api_host_create'),

    # 查看主机详情
    path('api/hosts/<int:host_id>/', views.api_host_detail_view, name='api_host_detail'),

    # 修改主机
    path('api/hosts/<int:host_id>/edit/', views.api_host_edit_view, name='api_host_edit'),

    # 删除主机
    path('api/hosts/delete/', views.api_host_delete_view, name='api_host_delete'),

    # 列出仓库中所有组
    path('api/inventories/<int:inventory_id>/groups/', views.api_inventory_groups_view, name='api_inventory_groups'),

    # 新建组
    path('api/groups/create/', views.api_group_create_view, name='api_group_create'),

    # 查看组详情
    path('api/groups/<int:group_id>/', views.api_group_detail_view, name='api_group_detail'),

    # 修改组
    path('api/groups/<int:group_id>/edit/', views.api_group_edit_view, name='api_group_edit'),

    # 删除组
    path('api/groups/delete/', views.api_group_delete_view, name='api_group_delete'),

    # 将主机加入组
    path('api/add_host_into_group/', views.api_add_host_into_group_view, name='api_add_host_into_group'),

    # 将主机移出组
    path('api/remove_host_from_group/', views.api_remove_host_from_group_view, name='api_remove_host_from_group'),

    # 将组加入组
    path('api/add_group_into_group/', views.api_add_group_into_group_view, name='api_add_group_into_group'),

    # 将组移出组
    path('api/remove_group_from_group/', views.api_remove_group_from_group_view, name='api_remove_group_from_group'),
]
