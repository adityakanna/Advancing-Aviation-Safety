from django import forms
from .models import User, SensorDevice


class UserLoginForm(forms.Form):
    """User login form"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'required': True
        })
    )


class UserRegistrationForm(forms.ModelForm):
    """User registration form - For pilot registration only"""
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    password_confirm = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'employee_id', 'phone_number', 
                  'license_number', 'date_of_birth', 'total_flight_hours', 'user_type']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Employee ID'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'License Number'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_flight_hours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total Flight Hours', 'min': '0'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow pilot registration through this form
        # Admin accounts should be created through admin panel
        self.fields['user_type'].queryset = User.objects.filter(user_type='pilot')
        self.fields['user_type'].initial = 'pilot'
        # Make it a radio button with only pilot option
        self.fields['user_type'].widget = forms.RadioSelect(choices=[('pilot', 'Pilot')])
        
        # Make all fields except total_flight_hours optional for registration
        self.fields['phone_number'].required = False
        self.fields['license_number'].required = False
        self.fields['date_of_birth'].required = False
        self.fields['total_flight_hours'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        user_type = cleaned_data.get('user_type')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Passwords do not match')
        
        # Double-check: prevent admin registration
        if user_type == 'admin':
            raise forms.ValidationError('Admin registration is not allowed through this form. Contact system administrator.')
        
        return cleaned_data


class SensorDeviceForm(forms.ModelForm):
    """Sensor device form for adding/editing devices"""
    
    class Meta:
        model = SensorDevice
        fields = ['device_id', 'device_type', 'manufacturer', 'model_number', 'assigned_to', 'is_active']
        widgets = {
            'device_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., EEG-001'
            }),
            'device_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'manufacturer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., NeuroSky'
            }),
            'model_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., MindWave Mobile'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'device_id': 'Device ID',
            'device_type': 'Device Type',
            'manufacturer': 'Manufacturer',
            'model_number': 'Model Number',
            'assigned_to': 'Assigned To (Pilot)',
            'is_active': 'Active Status'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show pilots in the assigned_to dropdown
        self.fields['assigned_to'].queryset = User.objects.filter(user_type='pilot')
        self.fields['assigned_to'].required = False


class UserProfileForm(forms.ModelForm):
    """Form for users to update their profile"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
