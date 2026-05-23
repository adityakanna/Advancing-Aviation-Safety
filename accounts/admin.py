from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, SensorDevice

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'user_type', 'employee_id', 'is_active']
    list_filter = ['user_type', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'employee_id', 'phone_number', 'profile_picture', 
                      'date_of_birth', 'license_number', 'total_flight_hours', 'is_active_pilot')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'employee_id', 'email', 'first_name', 'last_name')
        }),
    )

@admin.register(SensorDevice)
class SensorDeviceAdmin(admin.ModelAdmin):
    list_display = ['device_id', 'device_type', 'manufacturer', 'model_number', 'assigned_to', 'is_active']
    list_filter = ['device_type', 'is_active', 'manufacturer']
    search_fields = ['device_id', 'manufacturer', 'model_number']
    raw_id_fields = ['assigned_to']
