from django.urls import path

from . import views

app_name = 'job'

urlpatterns = [
    # 任务列表
    path('jobs/', views.jobs_view, name='jobs'),

    # 任务详情
    path('jobs/<int:job_id>/detail/', views.job_detail_view, name='job_detail'),

    # 删除任务
    path('jobs/ajax/delete/', views.job_delete_view, name='job_delete'),

    # 回调更新任务信息
    path('remote_update/<int:job_id>/', views.jobs_remote_update_view, name='remote_update'),
]


