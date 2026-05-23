# Aviation Safety Monitoring System - Complete Project Documentation

## Project Overview
The **Advancing Aviation Safety** project is a comprehensive Django-based web application designed to monitor pilot cognitive and physiological states during flight operations. The system uses machine learning models to detect fatigue, stress, attention levels, and workload in real-time, helping to improve aviation safety.

---

## Table of Contents
1. [Project Structure](#project-structure)
2. [Core Modules](#core-modules)
3. [Database Models](#database-models)
4. [File Descriptions](#file-descriptions)
5. [Configuration](#configuration)
6. [Dependencies](#dependencies)
7. [Setup Instructions](#setup-instructions)

---

## Project Structure

```
Advancing Aviation Safety/
├── aviation_system/          # Django project configuration
├── accounts/                 # User and device management
├── monitoring/               # Real-time monitoring system
├── analytics/                # ML models and data analysis
├── administration/           # System administration and configuration
├── aviation_venv/            # Python virtual environment
├── static/                   # CSS and JavaScript files
├── templates/                # HTML templates for web interface
├── media/                    # User-uploaded files and ML models
├── manage.py                 # Django management script
├── generate_realistic_dataset.py  # Dataset generation utility
└── README.md                 # Setup and installation guide
```

---

## Core Modules

### 1. **accounts/** - User and Device Management
Handles user authentication, profiles, and sensor device management.

#### Models:
- **User**: Extended Django user model with fields:
  - `user_type`: 'pilot' or 'admin'
  - `employee_id`: Unique employee identifier
  - `phone_number`: Contact information
  - `profile_picture`: User profile image
  - `date_of_birth`: Birth date
  - `license_number`: Pilot license number
  - `total_flight_hours`: Total flying experience
  - `is_active_pilot`: Status flag
  - Methods: `is_pilot()`, `is_admin()`

- **SensorDevice**: Represents physical sensors assigned to pilots
  - `device_id`: Unique device identifier
  - `device_type`: EEG, ECG, or Eye Tracker
  - `manufacturer`: Device manufacturer name
  - `model_number`: Device model
  - `assigned_to`: Foreign key to User
  - `is_active`: Device status
  - `last_calibration`: Calibration timestamp

#### Files:
- `models.py`: User and SensorDevice model definitions
- `views.py`: Views for user registration, login, profile management, and device management
- `forms.py`: Forms for user registration and device management
- `urls.py`: URL routing for accounts app
- `admin.py`: Django admin interface configuration
- `tests.py`: Unit tests for accounts app
- `migrations/`: Database migration files

---

### 2. **monitoring/** - Real-Time Monitoring System
Captures and stores sensor data during pilot monitoring sessions and assessments.

#### Models:
- **MonitoringSession**: Main session record for pilot monitoring
  - `pilot`: Foreign key to User
  - `session_type`: 'flight', 'simulator', or 'training'
  - `status`: 'active', 'completed', or 'aborted'
  - `start_time`: Session start timestamp
  - `end_time`: Session end timestamp
  - `duration_minutes`: Calculated session duration
  - `aircraft_type`: Type of aircraft
  - `flight_number`: Flight identifier
  - `route`: Flight route information
  - `notes`: Session notes and observations
  - Method: `calculate_duration()`

- **SensorReading**: Raw sensor data from devices
  - `session`: Foreign key to MonitoringSession
  - `device`: Foreign key to SensorDevice
  - `timestamp`: Reading timestamp
  - **EEG Data**: 8 channels (eeg_channel_1 through eeg_channel_8)
  - **ECG Data**: heart_rate, hrv (Heart Rate Variability), rr_interval
  - **Eye Tracking Data**: blink_rate, fixation_duration, saccade_velocity, pupil_diameter
  - Index: On session and timestamp for fast queries

- **MentalStateAssessment**: ML model predictions for mental state
  - `session`: Foreign key to MonitoringSession
  - `timestamp`: Assessment timestamp
  - **Mental State Scores** (0-1 range):
    - `fatigue_score`: Pilot fatigue level
    - `stress_score`: Pilot stress level
    - `attention_score`: Pilot attention level
    - `workload_score`: Cognitive workload
  - `overall_risk`: 'low', 'medium', 'high', or 'critical'
  - `alert_triggered`: Boolean flag for alert generation

#### Files:
- `models.py`: MonitoringSession, SensorReading, and MentalStateAssessment models
- `views.py`: Views for session management, live monitoring, and session history
- `forms.py`: Forms for monitoring session creation and management
- `urls.py`: URL routing for monitoring app
- `admin.py`: Django admin configuration
- `tests.py`: Unit tests for monitoring app
- `migrations/`: Database migration files

---

### 3. **analytics/** - Machine Learning and Data Analysis
Handles ML model training, dataset management, and report generation.

#### Models:
- **MLModel**: Machine learning model information
  - `name`: Model name
  - `model_type`: 'fatigue', 'stress', 'attention', or 'workload' detection
  - `version`: Model version string
  - `status`: 'training', 'active', or 'archived'
  - `algorithm`: Algorithm name (e.g., Random Forest, SVM)
  - `model_file`: Path to trained model file (joblib)
  - `scaler_file`: Path to data scaler file
  - **Performance Metrics**:
    - `accuracy`: Model accuracy percentage
    - `precision`: Precision metric
    - `recall`: Recall metric
    - `f1_score`: F1 score
  - `training_samples`: Number of samples used in training
  - `training_date`: Date model was trained
  - `created_by`: Foreign key to User (ML engineer)

- **TrainingDataset**: Dataset for ML model training
  - `name`: Dataset name
  - `description`: Dataset description
  - `file_path`: Path to CSV file
  - `total_samples`: Number of data samples
  - `feature_count`: Number of features in dataset
  - `created_by`: Foreign key to User

- **SessionReport**: Analysis report for completed sessions
  - `session`: One-to-one relationship with MonitoringSession
  - `generated_at`: Report generation timestamp
  - **Summary Statistics**:
    - `avg_fatigue`, `avg_stress`, `avg_attention`, `avg_workload`: Average scores
    - `max_fatigue`, `max_stress`, `max_workload`, `min_attention`: Extreme values
  - `total_alerts`: Total number of alerts generated
  - `critical_alerts`: Number of critical alerts
  - `overall_performance`: 'excellent', 'good', 'fair', or 'poor'
  - `recommendations`: Text recommendations for pilot
  - `report_file`: Path to generated PDF/document report

#### Files:
- `models.py`: MLModel, TrainingDataset, and SessionReport models
- `views.py`: Views for model management, training, dataset upload, and report viewing
- `forms.py`: Forms for model training and dataset upload
- `fast_ml_training.py`: Machine learning training script with scikit-learn
- `urls.py`: URL routing for analytics app
- `admin.py`: Django admin configuration
- `tests.py`: Unit tests for analytics app
- `migrations/`: Database migration files

---

### 4. **administration/** - System Administration and Configuration
Manages system settings, alert thresholds, audit logs, and backups.

#### Models:
- **SystemConfiguration**: Key-value system settings
  - `key`: Configuration key (unique)
  - `value`: Configuration value
  - `description`: Human-readable description
  - `data_type`: 'string', 'integer', 'float', 'boolean', or 'json'
  - `updated_by`: Foreign key to User (admin)
  - `updated_at`: Last update timestamp

- **AlertThreshold**: Alert threshold configuration for metrics
  - `metric_name`: 'fatigue', 'stress', 'attention', or 'workload'
  - `warning_threshold`: Threshold for warning alerts
  - `critical_threshold`: Threshold for critical alerts
  - `enabled`: Boolean flag to enable/disable alert
  - `updated_by`: Foreign key to User
  - `updated_at`: Last update timestamp

- **AuditLog**: System audit trail
  - `user`: Foreign key to User (who performed action)
  - `action`: 'create', 'update', 'delete', 'login', 'logout', 'config_change', 'model_train', 'alert_config'
  - `entity_type`: Type of entity affected
  - `entity_id`: ID of entity affected
  - `description`: Description of action
  - `ip_address`: IP address of user
  - `timestamp`: Action timestamp

- **SystemBackup**: Backup management
  - `backup_name`: Name of backup
  - `backup_type`: 'database', 'models', or 'full'
  - `file_path`: Path to backup file
  - `file_size_mb`: Size of backup in MB
  - `created_by`: Foreign key to User
  - `created_at`: Backup creation timestamp

#### Files:
- `models.py`: SystemConfiguration, AlertThreshold, AuditLog, and SystemBackup models
- `views.py`: Views for admin dashboard, system configuration, alert configuration, audit logs, and backups
- `forms.py`: Forms for configuration editing and threshold management
- `urls.py`: URL routing for administration app
- `admin.py`: Django admin configuration
- `tests.py`: Unit tests for administration app
- `migrations/`: Database migration files

---

### 5. **aviation_system/** - Django Project Configuration
Core Django project settings and configuration.

#### Files:
- **settings.py**: Django settings
  - Database configuration
  - Installed apps (crispy_forms, channels, local apps)
  - Middleware configuration
  - Static and media files configuration
  - Authentication settings
  
- **urls.py**: Main URL router
  - Routes to accounts, monitoring, analytics, and administration apps
  - Admin interface routing
  
- **wsgi.py**: WSGI application entry point for production servers
  
- **asgi.py**: ASGI application entry point for async support with Channels
  
- **__init__.py**: Python package initialization

---

## Database Models Summary

### User-Related:
- `User` (accounts) - Pilot and admin user profiles
- `SensorDevice` (accounts) - Physical sensors assigned to users

### Monitoring-Related:
- `MonitoringSession` (monitoring) - Flight/training session records
- `SensorReading` (monitoring) - Raw sensor data readings
- `MentalStateAssessment` (monitoring) - ML predictions for mental state

### Analytics-Related:
- `MLModel` (analytics) - Trained machine learning models
- `TrainingDataset` (analytics) - Training data for ML models
- `SessionReport` (analytics) - Generated analysis reports

### Administration-Related:
- `SystemConfiguration` (administration) - System settings
- `AlertThreshold` (administration) - Alert configuration
- `AuditLog` (administration) - System audit trail
- `SystemBackup` (administration) - Backup files

---

## File Descriptions

### Root Level Files:

| File | Purpose |
|------|---------|
| `manage.py` | Django management CLI tool for running commands (migrate, runserver, etc.) |
| `requirements.txt` | Python package dependencies (Django, scikit-learn, channels, etc.) |
| `generate_realistic_dataset.py` | Utility script to generate synthetic training datasets |
| `README.md` | Quick start guide and setup instructions |

### Dataset Files:

| File | Purpose |
|------|---------|
| `realistic_training_dataset.csv` | Training data CSV (features and labels for ML models) |
| `realistic_validation_dataset.csv` | Validation data CSV for model evaluation |
| `realistic_test_dataset.csv` | Test data CSV for final model testing |

### Static Files:

| File | Purpose |
|------|---------|
| `static/css/style.css` | Application-wide CSS styling |
| `static/js/main.js` | JavaScript for interactive features |
| `static/images/` | Images and icons used in templates |

### Template Files:

#### Base Template:
- `templates/base.html` - Base template with navigation and common layout

#### Accounts Templates:
- `login.html` - User login page
- `register.html` - User registration page
- `profile.html` - User profile view and edit
- `device_management.html` - Device management list
- `add_device.html` - Add new sensor device
- `edit_device.html` - Edit existing sensor device

#### Monitoring Templates:
- `start_monitoring.html` - Start new monitoring session
- `live_monitoring.html` - Real-time monitoring dashboard
- `end_monitoring.html` - End monitoring session
- `session_history.html` - View past monitoring sessions
- `session_summary.html` - View session summary and details
- `dashboard.html` - Monitoring dashboard overview

#### Analytics Templates:
- `dashboard.html` - Analytics dashboard with charts
- `model_management.html` - View and manage ML models
- `train_model.html` - Train new ML model
- `model_details.html` - View model information and metrics
- `upload_dataset.html` - Upload training dataset
- `reports_list.html` - List analysis reports

#### Administration Templates:
- `admin_dashboard.html` - Admin overview dashboard
- `user_management.html` - Manage users and permissions
- `system_configuration.html` - Edit system settings
- `edit_configuration.html` - Edit individual configuration
- `alert_configuration.html` - Configure alert thresholds
- `edit_threshold.html` - Edit alert threshold values
- `audit_logs.html` - View system audit logs
- `system_reports.html` - View system reports

### Media Folders:

| Folder | Purpose |
|--------|---------|
| `media/datasets/` | Stores uploaded training datasets |
| `media/ml_models/` | Stores trained ML model files (joblib format) |

---

## Configuration

### Key Settings (from settings.py):
- **DEBUG**: Set to `True` for development
- **ALLOWED_HOSTS**: Configure for your domain
- **INSTALLED_APPS**: All Django apps including accounts, monitoring, analytics, administration
- **DATABASES**: MySQL database configuration for `aviation_monitoring_db`
- **MIDDLEWARE**: CSRF protection, session handling, authentication
- **CHANNEL_LAYERS**: Redis configuration for WebSocket support

### Alert Thresholds Configuration:
Alert thresholds can be configured through the admin interface for:
- Fatigue detection
- Stress level detection
- Attention level detection
- Workload assessment

---

## Dependencies

Main Python packages (see requirements.txt):

| Package | Purpose |
|---------|---------|
| `Django` | Web framework |
| `mysqlclient` | MySQL database driver |
| `scikit-learn` | Machine learning algorithms |
| `pandas` | Data manipulation and analysis |
| `numpy` | Numerical computing |
| `matplotlib` | Data visualization |
| `seaborn` | Statistical data visualization |
| `scipy` | Scientific computing |
| `joblib` | Serialize Python objects (for ML models) |
| `channels` | WebSocket support for real-time updates |
| `channels-redis` | Redis backend for Channels |
| `Pillow` | Image processing |
| `django-crispy-forms` | Better form rendering |
| `crispy-bootstrap5` | Bootstrap 5 form styling |
| `python-dateutil` | Date utilities |
| `pytz` | Timezone support |

---

## Setup Instructions

### 1. Activate Virtual Environment:
```bash
aviation_venv\Scripts\activate
```

### 2. Install Requirements:
```bash
pip install -r requirements.txt
```

### 3. Create Database:
```sql
CREATE DATABASE aviation_monitoring_db;
```

### 4. Run Migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser:
```bash
python manage.py createsuperuser
```

### 6. Generate Training Dataset (Optional):
```bash
python generate_realistic_dataset.py
```

### 7. Train ML Models:
```bash
python analytics/fast_ml_training.py
```

### 8. Allocate Sensor Devices:
- Go to Device Management in the web interface
- Add and allocate the three available device models:
  - EEG Sensor
  - ECG Sensor
  - Eye Tracker

### 9. Run Development Server:
```bash
python manage.py runserver
```

Access the application at `http://localhost:8000/`

Login credentials:
- Username: `admin`
- Password: (as set during superuser creation)

---

## Key Features

### 1. **User Management**
- Role-based access (Pilot, Administrator)
- User profile management with flight hours tracking
- Pilot license and employee ID management

### 2. **Device Management**
- Register and manage EEG, ECG, and Eye Tracker devices
- Track device calibration status
- Assign devices to specific pilots

### 3. **Real-Time Monitoring**
- Live monitoring dashboard
- Real-time sensor data collection
- Multi-channel EEG data capture
- Heart rate and ECG analysis
- Eye tracking metrics
- Real-time mental state assessment

### 4. **Machine Learning**
- Fatigue detection model
- Stress detection model
- Attention level assessment
- Workload prediction
- Model performance metrics (accuracy, precision, recall, F1)
- Dataset management and versioning

### 5. **Analysis and Reporting**
- Session reports with statistical analysis
- Performance ratings (Excellent, Good, Fair, Poor)
- Alert generation and logging
- Recommendations for pilots
- Historical report access

### 6. **System Administration**
- System configuration management
- Alert threshold customization
- Comprehensive audit logging
- System backup management
- User permission management

---

## Workflow: From Monitoring to Report

1. **Setup Phase**: Admin allocates sensor devices to pilots
2. **Session Initiation**: Pilot starts a monitoring session (flight, simulator, or training)
3. **Data Collection**: Multiple sensors collect physiological data simultaneously
4. **Real-Time Analysis**: ML models assess mental state in real-time
5. **Alert Generation**: System generates alerts when thresholds are exceeded
6. **Session Completion**: Session is marked as complete
7. **Report Generation**: System generates comprehensive analysis report
8. **Review and Archival**: Pilot/Admin reviews report and it's stored for historical analysis

---

## Database Schema Notes

- All models use MySQL with custom table names
- Foreign key relationships maintain referential integrity
- Indexes are created for frequently queried fields (e.g., session + timestamp)
- Timestamps use UTC timezone through Django's timezone support
- Soft deletes are not implemented; deleted records are permanently removed
- User-related audit trails are maintained in AuditLog table

---

## Security Considerations

- CSRF protection enabled
- Session-based authentication
- Role-based access control (pilot vs. admin)
- User IP address logging in audit logs
- Secret key should be changed in production
- DEBUG should be set to False in production
- Database credentials should be environment variables
- HTTPS should be enforced in production

---

## Future Enhancement Opportunities

1. Real-time notification system via WebSockets (Channels already configured)
2. Advanced data visualization dashboards
3. Historical trend analysis and predictions
4. Multi-language support
5. Mobile application for remote monitoring
6. Integration with flight management systems
7. Advanced ML models (Deep Learning, LSTM for time-series)
8. Cloud deployment and scalability
9. Data export functionality (PDF, Excel)
10. Integration with external biometric devices

---

## Support and Troubleshooting

### Common Issues:

1. **Database Connection Error**: Ensure MySQL is running and database exists
2. **Migration Errors**: Clear migration history and re-run migrations
3. **Model Training Issues**: Verify dataset format and feature count
4. **Real-Time Monitoring Issues**: Check Redis and Channels configuration
5. **Static Files Not Loading**: Run `python manage.py collectstatic`

### Logs and Debugging:

- Application logs are available in the audit log table
- Django debug toolbar can be enabled for development
- ML model training outputs are saved to model files
- Session reports provide detailed analysis for each flight

---

**Last Updated**: 2026-04-17
**Project Version**: 1.0
**Status**: Active Development

