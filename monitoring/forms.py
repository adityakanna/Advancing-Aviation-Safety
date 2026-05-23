from django import forms
from .models import MonitoringSession

class StartSessionForm(forms.ModelForm):
    session_type = forms.ChoiceField(
        choices=MonitoringSession.SESSION_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        required=True,
        label='Session Type'
    )
    
    class Meta:
        model = MonitoringSession
        fields = ['session_type', 'aircraft_type', 'flight_number', 'route', 'notes']
        widgets = {
            'session_type': forms.Select(attrs={'class': 'form-select'}),
            'aircraft_type': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Boeing 737, Airbus A320'
            }),
            'flight_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., AI101'
            }),
            'route': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Delhi to Mumbai'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Any additional notes...'
            }),
        }

class EndSessionForm(forms.Form):
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Session end notes (optional)...'
        })
    )
