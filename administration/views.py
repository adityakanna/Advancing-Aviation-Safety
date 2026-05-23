from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import SystemConfiguration, AlertThreshold, AuditLog, SystemBackup
from .forms import AlertThresholdForm, SystemConfigurationForm
from accounts.models import User, SensorDevice
from monitoring.models import MonitoringSession, Alert
from analytics.models import MLModel, SessionReport


@login_required
def admin_dashboard(request):
    """
    Admin dashboard - ONLY accessible to admin users
    Fixed: No redirect loop
    """
    user = request.user
    
    # Check admin privileges - redirect to LOGIN if not admin (NOT to monitoring dashboard)
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('accounts:login')  # ← Fixed: Redirect to login, not monitoring
    
    # System statistics
    total_users = User.objects.filter(user_type='pilot').count()
    active_pilots = User.objects.filter(user_type='pilot', is_active_pilot=True).count()
    total_devices = SensorDevice.objects.count()
    active_devices = SensorDevice.objects.filter(is_active=True).count()
    
    # Session statistics
    total_sessions = MonitoringSession.objects.count()
    active_sessions = MonitoringSession.objects.filter(status='active').count()
    
    # Recent sessions
    recent_sessions = MonitoringSession.objects.all().select_related('pilot').order_by('-start_time')[:10]
    
    # Alert statistics (last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_alerts = Alert.objects.filter(timestamp__gte=seven_days_ago)
    total_alerts_7d = recent_alerts.count()
    critical_alerts_7d = recent_alerts.filter(severity='critical').count()
    
    # Model statistics
    active_models = MLModel.objects.filter(status='active').count()
    
    # Recent audit logs
    recent_logs = AuditLog.objects.all().select_related('user').order_by('-timestamp')[:15]
    
    context = {
        'total_users': total_users,
        'active_pilots': active_pilots,
        'total_devices': total_devices,
        'active_devices': active_devices,
        'total_sessions': total_sessions,
        'active_sessions': active_sessions,
        'recent_sessions': recent_sessions,
        'total_alerts_7d': total_alerts_7d,
        'critical_alerts_7d': critical_alerts_7d,
        'active_models': active_models,
        'recent_logs': recent_logs,
    }
    
    return render(request, 'administration/admin_dashboard.html', context)


@login_required
def user_management(request):
    """User management page"""
    user = request.user
    
    # Check admin privileges
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('accounts:login')
    
    users = User.objects.all().order_by('-date_joined')
    
    context = {
        'users': users
    }
    
    return render(request, 'administration/user_management.html', context)


@login_required
def toggle_user_status(request, user_id):
    """Toggle pilot active status"""
    current_user = request.user
    
    # Check admin privileges
    if current_user.user_type != 'admin' and not current_user.is_staff and not current_user.is_superuser:
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('accounts:login')
    
    user = get_object_or_404(User, id=user_id)
    
    if user.user_type == 'pilot':
        user.is_active_pilot = not user.is_active_pilot
        user.save()
        
        status = 'activated' if user.is_active_pilot else 'deactivated'
        
        # Log action
        AuditLog.objects.create(
            user=current_user,
            action='update',
            entity_type='User',
            entity_id=user.id,
            description=f'{status.capitalize()} user {user.get_full_name()}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'User {user.get_full_name()} {status}.')
    
    return redirect('administration:user_management')


@login_required
def alert_configuration(request):
    """Alert threshold configuration page"""
    user = request.user
    
    # Check admin privileges
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('accounts:login')
    
    thresholds = AlertThreshold.objects.all()
    
    # Create default thresholds if they don't exist
    default_thresholds = {
        'fatigue': {'warning': 0.6, 'critical': 0.75},
        'stress': {'warning': 0.65, 'critical': 0.8},
        'attention': {'warning': 0.4, 'critical': 0.25},
        'workload': {'warning': 0.7, 'critical': 0.85},
    }
    
    for metric, values in default_thresholds.items():
        if not AlertThreshold.objects.filter(metric_name=metric).exists():
            AlertThreshold.objects.create(
                metric_name=metric,
                warning_threshold=values['warning'],
                critical_threshold=values['critical'],
                enabled=True,
                updated_by=user
            )
    
    thresholds = AlertThreshold.objects.all()
    
    context = {
        'thresholds': thresholds
    }
    
    return render(request, 'administration/alert_configuration.html', context)


@login_required
def edit_threshold(request, threshold_id):
    """Edit alert threshold"""
    user = request.user
    
    # Check admin privileges
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('accounts:login')
    
    threshold = get_object_or_404(AlertThreshold, id=threshold_id)
    
    if request.method == 'POST':
        form = AlertThresholdForm(request.POST, instance=threshold)
        if form.is_valid():
            threshold = form.save(commit=False)
            threshold.updated_by = user
            threshold.save()
            
            # Log action
            AuditLog.objects.create(
                user=user,
                action='update',
                entity_type='AlertThreshold',
                entity_id=threshold.id,
                description=f'Updated alert threshold for {threshold.get_metric_name_display()}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Alert threshold updated successfully!')
            return redirect('administration:alert_configuration')
    else:
        form = AlertThresholdForm(instance=threshold)
    
    context = {
        'form': form,
        'threshold': threshold
    }
    
    return render(request, 'administration/edit_threshold.html', context)


@login_required
def system_configuration(request):
    """System configuration management"""
    user = request.user
    
    # Check admin privileges
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('accounts:login')
    
    configurations = SystemConfiguration.objects.all().order_by('key')
    
    context = {
        'configurations': configurations
    }
    
    return render(request, 'administration/system_configuration.html', context)


@login_required
def add_configuration(request):
    """Add new system configuration"""
    user = request.user
    
    # Check admin privileges
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        form = SystemConfigurationForm(request.POST)
        if form.is_valid():
            config = form.save(commit=False)
            config.updated_by = user
            config.save()
            
            # Log action
            AuditLog.objects.create(
                user=user,
                action='create',
                entity_type='SystemConfiguration',
                entity_id=config.id,
                description=f'Added configuration {config.key}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Configuration added successfully!')
            return redirect('administration:system_configuration')
    else:
        form = SystemConfigurationForm()
    
    context = {
        'form': form
    }
    
    return render(request, 'administration/add_configuration.html', context)


@login_required
def edit_configuration(request, config_id):
    """Edit system configuration"""
    user = request.user
    
    # Check admin privileges
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('accounts:login')
    
    config = get_object_or_404(SystemConfiguration, id=config_id)
    
    if request.method == 'POST':
        form = SystemConfigurationForm(request.POST, instance=config)
        if form.is_valid():
            config = form.save(commit=False)
            config.updated_by = user
            config.save()
            
            # Log action
            AuditLog.objects.create(
                user=user,
                action='update',
                entity_type='SystemConfiguration',
                entity_id=config.id,
                description=f'Updated configuration {config.key}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Configuration updated successfully!')
            return redirect('administration:system_configuration')
    else:
        form = SystemConfigurationForm(instance=config)
    
    context = {
        'form': form,
        'config': config
    }
    
    return render(request, 'administration/edit_configuration.html', context)


@login_required
def delete_configuration(request, config_id):
    """Delete system configuration"""
    user = request.user
    
    # Check admin privileges
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('accounts:login')
    
    config = get_object_or_404(SystemConfiguration, id=config_id)
    config_key = config.key
    
    # Log action before deleting
    AuditLog.objects.create(
        user=user,
        action='delete',
        entity_type='SystemConfiguration',
        entity_id=config.id,
        description=f'Deleted configuration {config_key}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    config.delete()
    
    messages.success(request, f'Configuration {config_key} deleted successfully!')
    return redirect('administration:system_configuration')


@login_required
def audit_logs(request):
    """View audit logs"""
    user = request.user
    
    # Check admin privileges
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('accounts:login')
    
    logs = AuditLog.objects.all().select_related('user').order_by('-timestamp')[:100]
    
    context = {
        'logs': logs
    }
    
    return render(request, 'administration/audit_logs.html', context)


@login_required
def system_reports(request):
    """Generate system reports"""
    user = request.user
    
    # Check admin privileges
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('accounts:login')
    
    # User statistics
    total_pilots = User.objects.filter(user_type='pilot').count()
    active_pilots = User.objects.filter(user_type='pilot', is_active_pilot=True).count()
    
    # Session statistics
    total_sessions = MonitoringSession.objects.count()
    completed_sessions = MonitoringSession.objects.filter(status='completed').count()
    active_sessions = MonitoringSession.objects.filter(status='active').count()
    
    # Alert statistics
    total_alerts = Alert.objects.count()
    critical_alerts = Alert.objects.filter(severity='critical').count()
    warning_alerts = Alert.objects.filter(severity='warning').count()
    
    # Performance statistics
    reports = SessionReport.objects.all()
    
    if reports.exists():
        avg_performance_stats = reports.aggregate(
            avg_fatigue=Avg('avg_fatigue'),
            avg_stress=Avg('avg_stress'),
            avg_attention=Avg('avg_attention'),
            avg_workload=Avg('avg_workload'),
        )
        
        performance_distribution = reports.values('overall_performance').annotate(count=Count('id'))
    else:
        avg_performance_stats = None
        performance_distribution = None
    
    context = {
        'total_pilots': total_pilots,
        'active_pilots': active_pilots,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'active_sessions': active_sessions,
        'total_alerts': total_alerts,
        'critical_alerts': critical_alerts,
        'warning_alerts': warning_alerts,
        'avg_performance_stats': avg_performance_stats,
        'performance_distribution': performance_distribution,
    }
    
    return render(request, 'administration/system_reports.html', context)
