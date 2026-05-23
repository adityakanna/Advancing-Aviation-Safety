from django.contrib import admin
from .models import MonitoringSession, SensorReading, MentalStateAssessment, Alert

@admin.register(MonitoringSession)
class MonitoringSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'pilot', 'session_type', 'status', 'start_time', 'duration_minutes']
    list_filter = ['status', 'session_type', 'start_time']
    search_fields = ['pilot__username', 'pilot__first_name', 'pilot__last_name', 'flight_number']
    raw_id_fields = ['pilot']
    date_hierarchy = 'start_time'

@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'device', 'timestamp']
    list_filter = ['device__device_type', 'timestamp']
    raw_id_fields = ['session', 'device']
    date_hierarchy = 'timestamp'

@admin.register(MentalStateAssessment)
class MentalStateAssessmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'timestamp', 'fatigue_score', 'stress_score', 
                   'attention_score', 'workload_score', 'overall_risk']
    list_filter = ['overall_risk', 'timestamp', 'alert_triggered']
    raw_id_fields = ['session']
    date_hierarchy = 'timestamp'

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'severity', 'alert_type', 'timestamp', 'acknowledged']
    list_filter = ['severity', 'alert_type', 'acknowledged', 'timestamp']
    search_fields = ['message']
    raw_id_fields = ['session', 'assessment']
    date_hierarchy = 'timestamp'
