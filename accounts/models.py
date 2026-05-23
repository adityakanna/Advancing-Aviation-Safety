from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('pilot', 'Pilot'),
        ('admin', 'Administrator'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='pilot')
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    total_flight_hours = models.IntegerField(default=0)
    is_active_pilot = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.employee_id})"
    
    def is_pilot(self):
        return self.user_type == 'pilot'
    
    def is_admin(self):
        return self.user_type == 'admin'


class SensorDevice(models.Model):
    DEVICE_TYPE_CHOICES = (
        ('eeg', 'EEG Sensor'),
        ('ecg', 'ECG Sensor'),
        ('eye_tracker', 'Eye Tracker'),
    )
    
    device_id = models.CharField(max_length=100, unique=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE_CHOICES)
    manufacturer = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='devices')
    is_active = models.BooleanField(default=True)
    last_calibration = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sensor_devices'
        ordering = ['device_type', 'device_id']
    
    def __str__(self):
        return f"{self.get_device_type_display()} - {self.device_id}"
