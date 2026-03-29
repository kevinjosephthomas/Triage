from sklearn.ensemble import RandomForestClassifier
import joblib
import pandas as pd

# Load Clinic 2 Data
df = pd.read_csv('clinic_elderly_care.csv')
X = df.drop(['triage_level'], axis=1)
# Encode categorical arrival_mode column
X = pd.get_dummies(X, columns=['arrival_mode'], drop_first=True)
y = df['triage_level']

# Initialize and Train
rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
rf_model.fit(X, y)

# Save the model
joblib.dump(rf_model, 'clinic_2_model.pkl')
print("Clinic 2: Random Forest Training Complete.")