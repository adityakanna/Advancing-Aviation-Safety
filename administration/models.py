from django.db import models
from accounts.models import User
from django.utils import timezone

class SystemConfiguration(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    data_type = models.CharField(max_length=20, choices=(
        ('string', 'String'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
    ))
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_configurations'
        ordering = ['key']
    
    def __str__(self):
        return f"{self.key}: {self.value}"


class AlertThreshold(models.Model):
    METRIC_CHOICES = (
        ('fatigue', 'Fatigue'),
        ('stress', 'Stress'),
        ('attention', 'Attention'),
        ('workload', 'Workload'),
    )
    
    metric_name = models.CharField(max_length=50, choices=METRIC_CHOICES, unique=True)
    warning_threshold = models.FloatField()
    critical_threshold = models.FloatField()
    enabled = models.BooleanField(default=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'alert_thresholds'
        ordering = ['metric_name']
    
    def __str__(self):
        return f"{self.get_metric_name_display()} - Warning: {self.warning_threshold}, Critical: {self.critical_threshold}"


class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('config_change', 'Configuration Change'),
        ('model_train', 'Model Training'),
        ('alert_config', 'Alert Configuration'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=100)
    entity_id = models.IntegerField(null=True, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.entity_type} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class SystemBackup(models.Model):
    backup_name = models.CharField(max_length=200)
    backup_type = models.CharField(max_length=50, choices=(
        ('database', 'Database'),
        ('models', 'ML Models'),
        ('full', 'Full System'),
    ))
    file_path = models.FileField(upload_to='backups/')
    file_size_mb = models.FloatField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'system_backups'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.backup_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
