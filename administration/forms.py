from django import forms
from .models import AlertThreshold, SystemConfiguration

class AlertThresholdForm(forms.ModelForm):
    class Meta:
        model = AlertThreshold
        fields = ['metric_name', 'warning_threshold', 'critical_threshold', 'enabled']
        widgets = {
            'metric_name': forms.Select(attrs={'class': 'form-select'}),
            'warning_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '1'
            }),
            'critical_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '1'
            }),
            'enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class SystemConfigurationForm(forms.ModelForm):
    class Meta:
        model = SystemConfiguration
        fields = ['key', 'value', 'description', 'data_type']
        widgets = {
            'key': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Configuration Key'
            }),
            'value': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Configuration Value'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Description'
            }),
            'data_type': forms.Select(attrs={'class': 'form-select'}),
        }
