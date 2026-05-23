from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    
    # Model Management
    path('models/', views.model_management, name='model_management'),
    path('models/<int:model_id>/', views.model_details, name='model_details'),
    path('models/train/', views.train_model, name='train_model'),
    path('models/<int:model_id>/activate/', views.activate_model, name='activate_model'),
    path('models/<int:model_id>/delete/', views.delete_model, name='delete_model'),
    
    # Datasets
    path('datasets/upload/', views.upload_dataset, name='upload_dataset'),
    
    # Reports
    path('reports/', views.reports_list, name='reports_list'),
    path('reports/<int:report_id>/download/', views.download_report, name='download_report'),
]
