from django.urls import path
from . import views

app_name = 'user'
urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    # 用户列表
    path('users/', views.users_view, name='users'),
    # 用户详情
    path('users/<int:target_user_id>/detail/', views.user_detail_view, name='user_detail'),
    # 用户组织
    path('users/<int:target_user_id>/organization/', views.user_organization_view, name='user_organization'),
    # 用户团队
    path('users/<int:target_user_id>/team/', views.user_team_view, name='user_team'),
    # 用户角色
    path('users/<int:target_user_id>/role/', views.user_role_view, name='user_role'),
    # 添加用户角色
    path('users/<int:target_user_id>/role/add/', views.user_role_add_view, name='user_role_add'),
    # 删除用户角色
    path('users/ajax/role/remove/', views.user_role_remove_view, name='user_role_remove'),
]
