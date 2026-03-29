import os
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import plotly.express as px

# 1. Page Configuration (Must be first)
st.set_page_config(page_title="AI Clinical Triage", layout="wide", page_icon="🏥")

# 2. Silence TensorFlow noise
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf

# 3. Load All Models
@st.cache_resource
def load_all_models():
    try:
        m1 = tf.keras.models.load_model('clinic_1_model.h5')
        m2 = joblib.load('clinic_2_model.pkl')
        m3 = joblib.load('clinic_3_model.pkl')
        meta = joblib.load('consolidated_global_model.pkl')
        return m1, m2, m3, meta
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None, None, None

m1, m2, m3, meta = load_all_models()

# 4. Sidebar - Patient Input
st.sidebar.header("📋 Patient Data Entry")
with st.sidebar.form("triage_form"):
    age = st.number_input("Age", 0, 120, 25)
    hr = st.number_input("Heart Rate (BPM)", 40, 200, 72)
    sbp = st.number_input("Systolic BP (mmHg)", 70, 220, 120)
    spo2 = st.slider("Oxygen Saturation (%)", 70, 100, 98)
    temp = st.number_input("Temperature (°C)", 34.0, 42.0, 36.6)
    pain = st.slider("Pain Level (1-10)", 1, 10, 1)
    chronic = st.number_input("Chronic Conditions", 0, 10, 0)
    prev_er = st.number_input("Prev ER Visits", 0, 20, 0)
    arrival = st.selectbox("Arrival Mode", ["walk-in", "ambulance", "wheelchair", "other"])
    travel = st.radio("Recent International Travel?", ["No", "Yes"])
    submit = st.form_submit_button("🔥 Run Federated Analysis")

# 5. Main Dashboard
st.title("🏥 Federated AI Triage Dashboard")

if not submit:
    st.info("👈 Enter patient vitals in the sidebar and click 'Run Federated Analysis' to see the consolidated AI decision.")

if submit and m1 is not None:
    # --- Data Processing ---
    sanitized_arrival = arrival.replace("-", "_").replace(" ", "_")
    input_dict = {
        'age': age, 'heart_rate': hr, 'systolic_blood_pressure': sbp,
        'oxygen_saturation': spo2, 'body_temperature': temp, 'pain_level': pain,
        'chronic_disease_count': chronic, 'previous_er_visits': prev_er,
        'travel_history': 1 if travel == "Yes" else 0,
        'arrival_mode_ambulance': 1 if sanitized_arrival == "ambulance" else 0,
        'arrival_mode_other': 1 if sanitized_arrival == "other" else 0,
        'arrival_mode_walk_in': 1 if sanitized_arrival == "walk_in" else 0,
        'arrival_mode_wheelchair': 1 if sanitized_arrival == "wheelchair" else 0
    }
    input_df = pd.DataFrame([input_dict])
    golden_features = list(m3.feature_names_in_)
    X_final = input_df[golden_features].astype(np.float32)

    # --- Predictions ---
    p1 = int(np.argmax(m1.predict(X_final, verbose=0), axis=1)[0])
    p2 = int(m2.predict(X_final)[0])
    p3 = int(m3.predict(X_final)[0])
    
    # Final meta-prediction
    res = meta.predict(np.array([[p1, p2, p3]]))[0]
    final_decision = int(res) # FIX: Force cast to standard Python Int

    # --- VISUALS ---
    st.subheader("🫀 Vital Signs Monitoring")
    v1, v2, v3 = st.columns(3)
    
    with v1: # SpO2 Gauge
        fig_spo2 = go.Figure(go.Indicator(
            mode = "gauge+number", value = spo2, title = {'text': "Oxygen Saturation (%)"},
            gauge = {'axis': {'range': [70, 100]}, 'bar': {'color': "darkblue"},
                     'steps': [{'range': [70, 90], 'color': "red"}, {'range': [90, 95], 'color': "yellow"}, {'range': [95, 100], 'color': "green"}]}))
        st.plotly_chart(fig_spo2, use_container_width=True)

    with v2: # Heart Rate Gauge
        fig_hr = go.Figure(go.Indicator(
            mode = "gauge+number", value = hr, title = {'text': "Heart Rate (BPM)"},
            gauge = {'axis': {'range': [40, 200]}, 'bar': {'color': "darkred"},
                     'steps': [{'range': [40, 60], 'color': "gray"}, {'range': [60, 100], 'color': "green"}, {'range': [100, 200], 'color': "red"}]}))
        st.plotly_chart(fig_hr, use_container_width=True)
        
    with v3: # Final Result Card
        triage_map = {
            0: ("LOW (Level 3)", "🟢 Stable", "green"),
            1: ("MEDIUM (Level 2)", "🟡 Urgent", "orange"),
            2: ("HIGH (Level 1)", "🟠 Very Urgent", "darkorange"),
            3: ("CRITICAL (Level 0)", "🔴 Emergency", "red")
        }
        label, desc, color = triage_map[final_decision]
        st.metric(label="CONSOLIDATED TRIAGE", value=label)
        st.markdown(f"<h1 style='text-align: center; color: {color};'>{desc}</h1>", unsafe_allow_html=True)
        # FIX: The cast to int() above prevents the int64 error here
        st.progress((final_decision + 1) * 25)

    st.divider()

    # Clinic Consensus Chart
    st.subheader("🤝 Federated Model Consensus")
    chart_data = pd.DataFrame({
        "Clinic Node": ["Urgent Care", "Elderly Care", "International"],
        "Predicted Level": [p1, p2, p3]
    })
    
    fig_cons = px.bar(chart_data, x="Clinic Node", y="Predicted Level", 
                      range_y=[0, 3], color="Predicted Level",
                      color_continuous_scale=["green", "yellow", "orange", "red"],
                      labels={"Predicted Level": "Urgency (0-3)"},
                      title="Comparison of Local Clinic Predictions")
    st.plotly_chart(fig_cons, use_container_width=True)

    st.caption("The Meta-Learner weights these inputs based on historical performance and patient complexity.")