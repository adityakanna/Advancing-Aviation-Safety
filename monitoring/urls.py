from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('start/', views.start_monitoring, name='start_monitoring'),
    path('live/<int:session_id>/', views.live_monitoring, name='live_monitoring'),
    path('live/<int:session_id>/data/', views.get_live_data, name='get_live_data'),
    path('end/<int:session_id>/', views.end_monitoring, name='end_monitoring'),
    path('summary/<int:session_id>/', views.session_summary, name='session_summary'),
    path('history/', views.session_history, name='session_history'),
    path('alert/acknowledge/<int:alert_id>/', views.acknowledge_alert, name='acknowledge_alert'),
]
