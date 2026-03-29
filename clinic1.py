import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load Clinic 1 Data
df = pd.read_csv('clinic_urgent_care.csv')
X = df.drop(['triage_level'], axis=1)
# Encode categorical arrival_mode column
X = pd.get_dummies(X, columns=['arrival_mode'], drop_first=True)
y = pd.get_dummies(df['triage_level']) # One-hot encoding for Triage Levels

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Scale features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)

# Build Keras Model
model_nn = tf.keras.Sequential([
    tf.keras.layers.Dense(32, activation='relu', input_shape=(X_train.shape[1],)),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(y.shape[1], activation='softmax')
])

model_nn.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model_nn.fit(X_train, y_train, epochs=10, batch_size=32, verbose=1)

model_nn.save('clinic_1_model.h5')
print("Clinic 1: Neural Network Training Complete.")