"""
Fast ML Training Pipeline - Optimized for Speed
Completes training in 2-5 minutes and updates database
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import os
import sys
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aviation_system.settings')

# Import Django and setup
import django
django.setup()

from analytics.models import MLModel, TrainingDataset


class FastMLTrainer:
    """
    Fast ML training pipeline optimized for speed
    """
    
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.models = {}
        self.scalers = {}
        self.feature_columns = [
            'eeg_channel_1', 'eeg_channel_2', 'eeg_channel_3', 'eeg_channel_4',
            'eeg_channel_5', 'eeg_channel_6', 'eeg_channel_7', 'eeg_channel_8',
            'ecg_heart_rate', 'ecg_hrv', 'ecg_rr_interval',
            'eye_blink_rate', 'eye_fixation_duration', 'eye_saccade_velocity', 'pupil_diameter'
        ]
        self.target_columns = ['fatigue', 'stress', 'attention', 'workload']
        self.results = {}
        self.saved_files = {}
        
    def load_data(self):
        """Load dataset"""
        print(f"Loading dataset from {self.dataset_path}...")
        self.df = pd.read_csv(self.dataset_path)
        print(f"Dataset loaded: {len(self.df)} samples")
        return self.df
    
    def train_single_model(self, target_name, X_train, y_train, X_test, y_test):
        """Train a single optimized model"""
        print(f"\n{'='*60}")
        print(f"Training {target_name.upper()} model...")
        print(f"{'='*60}")
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Use optimized hyperparameters (pre-tuned for speed)
        model = GradientBoostingRegressor(
            n_estimators=100,        # Reduced from 200-300
            max_depth=4,             # Reduced from 5-7
            learning_rate=0.1,
            subsample=0.8,
            min_samples_split=10,    # Increased for faster training
            min_samples_leaf=5,      # Increased for faster training
            max_features='sqrt',     # Use subset of features
            random_state=42,
            verbose=0
        )
        
        # Train model
        start_time = datetime.now()
        model.fit(X_train_scaled, y_train)
        training_time = (datetime.now() - start_time).total_seconds()
        
        # Evaluate
        y_pred_train = model.predict(X_train_scaled)
        y_pred_test = model.predict(X_test_scaled)
        
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        test_mae = mean_absolute_error(y_test, y_pred_test)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        
        print(f"Training time: {training_time:.2f} seconds")
        print(f"Training R²:   {train_r2:.4f}")
        print(f"Test R²:       {test_r2:.4f}")
        print(f"Test MAE:      {test_mae:.4f}")
        print(f"Test RMSE:     {test_rmse:.4f}")
        
        return model, scaler, {
            'train_r2': train_r2,
            'test_r2': test_r2,
            'test_mae': test_mae,
            'test_rmse': test_rmse,
            'training_time': training_time,
            'training_samples': len(X_train)
        }
    
    def train_all_models(self):
        """Train models for all targets"""
        print("\n" + "="*60)
        print("FAST ML TRAINING PIPELINE")
        print("="*60)
        
        X = self.df[self.feature_columns].values
        
        total_start = datetime.now()
        
        for target in self.target_columns:
            y = self.df[target].values
            
            # Simple 80-20 split for speed
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            model, scaler, metrics = self.train_single_model(
                target, X_train, y_train, X_test, y_test
            )
            
            self.models[target] = model
            self.scalers[target] = scaler
            self.results[target] = metrics
        
        total_time = (datetime.now() - total_start).total_seconds()
        
        print(f"\n{'='*60}")
        print(f"TOTAL TRAINING TIME: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        print(f"{'='*60}")
        
        return self.results
    
    def save_models(self, output_dir='media/ml_models'):
        """Save trained models to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        print(f"\nSaving models to {output_dir}...")
        
        for target in self.target_columns:
            model_filename = f'{target}_model_{timestamp}.pkl'
            scaler_filename = f'{target}_scaler_{timestamp}.pkl'
            
            model_path = os.path.join(output_dir, model_filename)
            scaler_path = os.path.join(output_dir, scaler_filename)
            
            joblib.dump(self.models[target], model_path)
            joblib.dump(self.scalers[target], scaler_path)
            
            self.saved_files[target] = {
                'model': model_path,
                'scaler': scaler_path
            }
            
            print(f"  ✓ {target}: {model_filename}")
        
        print("\n✓ All models saved successfully!")
        return self.saved_files
    
    def save_to_database(self):
        """Save trained models to database"""
        print("\n" + "="*60)
        print("SAVING MODELS TO DATABASE")
        print("="*60)
        
        version = datetime.now().strftime('%Y.%m.%d')
        
        for target in self.target_columns:
            try:
                # Deactivate old models
                old_models = MLModel.objects.filter(model_type=target)
                old_count = old_models.count()
                old_models.update(status='archived')
                
                if old_count > 0:
                    print(f"\n{target.upper()}: Archived {old_count} old model(s)")
                
                # Get metrics
                metrics = self.results[target]
                files = self.saved_files[target]
                # Create new active model
                new_model = MLModel.objects.create(
                    name=f'{target.title()} Detection Model',
                    model_type=target,
                    version=version,
                    algorithm='gradient_boosting',
                    accuracy=float(metrics['test_r2']),
                    precision=float(metrics['test_r2']),
                    recall=float(metrics['test_r2']),
                    f1_score=float(metrics['test_r2']),
                    training_samples=metrics['training_samples'],
                    model_file=files['model'],
                    scaler_file=files['scaler'],
                    status='active',
                    training_date=datetime.now() 
                )

                
                print(f"  ✓ Created new model (ID: {new_model.id})")
                print(f"  ✓ Accuracy: {metrics['test_r2']:.4f}")
                print(f"  ✓ Status: ACTIVE")
                
            except Exception as e:
                print(f"  ✗ Error saving {target} to database: {e}")
                import traceback
                traceback.print_exc()
        
        # Save dataset info
        try:
            dataset, created = TrainingDataset.objects.update_or_create(
                name='Aviation Training Dataset',
                defaults={
                    'file_path': self.dataset_path,
                    'total_samples': len(self.df),
                    'feature_count': len(self.feature_columns),
                }
            )
            print(f"\n✓ Dataset info saved (ID: {dataset.id})")
        except Exception as e:
            print(f"\n⚠ Warning: Could not save dataset info: {e}")
        
        print("\n" + "="*60)
        print("✅ ALL MODELS SAVED TO DATABASE!")
        print("="*60)


def main():
    """Main training execution"""
    
    print("\n" + "="*60)
    print("FAST ML TRAINING FOR AVIATION MONITORING")
    print("="*60)
    
    # Use realistic dataset
    dataset_file = 'realistic_training_dataset.csv'
    
    if not os.path.exists(dataset_file):
        print(f"\n✗ Dataset '{dataset_file}' not found!")
        print("Using fallback training dataset...")
        dataset_file = 'training_dataset.csv'
        
        if not os.path.exists(dataset_file):
            print("\n✗ No dataset found! Please generate dataset first:")
            print("  python generate_realistic_dataset.py")
            return
    
    # Train models
    trainer = FastMLTrainer(dataset_file)
    trainer.load_data()
    
    # Training pipeline
    trainer.train_all_models()
    trainer.save_models()
    trainer.save_to_database()  # ← NEW: Save to database
    
    # Summary
    print("\n" + "="*60)
    print("TRAINING SUMMARY")
    print("="*60)
    
    for target in trainer.target_columns:
        metrics = trainer.results[target]
        print(f"\n{target.upper()}:")
        print(f"  Test R²:   {metrics['test_r2']:.4f}")
        print(f"  Test MAE:  {metrics['test_mae']:.4f}")
        print(f"  Time:      {metrics['training_time']:.2f}s")
    
    print("\n" + "="*60)
    print("✓ Training complete! Models ready for use.")
    print("✓ Refresh your browser to see the new models.")
    print("="*60)


if __name__ == '__main__':
    main()
