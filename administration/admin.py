from django.contrib import admin
from .models import SystemConfiguration, AlertThreshold, AuditLog, SystemBackup

@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'data_type', 'updated_by', 'updated_at']
    list_filter = ['data_type', 'updated_at']
    search_fields = ['key', 'value', 'description']
    raw_id_fields = ['updated_by']

@admin.register(AlertThreshold)
class AlertThresholdAdmin(admin.ModelAdmin):
    list_display = ['metric_name', 'warning_threshold', 'critical_threshold', 'enabled', 'updated_at']
    list_filter = ['enabled', 'metric_name']
    raw_id_fields = ['updated_by']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'action', 'entity_type', 'timestamp', 'ip_address']
    list_filter = ['action', 'entity_type', 'timestamp']
    search_fields = ['description', 'user__username']
    raw_id_fields = ['user']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(SystemBackup)
class SystemBackupAdmin(admin.ModelAdmin):
    list_display = ['backup_name', 'backup_type', 'file_size_mb', 'created_by', 'created_at']
    list_filter = ['backup_type', 'created_at']
    search_fields = ['backup_name']
    raw_id_fields = ['created_by']
    date_hierarchy = 'created_at'
