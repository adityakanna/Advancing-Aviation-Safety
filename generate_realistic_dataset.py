"""
Realistic Aviation Mental State Dataset Generator
Based on actual physiological research and aviation psychology studies
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

class AviationPhysiologySimulator:
    """
    Simulates realistic physiological data based on aviation research
    References:
    - NASA Task Load Index (TLX)
    - International Civil Aviation Organization (ICAO) fatigue studies
    - Aviation Safety Reporting System (ASRS) data patterns
    """
    
    def __init__(self, seed=42):
        np.random.seed(seed)
        random.seed(seed)
        
    def generate_baseline_eeg(self, mental_state):
        """
        Generate EEG data based on brainwave frequency bands
        Delta (0.5-4 Hz): Deep sleep, unconscious
        Theta (4-8 Hz): Drowsiness, light sleep, meditation
        Alpha (8-13 Hz): Relaxed, calm, conscious
        Beta (13-30 Hz): Alert, focused, active thinking
        Gamma (30-100 Hz): High-level information processing
        """
        
        if mental_state == 'alert_optimal':
            # Optimal state: High beta, moderate alpha, low theta/delta
            delta = np.random.uniform(5, 15)      # Low delta
            theta = np.random.uniform(10, 20)     # Low theta
            alpha = np.random.uniform(25, 35)     # Moderate-high alpha
            beta = np.random.uniform(30, 45)      # High beta
            gamma = np.random.uniform(5, 15)      # Moderate gamma
            
        elif mental_state == 'normal_cruise':
            # Normal cruise: Balanced state
            delta = np.random.uniform(10, 20)
            theta = np.random.uniform(15, 25)
            alpha = np.random.uniform(20, 30)
            beta = np.random.uniform(25, 35)
            gamma = np.random.uniform(5, 12)
            
        elif mental_state == 'fatigued':
            # Fatigue: High theta/delta, low beta
            delta = np.random.uniform(25, 40)     # High delta
            theta = np.random.uniform(30, 50)     # High theta
            alpha = np.random.uniform(15, 25)     # Reduced alpha
            beta = np.random.uniform(10, 20)      # Low beta
            gamma = np.random.uniform(2, 8)       # Low gamma
            
        elif mental_state == 'high_stress':
            # Stress: High beta, low alpha
            delta = np.random.uniform(8, 18)
            theta = np.random.uniform(12, 22)
            alpha = np.random.uniform(10, 18)     # Low alpha
            beta = np.random.uniform(40, 60)      # Very high beta
            gamma = np.random.uniform(8, 18)      # Elevated gamma
            
        elif mental_state == 'overload':
            # Cognitive overload: Chaotic patterns
            delta = np.random.uniform(15, 30)
            theta = np.random.uniform(20, 35)
            alpha = np.random.uniform(12, 22)
            beta = np.random.uniform(35, 55)
            gamma = np.random.uniform(10, 20)
            
        elif mental_state == 'drowsy':
            # Drowsiness: Very high theta, low beta
            delta = np.random.uniform(30, 45)
            theta = np.random.uniform(40, 60)     # Very high theta
            alpha = np.random.uniform(18, 28)
            beta = np.random.uniform(8, 15)       # Very low beta
            gamma = np.random.uniform(2, 6)
            
        else:  # microsleep or severe fatigue
            delta = np.random.uniform(40, 60)
            theta = np.random.uniform(45, 65)
            alpha = np.random.uniform(10, 20)
            beta = np.random.uniform(5, 12)
            gamma = np.random.uniform(1, 5)
        
        return delta, theta, alpha, beta, gamma
    
    def generate_eeg_channels(self, mental_state):
        """
        Generate 8-channel EEG data
        Channels: Fp1, Fp2, F3, F4, C3, C4, P3, P4 (10-20 system)
        """
        delta, theta, alpha, beta, gamma = self.generate_baseline_eeg(mental_state)
        
        # Frontal channels (Fp1, Fp2) - Executive function
        frontal_bias = 1.1 if mental_state in ['high_stress', 'overload'] else 1.0
        ch1 = (alpha * 0.3 + beta * 0.5 + theta * 0.2) * frontal_bias + np.random.normal(0, 3)
        ch2 = (alpha * 0.3 + beta * 0.5 + theta * 0.2) * frontal_bias + np.random.normal(0, 3)
        
        # Frontal-central (F3, F4) - Motor planning, attention
        ch3 = (alpha * 0.4 + beta * 0.4 + theta * 0.2) + np.random.normal(0, 2.5)
        ch4 = (alpha * 0.4 + beta * 0.4 + theta * 0.2) + np.random.normal(0, 2.5)
        
        # Central (C3, C4) - Sensorimotor
        ch5 = (alpha * 0.5 + beta * 0.3 + theta * 0.2) + np.random.normal(0, 2)
        ch6 = (alpha * 0.5 + beta * 0.3 + theta * 0.2) + np.random.normal(0, 2)
        
        # Parietal (P3, P4) - Visual-spatial processing
        parietal_bias = 1.15 if mental_state == 'alert_optimal' else 1.0
        ch7 = (alpha * 0.6 + beta * 0.2 + theta * 0.2) * parietal_bias + np.random.normal(0, 2)
        ch8 = (alpha * 0.6 + beta * 0.2 + theta * 0.2) * parietal_bias + np.random.normal(0, 2)
        
        return {
            'eeg_channel_1': np.clip(ch1, 5, 70),
            'eeg_channel_2': np.clip(ch2, 5, 70),
            'eeg_channel_3': np.clip(ch3, 5, 70),
            'eeg_channel_4': np.clip(ch4, 5, 70),
            'eeg_channel_5': np.clip(ch5, 5, 70),
            'eeg_channel_6': np.clip(ch6, 5, 70),
            'eeg_channel_7': np.clip(ch7, 5, 70),
            'eeg_channel_8': np.clip(ch8, 5, 70),
        }
    
    def generate_ecg_data(self, mental_state, age=35, fitness_level='average'):
        """
        Generate realistic ECG metrics
        Based on autonomic nervous system responses
        """
        
        # Age-adjusted max heart rate: 220 - age
        max_hr = 220 - age
        
        # Fitness level affects resting HR
        if fitness_level == 'high':
            resting_hr = np.random.uniform(50, 60)
        elif fitness_level == 'average':
            resting_hr = np.random.uniform(60, 75)
        else:
            resting_hr = np.random.uniform(75, 85)
        
        if mental_state == 'alert_optimal':
            hr = resting_hr + np.random.uniform(5, 15)
            hrv = np.random.uniform(55, 75)      # High HRV = good
            rr = 60000 / hr + np.random.uniform(-50, 50)
            
        elif mental_state == 'normal_cruise':
            hr = resting_hr + np.random.uniform(0, 10)
            hrv = np.random.uniform(45, 65)
            rr = 60000 / hr + np.random.uniform(-40, 40)
            
        elif mental_state == 'fatigued':
            hr = resting_hr - np.random.uniform(5, 15)  # Lower HR when fatigued
            hrv = np.random.uniform(25, 45)              # Lower HRV
            rr = 60000 / hr + np.random.uniform(-60, 60)
            
        elif mental_state == 'high_stress':
            hr = resting_hr + np.random.uniform(20, 40)  # Elevated HR
            hrv = np.random.uniform(20, 35)              # Very low HRV
            rr = 60000 / hr + np.random.uniform(-30, 30)
            
        elif mental_state == 'overload':
            hr = resting_hr + np.random.uniform(25, 45)
            hrv = np.random.uniform(15, 30)
            rr = 60000 / hr + np.random.uniform(-40, 40)
            
        elif mental_state == 'drowsy':
            hr = resting_hr - np.random.uniform(10, 20)
            hrv = np.random.uniform(20, 40)
            rr = 60000 / hr + np.random.uniform(-70, 70)
            
        else:  # severe fatigue
            hr = resting_hr - np.random.uniform(15, 25)
            hrv = np.random.uniform(15, 30)
            rr = 60000 / hr + np.random.uniform(-80, 80)
        
        return {
            'ecg_heart_rate': np.clip(hr, 45, 180),
            'ecg_hrv': np.clip(hrv, 10, 100),
            'ecg_rr_interval': np.clip(rr, 333, 1333),  # 45-180 bpm range
        }
    
    def generate_eye_tracking(self, mental_state):
        """
        Generate eye tracking metrics
        Based on oculomotor research in aviation
        """
        
        if mental_state == 'alert_optimal':
            blink_rate = np.random.uniform(15, 22)       # Normal blink rate
            fixation = np.random.uniform(200, 280)        # Optimal fixation
            saccade = np.random.uniform(320, 420)         # Fast saccades
            pupil = np.random.uniform(4.2, 5.0)          # Moderate pupil size
            
        elif mental_state == 'normal_cruise':
            blink_rate = np.random.uniform(17, 25)
            fixation = np.random.uniform(250, 320)
            saccade = np.random.uniform(280, 380)
            pupil = np.random.uniform(3.8, 4.6)
            
        elif mental_state == 'fatigued':
            blink_rate = np.random.uniform(28, 40)       # Increased blinks
            fixation = np.random.uniform(350, 500)        # Longer fixations
            saccade = np.random.uniform(200, 280)         # Slower saccades
            pupil = np.random.uniform(3.2, 4.0)          # Smaller pupils
            
        elif mental_state == 'high_stress':
            blink_rate = np.random.uniform(25, 35)       # Increased blinks
            fixation = np.random.uniform(150, 220)        # Rapid scanning
            saccade = np.random.uniform(350, 480)         # Fast eye movements
            pupil = np.random.uniform(5.0, 6.5)          # Dilated pupils
            
        elif mental_state == 'overload':
            blink_rate = np.random.uniform(30, 42)
            fixation = np.random.uniform(120, 200)        # Very short fixations
            saccade = np.random.uniform(380, 520)
            pupil = np.random.uniform(5.5, 7.0)
            
        elif mental_state == 'drowsy':
            blink_rate = np.random.uniform(35, 50)       # Very high blink rate
            fixation = np.random.uniform(400, 600)        # Long, unfocused fixations
            saccade = np.random.uniform(150, 230)         # Very slow saccades
            pupil = np.random.uniform(2.8, 3.6)          # Constricted pupils
            
        else:  # microsleep
            blink_rate = np.random.uniform(45, 65)
            fixation = np.random.uniform(500, 800)
            saccade = np.random.uniform(100, 180)
            pupil = np.random.uniform(2.5, 3.2)
        
        return {
            'eye_blink_rate': np.clip(blink_rate, 5, 70),
            'eye_fixation_duration': np.clip(fixation, 80, 800),
            'eye_saccade_velocity': np.clip(saccade, 80, 600),
            'pupil_diameter': np.clip(pupil, 2.0, 8.0),
        }
    
    def calculate_mental_state_labels(self, mental_state, flight_phase, time_of_day):
        """
        Calculate ground truth labels based on physiological state
        Values range from 0 (optimal) to 1 (critical)
        """
        
        # Base values for each state
        state_profiles = {
            'alert_optimal': {
                'fatigue': (0.05, 0.15),
                'stress': (0.15, 0.25),
                'attention': (0.85, 0.95),
                'workload': (0.25, 0.40)
            },
            'normal_cruise': {
                'fatigue': (0.15, 0.30),
                'stress': (0.20, 0.35),
                'attention': (0.65, 0.80),
                'workload': (0.35, 0.50)
            },
            'fatigued': {
                'fatigue': (0.65, 0.85),
                'stress': (0.30, 0.45),
                'attention': (0.20, 0.40),
                'workload': (0.60, 0.75)
            },
            'high_stress': {
                'fatigue': (0.40, 0.55),
                'stress': (0.75, 0.90),
                'attention': (0.50, 0.65),
                'workload': (0.75, 0.90)
            },
            'overload': {
                'fatigue': (0.55, 0.70),
                'stress': (0.80, 0.95),
                'attention': (0.25, 0.45),
                'workload': (0.85, 0.98)
            },
            'drowsy': {
                'fatigue': (0.75, 0.92),
                'stress': (0.25, 0.40),
                'attention': (0.10, 0.30),
                'workload': (0.70, 0.85)
            },
            'microsleep': {
                'fatigue': (0.88, 0.98),
                'stress': (0.20, 0.35),
                'attention': (0.02, 0.15),
                'workload': (0.75, 0.92)
            }
        }
        
        profile = state_profiles[mental_state]
        
        # Base values
        fatigue = np.random.uniform(*profile['fatigue'])
        stress = np.random.uniform(*profile['stress'])
        attention = np.random.uniform(*profile['attention'])
        workload = np.random.uniform(*profile['workload'])
        
        # Flight phase modifiers
        if flight_phase == 'takeoff':
            stress += np.random.uniform(0.05, 0.15)
            workload += np.random.uniform(0.10, 0.20)
            attention += np.random.uniform(0.05, 0.15)
        elif flight_phase == 'landing':
            stress += np.random.uniform(0.10, 0.20)
            workload += np.random.uniform(0.15, 0.25)
            attention += np.random.uniform(0.05, 0.15)
        elif flight_phase == 'emergency':
            stress += np.random.uniform(0.20, 0.35)
            workload += np.random.uniform(0.20, 0.30)
            fatigue += np.random.uniform(0.05, 0.15)
        
        # Time of day modifiers (circadian rhythm)
        if time_of_day in ['night', 'early_morning']:  # 00:00-06:00
            fatigue += np.random.uniform(0.10, 0.25)
            attention -= np.random.uniform(0.10, 0.20)
        elif time_of_day == 'afternoon':  # 14:00-16:00
            fatigue += np.random.uniform(0.05, 0.15)  # Post-lunch dip
        
        # Clip values to valid range
        return {
            'fatigue': np.clip(fatigue, 0, 1),
            'stress': np.clip(stress, 0, 1),
            'attention': np.clip(attention, 0, 1),
            'workload': np.clip(workload, 0, 1),
        }
    
    def generate_sample(self, mental_state=None, flight_phase='cruise', time_of_day='day'):
        """Generate a single realistic sample"""
        
        if mental_state is None:
            mental_state = random.choice([
                'alert_optimal', 'normal_cruise', 'fatigued', 
                'high_stress', 'overload', 'drowsy', 'microsleep'
            ])
        
        # Generate physiological data
        sample = {}
        sample.update(self.generate_eeg_channels(mental_state))
        sample.update(self.generate_ecg_data(mental_state, 
                                             age=random.randint(25, 55),
                                             fitness_level=random.choice(['high', 'average', 'low'])))
        sample.update(self.generate_eye_tracking(mental_state))
        
        # Generate labels
        labels = self.calculate_mental_state_labels(mental_state, flight_phase, time_of_day)
        sample.update(labels)
        
        # Add metadata
        sample['mental_state_category'] = mental_state
        sample['flight_phase'] = flight_phase
        sample['time_of_day'] = time_of_day
        
        return sample

def generate_realistic_dataset(n_samples=15000, output_file='realistic_training_dataset.csv'):
    """
    Generate realistic aviation mental state dataset
    """
    
    print("="*70)
    print("REALISTIC AVIATION MENTAL STATE DATASET GENERATOR")
    print("="*70)
    print(f"\nGenerating {n_samples} realistic physiological samples...")
    print("Based on aviation psychology and human factors research\n")
    
    simulator = AviationPhysiologySimulator()
    
    # Define realistic distribution of states
    state_distribution = {
        'alert_optimal': 0.15,      # 15% - Peak performance
        'normal_cruise': 0.35,      # 35% - Normal operations
        'fatigued': 0.20,          # 20% - Fatigue states
        'high_stress': 0.12,       # 12% - High stress situations
        'overload': 0.08,          # 8% - Cognitive overload
        'drowsy': 0.07,            # 7% - Drowsiness
        'microsleep': 0.03,        # 3% - Critical fatigue
    }
    
    flight_phases = ['cruise', 'takeoff', 'landing', 'emergency']
    flight_phase_weights = [0.70, 0.10, 0.15, 0.05]
    
    times_of_day = ['morning', 'day', 'afternoon', 'evening', 'night', 'early_morning']
    time_weights = [0.15, 0.30, 0.15, 0.20, 0.15, 0.05]
    
    data = []
    
    for i in range(n_samples):
        if (i + 1) % 1000 == 0:
            print(f"Generated {i + 1}/{n_samples} samples...")
        
        # Select state based on distribution
        mental_state = np.random.choice(
            list(state_distribution.keys()),
            p=list(state_distribution.values())
        )
        
        flight_phase = np.random.choice(flight_phases, p=flight_phase_weights)
        time_of_day = np.random.choice(times_of_day, p=time_weights)
        
        sample = simulator.generate_sample(mental_state, flight_phase, time_of_day)
        data.append(sample)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Reorder columns
    feature_cols = [
        'eeg_channel_1', 'eeg_channel_2', 'eeg_channel_3', 'eeg_channel_4',
        'eeg_channel_5', 'eeg_channel_6', 'eeg_channel_7', 'eeg_channel_8',
        'ecg_heart_rate', 'ecg_hrv', 'ecg_rr_interval',
        'eye_blink_rate', 'eye_fixation_duration', 'eye_saccade_velocity', 'pupil_diameter'
    ]
    label_cols = ['fatigue', 'stress', 'attention', 'workload']
    meta_cols = ['mental_state_category', 'flight_phase', 'time_of_day']
    
    df = df[feature_cols + label_cols + meta_cols]
    
    # Save dataset
    df.to_csv(output_file, index=False)
    
    print(f"\n{'='*70}")
    print("DATASET GENERATION COMPLETE")
    print(f"{'='*70}")
    print(f"\nDataset saved to: {output_file}")
    print(f"Total samples: {len(df)}")
    print(f"\nFeature Statistics:")
    print(f"  - EEG channels: 8")
    print(f"  - ECG metrics: 3")
    print(f"  - Eye tracking metrics: 4")
    print(f"  - Total features: 15")
    print(f"\nLabel Distribution:")
    print(df['mental_state_category'].value_counts())
    print(f"\nLabel Statistics:")
    print(df[label_cols].describe())
    print(f"\n{'='*70}\n")
    
    return df

if __name__ == '__main__':
    # Generate training dataset (12000 samples)
    print("Generating TRAINING dataset...")
    train_df = generate_realistic_dataset(12000, 'realistic_training_dataset.csv')
    
    print("\nGenerating VALIDATION dataset...")
    val_df = generate_realistic_dataset(3000, 'realistic_validation_dataset.csv')
    
    print("\nGenerating TEST dataset...")
    test_df = generate_realistic_dataset(2000, 'realistic_test_dataset.csv')
    
    print("\n" + "="*70)
    print("ALL DATASETS GENERATED SUCCESSFULLY!")
    print("="*70)
    print("\nFiles created:")
    print("  1. realistic_training_dataset.csv (12,000 samples)")
    print("  2. realistic_validation_dataset.csv (3,000 samples)")
    print("  3. realistic_test_dataset.csv (2,000 samples)")
    print("\nYou can now use these datasets for production ML model training!")
    print("="*70)
