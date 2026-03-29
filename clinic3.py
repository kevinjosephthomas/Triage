import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import GradientBoostingClassifier

# Load Clinic 3 Data
df = pd.read_csv('clinic_international.csv')

# RL Logic: We define a 'Reward' column based on clinical safety
# Penalty is high (-50) if Travel=1 and Temp>38 but triage is 'Low'
def calculate_reward(row):
    is_infectious_risk = (row['travel_history'] == 1 and row['body_temperature'] > 38.0)
    if is_infectious_risk and row['triage_level'] > 1: # 0=Critical, 1=High
        return -50 # High penalty for under-triaging infectious risk
    return 10 # Reward for following data patterns

df['reward'] = df.apply(calculate_reward, axis=1)

# In a structured data setting, RL can be implemented as a 'Policy Gradient' 
# or a Weighted Gradient Booster (XGBoost style)
X = df.drop(['triage_level', 'reward'], axis=1)
# Encode categorical arrival_mode column
X = pd.get_dummies(X, columns=['arrival_mode'], drop_first=True)
y = df['triage_level']

# Train with sample weights (RL Reward influence)
# We shift rewards to positive weights for the classifier
weights = df['reward'] + abs(df['reward'].min()) + 1 

rl_policy_model = GradientBoostingClassifier()
rl_policy_model.fit(X, y, sample_weight=weights)

joblib.dump(rl_policy_model, 'clinic_3_model.pkl')
print("Clinic 3: RL-weighted Policy Model Training Complete.")