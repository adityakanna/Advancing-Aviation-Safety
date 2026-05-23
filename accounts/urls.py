from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('', views.user_login, name='login'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('register/', views.register, name='register'),
    
    # Device Management (Admin only)
    path('devices/', views.device_management, name='device_management'),
    path('devices/add/', views.add_device, name='add_device'),
    path('devices/<int:device_id>/edit/', views.edit_device, name='edit_device'),
    path('devices/<int:device_id>/delete/', views.delete_device, name='delete_device'),
    path('devices/<int:device_id>/toggle/', views.toggle_device_status, name='toggle_device_status'),
]
