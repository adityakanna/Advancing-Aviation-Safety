from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Avg, Count
from django.utils import timezone  # ✅ ADDED: Timezone support
import os


from .models import MLModel, TrainingDataset, SessionReport


@login_required
def analytics_dashboard(request):
    """Analytics dashboard"""
    user = request.user
    
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    # Get active models
    active_models = MLModel.objects.filter(status='active')
    total_models = MLModel.objects.all().count()
    
    # Get datasets
    datasets = TrainingDataset.objects.all()[:5]
    total_datasets = TrainingDataset.objects.all().count()
    
    # Get recent reports
    recent_reports = SessionReport.objects.all().select_related('session__pilot').order_by('-session__start_time')[:10]
    total_reports = SessionReport.objects.all().count()
    
    context = {
        'active_models': active_models,
        'total_models': total_models,
        'datasets': datasets,
        'total_datasets': total_datasets,
        'recent_reports': recent_reports,
        'total_reports': total_reports,
    }
    
    # Fix: Use correct template name
    return render(request, 'analytics/dashboard.html', context)




@login_required
def model_management(request):
    """ML Model management page"""
    user = request.user
    
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    models = MLModel.objects.all().order_by('-created_at')
    
    context = {'models': models}
    return render(request, 'analytics/model_management.html', context)


@login_required
def train_model(request):
    """Train new ML models"""
    user = request.user
    
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        messages.info(request, 'Training started. Please wait...')
        
        try:
            # Import training function
            import pandas as pd
            import numpy as np
            from sklearn.ensemble import GradientBoostingRegressor
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import StandardScaler
            from sklearn.metrics import r2_score
            import joblib
            from datetime import datetime
            
            # Load dataset
            dataset_file = 'realistic_training_dataset.csv'
            
            if not os.path.exists(dataset_file):
                messages.error(request, f'Dataset not found: {dataset_file}')
                return redirect('analytics:model_management')
            
            df = pd.read_csv(dataset_file)
            
            # Features
            features = [
                'eeg_channel_1', 'eeg_channel_2', 'eeg_channel_3', 'eeg_channel_4',
                'eeg_channel_5', 'eeg_channel_6', 'eeg_channel_7', 'eeg_channel_8',
                'ecg_heart_rate', 'ecg_hrv', 'ecg_rr_interval',
                'eye_blink_rate', 'eye_fixation_duration', 'eye_saccade_velocity', 'pupil_diameter'
            ]
            
            X = df[features].values
            targets = ['fatigue', 'stress', 'attention', 'workload']
            
            # Create output directory
            output_dir = 'media/ml_models'
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            trained_count = 0
            
            # Create dataset entry in database
            dataset_obj = TrainingDataset.objects.create(
                name=f'Training Dataset - {timestamp}',
                description=f'Dataset used for training {len(targets)} models on {timezone.now().strftime("%Y-%m-%d %H:%M")}',
                file_path=dataset_file,
                total_samples=len(df),
                feature_count=len(features),
                created_by=user
            )
            
            # Train each model
            for target in targets:
                try:
                    y = df[target].values
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                    
                    # Scale
                    scaler = StandardScaler()
                    X_train_scaled = scaler.fit_transform(X_train)
                    X_test_scaled = scaler.transform(X_test)
                    
                    # Train
                    model = GradientBoostingRegressor(
                        n_estimators=100,
                        max_depth=4,
                        learning_rate=0.1,
                        random_state=42
                    )
                    model.fit(X_train_scaled, y_train)
                    
                    # Evaluate
                    y_pred = model.predict(X_test_scaled)
                    accuracy = r2_score(y_test, y_pred)
                    
                    # Save files
                    model_file = os.path.join(output_dir, f'{target}_model_{timestamp}.pkl')
                    scaler_file = os.path.join(output_dir, f'{target}_scaler_{timestamp}.pkl')
                    
                    joblib.dump(model, model_file)
                    joblib.dump(scaler, scaler_file)
                    
                    # Update database - ✅ FIXED SECTION
                    MLModel.objects.filter(model_type=target).update(status='archived')
                    
                    # Generate unique version with timestamp
                    version = timezone.now().strftime('%Y.%m.%d.%H%M%S')
                    
                    MLModel.objects.create(
                        name=f'{target.title()} Detection Model',
                        model_type=target,
                        version=version,  # ✅ FIXED: Unique version
                        algorithm='gradient_boosting',
                        accuracy=float(accuracy),
                        precision=float(accuracy),
                        recall=float(accuracy),
                        f1_score=float(accuracy),
                        training_samples=len(X_train),
                        model_file=model_file,
                        scaler_file=scaler_file,
                        status='active',
                        training_date=timezone.now()  # ✅ FIXED: Timezone-aware datetime
                    )
                    
                    trained_count += 1
                    
                except Exception as e:
                    print(f"Error training {target}: {e}")
                    continue
            
            if trained_count == 4:
                messages.success(request, f'✅ Successfully trained all 4 models! Ready to use.')
            elif trained_count > 0:
                messages.warning(request, f'⚠ Trained {trained_count} out of 4 models.')
            else:
                messages.error(request, 'Training failed. Check console for errors.')
                
        except Exception as e:
            messages.error(request, f'Training error: {str(e)}')
            print(f"Training exception: {e}")
            import traceback
            traceback.print_exc()
        
        return redirect('analytics:model_management')
    
    return render(request, 'analytics/train_model.html')




@login_required
def activate_model(request, model_id):
    """Activate model"""
    user = request.user
    
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    model = get_object_or_404(MLModel, id=model_id)
    MLModel.objects.filter(model_type=model.model_type).update(status='archived')
    model.status = 'active'
    model.save()
    
    messages.success(request, f'{model.name} activated!')
    return redirect('analytics:model_management')



@login_required
def delete_model(request, model_id):
    """Delete model"""
    user = request.user
    
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    model = get_object_or_404(MLModel, id=model_id)
    model.delete()
    
    messages.success(request, 'Model deleted!')
    return redirect('analytics:model_management')



@login_required
def reports_list(request):
    """View reports"""
    user = request.user
    
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    reports = SessionReport.objects.all().select_related('session__pilot').order_by('-session__start_time')
    
    context = {'reports': reports}
    return render(request, 'analytics/reports_list.html', context)



@login_required
def download_report(request, report_id):
    """Download report as CSV"""
    report = get_object_or_404(SessionReport, id=report_id)
    
    if request.user.user_type == 'pilot' and report.session.pilot != request.user:
        messages.error(request, 'Access denied.')
        return redirect('monitoring:dashboard')
    
    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="report_{report.id}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Session Report'])
    writer.writerow(['Pilot', report.session.pilot.get_full_name()])
    writer.writerow(['Date', report.session.start_time])
    
    return response


@login_required
def upload_dataset(request):
    """Upload training dataset"""
    user = request.user
    
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        # Handle file upload
        if 'dataset_file' in request.FILES:
            try:
                import pandas as pd
                
                dataset_file = request.FILES['dataset_file']
                dataset_name = request.POST.get('dataset_name', dataset_file.name)
                dataset_description = request.POST.get('dataset_description', '')
                
                # Handle file upload
                upload_dir = 'media/datasets'
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, dataset_file.name)
                
                # Save file
                with open(file_path, 'wb+') as f:
                    for chunk in dataset_file.chunks():
                        f.write(chunk)
                
                # Read dataset to get stats
                try:
                    df = pd.read_csv(file_path)
                    total_samples = len(df)
                    feature_count = len(df.columns)
                except Exception as e:
                    messages.warning(request, 'Could not read CSV file. Saving anyway.')
                    total_samples = 0
                    feature_count = 0
                
                # Create dataset entry in database
                TrainingDataset.objects.create(
                    name=dataset_name,
                    description=dataset_description,
                    file_path=file_path,
                    total_samples=total_samples,
                    feature_count=feature_count,
                    created_by=user
                )
                
                messages.success(request, f'Dataset "{dataset_name}" uploaded successfully!')
                return redirect('analytics:analytics_dashboard')
            
            except Exception as e:
                messages.error(request, f'Error uploading dataset: {str(e)}')
                return redirect('analytics:upload_dataset')
        else:
            messages.error(request, 'No file selected.')
    
    return render(request, 'analytics/upload_dataset.html')


@login_required
def model_details(request, model_id):
    """View model details"""
    user = request.user
    
    if user.user_type != 'admin' and not user.is_staff and not user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    model = get_object_or_404(MLModel, id=model_id)
    
    context = {
        'model': model
    }
    
    return render(request, 'analytics/model_details.html', context)
