from django.db.models import Sum 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db.models import Avg, Max, Min, Count
from datetime import timedelta
import json
import random
import numpy as np
import joblib
import os

from .models import MonitoringSession, SensorReading, MentalStateAssessment, Alert
from .forms import StartSessionForm, EndSessionForm
from accounts.models import SensorDevice
from analytics.models import MLModel, SessionReport
from administration.models import AlertThreshold

@login_required
def dashboard(request):
    """
    Main dashboard - routes users based on their type
    NOW: Admins can also monitor
    """
    user = request.user
    
    # ============================================
    # ADMIN USERS - Show Admin Monitoring Dashboard
    # ============================================
    if user.user_type == 'admin' or user.is_staff or user.is_superuser:
        # Admin can monitor AND manage
        
        # Get active session
        active_session = MonitoringSession.objects.filter(
            pilot=user, 
            status='active'
        ).first()
        
        # Get admin's sessions
        admin_sessions = MonitoringSession.objects.filter(
            pilot=user
        ).order_by('-start_time')[:5]
        
        # Get all sessions (admin view)
        all_sessions = MonitoringSession.objects.all().count()
        
        # Get statistics
        total_sessions = MonitoringSession.objects.filter(pilot=user).count()
        total_flight_time = MonitoringSession.objects.filter(
            pilot=user, 
            status='completed'
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0
        
        recent_alerts = Alert.objects.filter(
            session__pilot=user
        ).order_by('-timestamp')[:10]
        
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_alerts_count = Alert.objects.filter(
            session__pilot=user,
            timestamp__gte=seven_days_ago
        ).count()
        
        # Get available devices
        devices = SensorDevice.objects.filter(is_active=True)
        active_devices_count = devices.count()
        
        # Admin can always monitor if devices exist
        can_start_monitoring = active_devices_count >= 3
        
        context = {
            'active_session': active_session,
            'recent_sessions': admin_sessions,
            'all_sessions_count': all_sessions,
            'total_sessions': total_sessions,
            'total_flight_time': total_flight_time,
            'recent_alerts': recent_alerts,
            'recent_alerts_count': recent_alerts_count,
            'devices': devices,
            'active_devices_count': active_devices_count,
            'can_start_monitoring': can_start_monitoring,
            'is_admin': True,
        }
        
        return render(request, 'monitoring/dashboard.html', context)
    
    # ============================================
    # PILOT USERS - Show Pilot Dashboard
    # ============================================
    elif user.user_type == 'pilot':
        # Get active session
        active_session = MonitoringSession.objects.filter(
            pilot=user, 
            status='active'
        ).first()
        
        # Get recent sessions (last 5)
        recent_sessions = MonitoringSession.objects.filter(
            pilot=user
        ).order_by('-start_time')[:5]
        
        # Get statistics
        total_sessions = MonitoringSession.objects.filter(pilot=user).count()
        
        # Calculate total flight time
        total_flight_time = MonitoringSession.objects.filter(
            pilot=user, 
            status='completed'
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0
        
        # Get recent alerts (last 10)
        recent_alerts = Alert.objects.filter(
            session__pilot=user
        ).order_by('-timestamp')[:10]
        
        # Count recent alerts (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_alerts_count = Alert.objects.filter(
            session__pilot=user,
            timestamp__gte=seven_days_ago
        ).count()
        
        # Get assigned devices
        devices = SensorDevice.objects.filter(assigned_to=user, is_active=True)
        active_devices_count = devices.count()
        
        # Check if user has minimum required devices (EEG, ECG, Eye Tracker)
        has_eeg = devices.filter(device_type='eeg').exists()
        has_ecg = devices.filter(device_type='ecg').exists()
        has_eye = devices.filter(device_type='eye_tracker').exists()
        can_start_monitoring = has_eeg and has_ecg and has_eye
        
        context = {
            'active_session': active_session,
            'recent_sessions': recent_sessions,
            'total_sessions': total_sessions,
            'total_flight_time': total_flight_time,
            'recent_alerts': recent_alerts,
            'recent_alerts_count': recent_alerts_count,
            'devices': devices,
            'active_devices_count': active_devices_count,
            'can_start_monitoring': can_start_monitoring,
            'is_admin': False,
        }
        
        return render(request, 'monitoring/dashboard.html', context)
    
    # ============================================
    # INVALID USER TYPE
    # ============================================
    else:
        messages.error(request, 'Invalid user type. Please contact system administrator.')
        return redirect('accounts:login')



@login_required
def start_monitoring(request):
    """Start a new monitoring session - Allow both pilots and admins"""
    user = request.user
    
    # Check if user already has an active session
    active_session = MonitoringSession.objects.filter(
        pilot=user,
        status='active'
    ).first()
    
    if active_session:
        messages.warning(request, 'You already have an active monitoring session.')
        return redirect('monitoring:live_monitoring', session_id=active_session.id)
    
    # Check if user has devices assigned
    devices = SensorDevice.objects.filter(assigned_to=user, is_active=True)
    has_sufficient_devices = devices.count() >= 3
    
    # If admin, show all available devices for demo/testing
    if user.user_type == 'admin' or user.is_staff or user.is_superuser:
        # Admin can use any pilot's devices for testing
        all_devices = SensorDevice.objects.filter(is_active=True)
        has_sufficient_devices = all_devices.count() >= 3
        
        # Show all devices for admin reference
        devices = all_devices if all_devices.exists() else SensorDevice.objects.all()
    else:
        # Regular pilot - check their own devices
        if not has_sufficient_devices:
            messages.error(request, 'You need at least 3 sensors (EEG, ECG, Eye Tracker) assigned to start monitoring.')
            return redirect('monitoring:dashboard')
    
    if request.method == 'POST':
        form = StartSessionForm(request.POST)
        if form.is_valid():
            # Check again before saving
            if user.user_type != 'admin' and not user.is_staff and not has_sufficient_devices:
                messages.error(request, 'Insufficient devices for monitoring.')
                return redirect('monitoring:dashboard')
            
            session = form.save(commit=False)
            session.pilot = user
            session.status = 'active'
            session.start_time = timezone.now()
            session.save()
            
            messages.success(request, 'Monitoring session started successfully!')
            return redirect('monitoring:live_monitoring', session_id=session.id)
    else:
        form = StartSessionForm()
    
    context = {
        'form': form,
        'devices': devices,
        'has_sufficient_devices': has_sufficient_devices,
        'is_admin': user.user_type == 'admin' or user.is_staff or user.is_superuser
    }
    return render(request, 'monitoring/start_monitoring.html', context)



@login_required
def live_monitoring(request, session_id):
    """Live monitoring view with real-time data"""
    session = get_object_or_404(MonitoringSession, id=session_id, pilot=request.user)
    
    if session.status != 'active':
        messages.warning(request, 'This session is not active.')
        return redirect('monitoring:dashboard')
    
    # Load ML models for predictions
    from analytics.models import MLModel
    import joblib
    import os
    
    ml_models = {}
    scalers = {}
    
    for model_type in ['fatigue', 'stress', 'attention', 'workload']:
        try:
            # Get active model from database
            ml_model = MLModel.objects.filter(
                model_type=model_type,
                status='active'
            ).first()
            
            if ml_model and ml_model.model_file:
                # Get the file path and handle cases where 'media/' is included in the stored path
                file_field = ml_model.model_file
                model_path = str(file_field.path) if hasattr(file_field, 'path') else str(file_field)
                
                # Handle double media/ issue - if path contains media/media, fix it
                if 'media\\media\\' in model_path or 'media/media/' in model_path:
                    # Remove the extra 'media/' prefix
                    model_path = model_path.replace('media\\media\\', 'media\\', 1).replace('media/media/', 'media/', 1)
                
                if os.path.exists(model_path):
                    # Load the trained model
                    ml_models[model_type] = joblib.load(model_path)
                    
                    # Load the scaler
                    if ml_model.scaler_file:
                        scaler_field = ml_model.scaler_file
                        scaler_path = str(scaler_field.path) if hasattr(scaler_field, 'path') else str(scaler_field)
                        
                        # Handle double media/ issue
                        if 'media\\media\\' in scaler_path or 'media/media/' in scaler_path:
                            scaler_path = scaler_path.replace('media\\media\\', 'media\\', 1).replace('media/media/', 'media/', 1)
                        
                        if os.path.exists(scaler_path):
                            scalers[model_type] = joblib.load(scaler_path)
                    
                    print(f"✓ Loaded {model_type} model from: {model_path}")
                else:
                    print(f"⚠ Model file not found: {model_path}")
            else:
                print(f"⚠ {model_type} model not found in database")
                
        except Exception as e:
            print(f"✗ Error loading {model_type} model: {e}")
    
    # Get recent assessments for charts
    assessments = MentalStateAssessment.objects.filter(
        session=session
    ).order_by('-timestamp')[:50]
    
    # Get recent alerts
    alerts = Alert.objects.filter(
        session=session
    ).order_by('-timestamp')[:10]
    
    context = {
        'session': session,
        'assessments': assessments,
        'alerts': alerts,
        'models_loaded': len(ml_models),
        'models_available': ml_models.keys(),
    }
    
    return render(request, 'monitoring/live_monitoring.html', context)



@login_required
def get_live_data(request, session_id):
    """API endpoint for real-time data updates"""
    session = get_object_or_404(MonitoringSession, id=session_id, pilot=request.user)
    
    # Generate simulated sensor data
    sensor_data = generate_simulated_sensor_data()
    
    # Save sensor reading
    # For admins, use any available EEG device; for pilots, use their assigned devices
    if request.user.is_staff or request.user.is_superuser or request.user.user_type == 'admin':
        eeg_device = SensorDevice.objects.filter(device_type='eeg', is_active=True).first()
    else:
        eeg_device = SensorDevice.objects.filter(assigned_to=request.user, device_type='eeg', is_active=True).first()
    
    if eeg_device:
        reading = SensorReading.objects.create(
            session=session,
            device=eeg_device,
            **sensor_data
        )
        
        # Predict mental state
        mental_state = predict_mental_state(sensor_data)
        
        # Determine overall risk
        overall_risk = determine_risk_level(mental_state)
        
        # Create assessment
        assessment = MentalStateAssessment.objects.create(
            session=session,
            fatigue_score=mental_state['fatigue'],
            stress_score=mental_state['stress'],
            attention_score=mental_state['attention'],
            workload_score=mental_state['workload'],
            overall_risk=overall_risk
        )
        
        # Check for alerts
        alert_data = check_thresholds(session, assessment, mental_state)
        
        response_data = {
            'sensor_data': sensor_data,
            'mental_state': mental_state,
            'overall_risk': overall_risk,
            'alert': alert_data
        }
        
        return JsonResponse(response_data)
    
    return JsonResponse({'error': 'No EEG device found'}, status=400)


def generate_simulated_sensor_data():
    """
    Generate realistic simulated sensor data
    TODO: Replace with actual sensor integration
    """
    return {
        'eeg_channel_1': round(random.uniform(15, 35), 2),
        'eeg_channel_2': round(random.uniform(15, 35), 2),
        'eeg_channel_3': round(random.uniform(15, 35), 2),
        'eeg_channel_4': round(random.uniform(10, 30), 2),
        'eeg_channel_5': round(random.uniform(15, 35), 2),
        'eeg_channel_6': round(random.uniform(10, 25), 2),
        'eeg_channel_7': round(random.uniform(15, 30), 2),
        'eeg_channel_8': round(random.uniform(10, 25), 2),
        'ecg_heart_rate': round(random.uniform(60, 100), 2),
        'ecg_hrv': round(random.uniform(30, 70), 2),
        'ecg_rr_interval': round(random.uniform(600, 1000), 2),
        'eye_blink_rate': round(random.uniform(10, 30), 2),
        'eye_fixation_duration': round(random.uniform(200, 400), 2),
        'eye_saccade_velocity': round(random.uniform(250, 450), 2),
        'pupil_diameter': round(random.uniform(3.5, 5.5), 2),
    }


def predict_mental_state(sensor_data):
    """
    Predict mental state using ML models
    Returns predictions for fatigue, stress, attention, workload
    """
    try:
        # Load models and scalers
        models = {}
        scalers = {}
        
        for metric in ['fatigue', 'stress', 'attention', 'workload']:
            model_obj = MLModel.objects.filter(
                model_type=metric,
                status='active'
            ).first()
            
            if model_obj:
                try:
                    # Get model file path and handle double media/ issue
                    model_file = model_obj.model_file
                    model_path = str(model_file.path) if hasattr(model_file, 'path') else str(model_file)
                    
                    if 'media\\media\\' in model_path or 'media/media/' in model_path:
                        model_path = model_path.replace('media\\media\\', 'media\\', 1).replace('media/media/', 'media/', 1)
                    
                    if os.path.exists(model_path):
                        models[metric] = joblib.load(model_path)
                    else:
                        print(f"Model file not found: {model_path}")
                        continue
                    
                    # Get scaler file path and handle double media/ issue
                    if model_obj.scaler_file:
                        scaler_file = model_obj.scaler_file
                        scaler_path = str(scaler_file.path) if hasattr(scaler_file, 'path') else str(scaler_file)
                        
                        if 'media\\media\\' in scaler_path or 'media/media/' in scaler_path:
                            scaler_path = scaler_path.replace('media\\media\\', 'media\\', 1).replace('media/media/', 'media/', 1)
                        
                        if os.path.exists(scaler_path):
                            scalers[metric] = joblib.load(scaler_path)
                        
                except Exception as e:
                    print(f"Error loading {metric} model: {e}")
                    continue
        
        # Prepare features (15 features)
        features = [
            sensor_data['eeg_channel_1'], sensor_data['eeg_channel_2'],
            sensor_data['eeg_channel_3'], sensor_data['eeg_channel_4'],
            sensor_data['eeg_channel_5'], sensor_data['eeg_channel_6'],
            sensor_data['eeg_channel_7'], sensor_data['eeg_channel_8'],
            sensor_data['ecg_heart_rate'], sensor_data['ecg_hrv'],
            sensor_data['ecg_rr_interval'], sensor_data['eye_blink_rate'],
            sensor_data['eye_fixation_duration'], sensor_data['eye_saccade_velocity'],
            sensor_data['pupil_diameter']
        ]
        
        X = np.array(features).reshape(1, -1)
        
        predictions = {}
        for metric in ['fatigue', 'stress', 'attention', 'workload']:
            if metric in models and metric in scalers:
                try:
                    X_scaled = scalers[metric].transform(X)
                    pred = models[metric].predict(X_scaled)[0]
                    predictions[metric] = round(float(np.clip(pred, 0, 1)), 3)
                except Exception as e:
                    print(f"Error predicting {metric}: {e}")
                    predictions[metric] = round(random.uniform(0.2, 0.7), 3)
            else:
                # Fallback to random values if model not found
                predictions[metric] = round(random.uniform(0.2, 0.7), 3)
        
        return predictions
    
    except Exception as e:
        print(f"Error in predict_mental_state: {e}")
        # Fallback predictions
        return {
            'fatigue': round(random.uniform(0.2, 0.6), 3),
            'stress': round(random.uniform(0.2, 0.6), 3),
            'attention': round(random.uniform(0.4, 0.8), 3),
            'workload': round(random.uniform(0.3, 0.7), 3),
        }


def determine_risk_level(mental_state):
    """
    Determine overall risk level based on mental state scores
    Returns: 'low', 'medium', 'high', or 'critical'
    """
    risk_score = (
        mental_state['fatigue'] * 0.3 +
        mental_state['stress'] * 0.3 +
        (1 - mental_state['attention']) * 0.2 +
        mental_state['workload'] * 0.2
    )
    
    if risk_score >= 0.75:
        return 'critical'
    elif risk_score >= 0.60:
        return 'high'
    elif risk_score >= 0.40:
        return 'medium'
    else:
        return 'low'


def check_thresholds(session, assessment, mental_state):
    """
    Check if any thresholds are exceeded and create alerts
    Returns alert data if triggered
    """
    thresholds = AlertThreshold.objects.filter(enabled=True)
    
    for threshold in thresholds:
        metric_value = mental_state[threshold.metric_name]
        
        # For attention, lower is worse
        if threshold.metric_name == 'attention':
            if metric_value <= threshold.critical_threshold:
                severity = 'critical'
                message = f'CRITICAL: Attention level extremely low ({metric_value:.2f})'
            elif metric_value <= threshold.warning_threshold:
                severity = 'warning'
                message = f'WARNING: Attention level low ({metric_value:.2f})'
            else:
                continue
        else:
            # For fatigue, stress, workload - higher is worse
            if metric_value >= threshold.critical_threshold:
                severity = 'critical'
                message = f'CRITICAL: {threshold.get_metric_name_display()} level very high ({metric_value:.2f})'
            elif metric_value >= threshold.warning_threshold:
                severity = 'warning'
                message = f'WARNING: {threshold.get_metric_name_display()} level elevated ({metric_value:.2f})'
            else:
                continue
        
        # Create alert
        alert = Alert.objects.create(
            session=session,
            assessment=assessment,
            severity=severity,
            alert_type=threshold.metric_name,
            message=message
        )
        
        # Update assessment with alert info
        assessment.alert_triggered = True
        assessment.alert_type = threshold.metric_name
        assessment.alert_message = message
        assessment.save()
        
        return {
            'triggered': True,
            'severity': severity,
            'type': threshold.metric_name,
            'message': message
        }
    
    return {'triggered': False}


@login_required
def end_monitoring(request, session_id):
    """End an active monitoring session"""
    session = get_object_or_404(MonitoringSession, id=session_id, pilot=request.user)
    
    if session.status != 'active':
        messages.error(request, 'This session is already ended.')
        return redirect('monitoring:dashboard')
    
    if request.method == 'POST':
        form = EndSessionForm(request.POST)
        if form.is_valid():
            session.status = 'completed'
            session.end_time = timezone.now()
            session.calculate_duration()
            
            if form.cleaned_data.get('notes'):
                session.notes += '\n\nEnd Notes: ' + form.cleaned_data['notes']
            
            session.save()
            
            # Generate session report
            generate_session_report(session)
            
            messages.success(request, 'Monitoring session ended. Report generated.')
            return redirect('monitoring:session_summary', session_id=session.id)
    else:
        form = EndSessionForm()
    
    context = {
        'session': session,
        'form': form
    }
    return render(request, 'monitoring/end_monitoring.html', context)


def generate_session_report(session):
    """
    Generate comprehensive session report with statistics and recommendations
    """
    # Calculate statistics
    assessments = MentalStateAssessment.objects.filter(session=session)
    
    if assessments.exists():
        stats = assessments.aggregate(
            avg_fatigue=Avg('fatigue_score'),
            avg_stress=Avg('stress_score'),
            avg_attention=Avg('attention_score'),
            avg_workload=Avg('workload_score'),
            max_fatigue=Max('fatigue_score'),
            max_stress=Max('stress_score'),
            min_attention=Min('attention_score'),
            max_workload=Max('workload_score'),
        )
        
        alerts = Alert.objects.filter(session=session)
        total_alerts = alerts.count()
        critical_alerts = alerts.filter(severity='critical').count()
        
        # Determine overall performance
        avg_score = (
            (1 - stats['avg_fatigue']) * 0.25 +
            (1 - stats['avg_stress']) * 0.25 +
            stats['avg_attention'] * 0.25 +
            (1 - stats['avg_workload']) * 0.25
        )
        
        if avg_score >= 0.75:
            performance = 'excellent'
        elif avg_score >= 0.60:
            performance = 'good'
        elif avg_score >= 0.45:
            performance = 'fair'
        else:
            performance = 'poor'
        
        # Generate recommendations
        recommendations = []
        if stats['avg_fatigue'] and stats['avg_fatigue'] > 0.6:
            recommendations.append('High fatigue detected. Recommend rest before next flight.')
        if stats['avg_stress'] and stats['avg_stress'] > 0.6:
            recommendations.append('Elevated stress levels. Consider stress management techniques.')
        if stats['avg_attention'] and stats['avg_attention'] < 0.5:
            recommendations.append('Attention levels below optimal. Ensure adequate rest and hydration.')
        if stats['max_workload'] and stats['max_workload'] > 0.8:
            recommendations.append('Peak workload very high. Monitor for signs of cognitive overload.')
        if critical_alerts > 0:
            recommendations.append(f'{critical_alerts} critical alerts triggered. Review flight conditions.')
        
        if not recommendations:
            recommendations.append('Performance within normal parameters. Maintain current practices.')
        
        # Create or update report
        report, created = SessionReport.objects.update_or_create(
            session=session,
            defaults={
                'avg_fatigue': stats['avg_fatigue'] or 0,
                'avg_stress': stats['avg_stress'] or 0,
                'avg_attention': stats['avg_attention'] or 0,
                'avg_workload': stats['avg_workload'] or 0,
                'max_fatigue': stats['max_fatigue'] or 0,
                'max_stress': stats['max_stress'] or 0,
                'min_attention': stats['min_attention'] or 0,
                'max_workload': stats['max_workload'] or 0,
                'total_alerts': total_alerts,
                'critical_alerts': critical_alerts,
                'overall_performance': performance,
                'recommendations': '\n'.join(recommendations)
            }
        )
        
        return report
    
    return None

@login_required
def session_summary(request, session_id):
    """Display session summary with report and analytics"""
    session = get_object_or_404(MonitoringSession, id=session_id, pilot=request.user)
    
    # Get or generate report
    try:
        report = SessionReport.objects.get(session=session)
    except SessionReport.DoesNotExist:
        # Generate report if it doesn't exist
        report = generate_session_report(session)
    
    # Get assessments for chart
    assessments = MentalStateAssessment.objects.filter(session=session).order_by('timestamp')
    
    # Get all alerts
    alerts = Alert.objects.filter(session=session).order_by('-timestamp')
    
    context = {
        'session': session,
        'report': report,  # This might be None if generation failed
        'assessments': assessments,
        'alerts': alerts,
        'has_report': report is not None,  # Add this flag
    }
    
    return render(request, 'monitoring/session_summary.html', context)


@login_required
def session_history(request):
    """Display all pilot's past sessions"""
    sessions = MonitoringSession.objects.filter(
        pilot=request.user
    ).order_by('-start_time')
    
    context = {
        'sessions': sessions
    }
    
    return render(request, 'monitoring/session_history.html', context)


@login_required
def acknowledge_alert(request, alert_id):
    """Acknowledge an alert (AJAX endpoint)"""
    alert = get_object_or_404(Alert, id=alert_id)
    
    if alert.session.pilot != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    alert.acknowledged = True
    alert.acknowledged_at = timezone.now()
    alert.save()
    
    return JsonResponse({'success': True})
