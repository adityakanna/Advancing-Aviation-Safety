from django.contrib import admin
from .models import MLModel, TrainingDataset, SessionReport

@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_type', 'version', 'status', 'algorithm', 'accuracy', 'training_date']
    list_filter = ['status', 'model_type', 'algorithm', 'training_date']
    search_fields = ['name', 'version']
    raw_id_fields = ['created_by']
    date_hierarchy = 'training_date'

@admin.register(TrainingDataset)
class TrainingDatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_samples', 'feature_count', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    raw_id_fields = ['created_by']
    date_hierarchy = 'created_at'

@admin.register(SessionReport)
class SessionReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'overall_performance', 'total_alerts', 
                   'critical_alerts', 'generated_at']
    list_filter = ['overall_performance', 'generated_at']
    raw_id_fields = ['session']
    date_hierarchy = 'generated_at'
