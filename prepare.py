import pandas as pd
import numpy as np

# Load your dataset
df = pd.read_csv('synthetic_medical_triage.csv')

# Define core features
core_features = [
    'age', 'heart_rate', 'systolic_blood_pressure', 'oxygen_saturation', 
    'body_temperature', 'pain_level', 'chronic_disease_count', 
    'previous_er_visits', 'arrival_mode'
]

# --- CLINIC 1: URGENT CARE (Stable/Low Risk) ---
# Filter for mostly Low (0) and Medium (1) triage levels
clinic_1_df = df[df['triage_level'].isin([0, 1])].sample(frac=0.7, random_state=42)
clinic_1_df['travel_history'] = 0 # Not tracked here

# --- CLINIC 2: ELDERLY CARE (Age Focus) ---
# Filter for patients over 65
clinic_2_df = df[df['age'] > 65].copy()
clinic_2_df['travel_history'] = 0 # Not tracked here

# --- CLINIC 3: INTERNATIONAL CLINIC (Risk/Travel Focus) ---
# Take a general sample and inject the 'travel_history' feature
remaining_df = df[~df.index.isin(clinic_1_df.index.union(clinic_2_df.index))].copy()

# Add travel_history: 15% probability of having traveled (1)
remaining_df['travel_history'] = np.random.binomial(1, 0.15, size=len(remaining_df))
clinic_3_df = remaining_df.copy()

# Save for Federated Clients
clinic_1_df.to_csv('clinic_urgent_care.csv', index=False)
clinic_2_df.to_csv('clinic_elderly_care.csv', index=False)
clinic_3_df.to_csv('clinic_international.csv', index=False)

print("Clinics created successfully with custom features.")