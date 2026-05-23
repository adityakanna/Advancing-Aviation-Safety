from django.db import models
from accounts.models import User, SensorDevice
from django.utils import timezone

class MonitoringSession(models.Model):
    SESSION_TYPE_CHOICES = (
        ('flight', 'Real Flight'),
        ('simulator', 'Simulator'),
        ('training', 'Training'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('aborted', 'Aborted'),
    )
    
    pilot = models.ForeignKey(User, on_delete=models.CASCADE, related_name='monitoring_sessions')
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)
    aircraft_type = models.CharField(max_length=100, blank=True)
    flight_number = models.CharField(max_length=50, blank=True)
    route = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'monitoring_sessions'
        ordering = ['-start_time']
    
    def __str__(self):
        return f"Session {self.id} - {self.pilot.get_full_name()} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    def calculate_duration(self):
        if self.end_time:
            delta = self.end_time - self.start_time
            self.duration_minutes = int(delta.total_seconds() / 60)
            self.save()


class SensorReading(models.Model):
    session = models.ForeignKey(MonitoringSession, on_delete=models.CASCADE, related_name='sensor_readings')
    device = models.ForeignKey(SensorDevice, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    
    # EEG Data (8 channels)
    eeg_channel_1 = models.FloatField(null=True, blank=True)
    eeg_channel_2 = models.FloatField(null=True, blank=True)
    eeg_channel_3 = models.FloatField(null=True, blank=True)
    eeg_channel_4 = models.FloatField(null=True, blank=True)
    eeg_channel_5 = models.FloatField(null=True, blank=True)
    eeg_channel_6 = models.FloatField(null=True, blank=True)
    eeg_channel_7 = models.FloatField(null=True, blank=True)
    eeg_channel_8 = models.FloatField(null=True, blank=True)
    
    # ECG Data
    ecg_heart_rate = models.FloatField(null=True, blank=True)
    ecg_hrv = models.FloatField(null=True, blank=True)  # Heart Rate Variability
    ecg_rr_interval = models.FloatField(null=True, blank=True)
    
    # Eye Tracking Data
    eye_blink_rate = models.FloatField(null=True, blank=True)
    eye_fixation_duration = models.FloatField(null=True, blank=True)
    eye_saccade_velocity = models.FloatField(null=True, blank=True)
    pupil_diameter = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'sensor_readings'
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
        ]
    
    def __str__(self):
        return f"Reading - {self.device.device_type} - {self.timestamp.strftime('%H:%M:%S')}"


class MentalStateAssessment(models.Model):
    session = models.ForeignKey(MonitoringSession, on_delete=models.CASCADE, related_name='assessments')
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Mental State Scores (0-1 range)
    fatigue_score = models.FloatField()
    stress_score = models.FloatField()
    attention_score = models.FloatField()
    workload_score = models.FloatField()
    
    # Overall risk assessment
    overall_risk = models.CharField(max_length=20, choices=(
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ))
    
    # Alert triggered
    alert_triggered = models.BooleanField(default=False)
    alert_type = models.CharField(max_length=50, blank=True)
    alert_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'mental_state_assessments'
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
        ]
    
    def __str__(self):
        return f"Assessment - {self.session.pilot.get_full_name()} - {self.overall_risk}"


class Alert(models.Model):
    SEVERITY_CHOICES = (
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    )
    
    session = models.ForeignKey(MonitoringSession, on_delete=models.CASCADE, related_name='alerts')
    assessment = models.ForeignKey(MentalStateAssessment, on_delete=models.CASCADE, related_name='alert_details')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    alert_type = models.CharField(max_length=50)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'alerts'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.get_severity_display()} - {self.alert_type} - {self.timestamp.strftime('%H:%M:%S')}"
