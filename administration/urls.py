from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.user_management, name='user_management'),
    path('users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),
    path('alerts/', views.alert_configuration, name='alert_configuration'),
    path('alerts/<int:threshold_id>/edit/', views.edit_threshold, name='edit_threshold'),
    path('config/', views.system_configuration, name='system_configuration'),
    path('config/add/', views.add_configuration, name='add_configuration'),
    path('config/<int:config_id>/edit/', views.edit_configuration, name='edit_configuration'),
    path('config/<int:config_id>/delete/', views.delete_configuration, name='delete_configuration'),
    path('logs/', views.audit_logs, name='audit_logs'),
    path('reports/', views.system_reports, name='system_reports'),
]
