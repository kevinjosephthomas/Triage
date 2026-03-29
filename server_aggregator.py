import os
import pandas as pd
import numpy as np
import joblib
import warnings

# 1. Silence Noise
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# 2. Load Validation Data
# We increase the sample to 2000 for better "diversity" in the meta-learner
try:
    df_val = pd.read_csv('synthetic_medical_triage.csv').sample(2000, random_state=42)
except FileNotFoundError:
    print("CSV not found. Run your data generation script first.")
    exit()

y_val = df_val['triage_level']

# 3. Preprocess (One-Hot Encoding to match Clinic Training)
df_processed = pd.get_dummies(df_val.drop(columns=['triage_level', 'clinic_id', 'reward'], errors='ignore'))

# 4. Load Clinic Models
print("--- Loading Local Specialist Models ---")
m1 = tf.keras.models.load_model('clinic_1_model.h5')
m2 = joblib.load('clinic_2_model.pkl')
m3 = joblib.load('clinic_3_model.pkl')

# 5. Feature Alignment Helper
def align(df, expected_features):
    for col in expected_features:
        if col not in df.columns:
            df[col] = 0
    return df[expected_features].astype(np.float32)

# 6. Generate Predictions (The Meta-Features)
print("--- Generating Specialist Opinions ---")
feat2 = m2.feature_names_in_
feat3 = m3.feature_names_in_

# Clinic 1 (NN)
X1 = align(df_processed.copy(), list(feat3))
p1 = np.argmax(m1.predict(X1, verbose=0), axis=1)

# Clinic 2 (RF)
X2 = align(df_processed.copy(), feat2)
p2 = m2.predict(X2)

# Clinic 3 (RL/GBM)
X3 = align(df_processed.copy(), feat3)
p3 = m3.predict(X3)

# Combine into a "Voter Matrix"
meta_features = np.column_stack((p1, p2, p3))

# 7. Train Balanced Meta-Learner
print("--- Training Balanced Consolidator ---")
# 'balanced' class_weight fixes the issue where the model predicts only one level
meta_model = RandomForestClassifier(
    n_estimators=100, 
    class_weight='balanced', 
    max_depth=5, 
    random_state=42
)
meta_model.fit(meta_features, y_val)

# 8. Integrity Check
final_preds = meta_model.predict(meta_features)
unique_labels = np.unique(final_preds)

print("\n" + "="*40)
print(f"CONSOLIDATED ACCURACY: {accuracy_score(y_val, final_preds):.4f}")
print(f"UNIQUE LEVELS PREDICTED: {unique_labels}")
print("="*40)

if len(unique_labels) < 2:
    print("🚨 ALERT: Model is still biased. Check if your CSV has multiple triage levels!")
else:
    print("✅ Success: Model is distinguishing between different triage levels.")

# 9. Save
joblib.dump(meta_model, 'consolidated_global_model.pkl')
print("\nGlobal Consolidator Saved as 'consolidated_global_model.pkl'")