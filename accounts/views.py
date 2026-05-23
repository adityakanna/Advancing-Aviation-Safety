from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, SensorDevice
from .forms import UserLoginForm, UserRegistrationForm, SensorDeviceForm


def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        # Redirect based on user type
        if request.user.user_type == 'admin' or request.user.is_staff:
            return redirect('administration:admin_dashboard')
        else:
            return redirect('monitoring:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                
                # Redirect based on user type
                if user.user_type == 'admin' or user.is_staff or user.is_superuser:
                    return redirect('administration:admin_dashboard')
                else:
                    return redirect('monitoring:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def user_profile(request):
    """User profile view"""
    user = request.user
    
    # Get user's devices if pilot
    devices = None
    if user.user_type == 'pilot':
        devices = SensorDevice.objects.filter(assigned_to=user)
    
    context = {
        'user': user,
        'devices': devices
    }
    
    return render(request, 'accounts/profile.html', context)


# ============================================
# DEVICE MANAGEMENT VIEWS (ADMIN ONLY)
# ============================================

@login_required
def device_management(request):
    """Device management page - ADMIN ONLY"""
    user = request.user
    
    # Check admin privileges
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('accounts:login')
    
    devices = SensorDevice.objects.all().select_related('assigned_to').order_by('-created_at')
    
    context = {
        'devices': devices
    }
    
    return render(request, 'accounts/device_management.html', context)


@login_required
def add_device(request):
    """Add new sensor device"""
    user = request.user
    
    # Check admin privileges
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        form = SensorDeviceForm(request.POST)
        if form.is_valid():
            device = form.save()
            messages.success(request, f'Device {device.device_id} added successfully!')
            return redirect('accounts:device_management')
    else:
        form = SensorDeviceForm()
    
    context = {
        'form': form
    }
    
    return render(request, 'accounts/add_device.html', context)


@login_required
def edit_device(request, device_id):
    """Edit sensor device"""
    user = request.user
    
    # Check admin privileges
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('accounts:login')
    
    device = get_object_or_404(SensorDevice, id=device_id)
    
    if request.method == 'POST':
        form = SensorDeviceForm(request.POST, instance=device)
        if form.is_valid():
            device = form.save()
            messages.success(request, f'Device {device.device_id} updated successfully!')
            return redirect('accounts:device_management')
    else:
        form = SensorDeviceForm(instance=device)
    
    context = {
        'form': form,
        'device': device
    }
    
    return render(request, 'accounts/edit_device.html', context)


@login_required
def delete_device(request, device_id):
    """Delete sensor device"""
    user = request.user
    
    # Check admin privileges
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('accounts:login')
    
    device = get_object_or_404(SensorDevice, id=device_id)
    device_id_str = device.device_id
    device.delete()
    
    messages.success(request, f'Device {device_id_str} deleted successfully!')
    return redirect('accounts:device_management')


@login_required
def toggle_device_status(request, device_id):
    """Toggle device active status"""
    user = request.user
    
    # Check admin privileges
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('accounts:login')
    
    device = get_object_or_404(SensorDevice, id=device_id)
    device.is_active = not device.is_active
    device.save()
    
    status = 'activated' if device.is_active else 'deactivated'
    messages.success(request, f'Device {device.device_id} {status}.')
    
    return redirect('accounts:device_management')


# ============================================
# USER MANAGEMENT VIEWS (Optional - for future use)
# ============================================

def register(request):
    """User registration view - For pilot registration"""
    # Allow admin users to register pilots, but prevent regular users from accessing after login
    if request.user.is_authenticated and request.user.user_type != 'admin' and not request.user.is_staff:
        messages.info(request, 'You are already logged in.')
        return redirect('monitoring:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user_type = form.cleaned_data.get('user_type')
            
            # Prevent admin registration through public endpoint
            if user_type == 'admin':
                print('admin cannot register new user')
                messages.error(request, 'Admin accounts must be created by system administrators only.')
                form.add_error('user_type', 'Admin registration is not allowed through this form')
            else:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()
                
                messages.success(request, f'Registration successful! Welcome {user.get_full_name()}, please login.')
                return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})
