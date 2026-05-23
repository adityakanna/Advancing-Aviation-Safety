from django.db import models
from accounts.models import User
from django.utils import timezone

class MLModel(models.Model):
    MODEL_TYPE_CHOICES = (
        ('fatigue', 'Fatigue Detection'),
        ('stress', 'Stress Detection'),
        ('attention', 'Attention Detection'),
        ('workload', 'Workload Detection'),
    )
    
    STATUS_CHOICES = (
        ('training', 'Training'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    )
    
    name = models.CharField(max_length=200)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPE_CHOICES)
    version = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='training')
    algorithm = models.CharField(max_length=100)
    model_file = models.FileField(upload_to='ml_models/')
    scaler_file = models.FileField(upload_to='ml_models/', null=True, blank=True)
    
    # Performance Metrics
    accuracy = models.FloatField(null=True, blank=True)
    precision = models.FloatField(null=True, blank=True)
    recall = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    
    training_samples = models.IntegerField(default=0)
    training_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ml_models'
        ordering = ['-created_at']
        unique_together = ['model_type', 'version']
    
    def __str__(self):
        return f"{self.name} - v{self.version} ({self.status})"


class TrainingDataset(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    file_path = models.FileField(upload_to='datasets/')
    total_samples = models.IntegerField(default=0)
    feature_count = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'training_datasets'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.total_samples} samples)"


class SessionReport(models.Model):
    session = models.OneToOneField('monitoring.MonitoringSession', on_delete=models.CASCADE, related_name='report')
    generated_at = models.DateTimeField(auto_now_add=True)
    
    # Summary Statistics
    avg_fatigue = models.FloatField()
    avg_stress = models.FloatField()
    avg_attention = models.FloatField()
    avg_workload = models.FloatField()
    
    max_fatigue = models.FloatField()
    max_stress = models.FloatField()
    min_attention = models.FloatField()
    max_workload = models.FloatField()
    
    total_alerts = models.IntegerField(default=0)
    critical_alerts = models.IntegerField(default=0)
    
    # Performance Rating
    overall_performance = models.CharField(max_length=20, choices=(
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ))
    
    recommendations = models.TextField()
    report_file = models.FileField(upload_to='reports/', null=True, blank=True)
    
    class Meta:
        db_table = 'session_reports'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"Report - Session {self.session.id} - {self.session.pilot.get_full_name()}"
