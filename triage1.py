import os
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import plotly.express as px
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

# Page config
st.set_page_config(page_title="AI Clinical Triage", layout="wide", page_icon="🏥")

# Silence TF logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf

# Groq client (IMPORTANT: put your key here OR use env)
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load models
@st.cache_resource
def load_models():
    try:
        m1 = tf.keras.models.load_model('clinic_1_model.h5')
        m2 = joblib.load('clinic_2_model.pkl')
        m3 = joblib.load('clinic_3_model.pkl')
        meta = joblib.load('consolidated_global_model.pkl')
        return m1, m2, m3, meta
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None, None, None

m1, m2, m3, meta = load_models()

# Chatbot function
def generate_medical_advice(patient_data, prediction_label):
    prompt = f"""
    You are a medical triage assistant.

    Patient Details:
    {patient_data}

    Predicted Triage Level:
    {prediction_label}

    Answer clearly:
    - What condition means
    - Risk level
    - What patient should do next
    Keep it simple and short.
    """

    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# Sidebar
st.sidebar.header("📋 Patient Data Entry")
with st.sidebar.form("form"):
    age = st.number_input("Age", 0, 120, 25)
    hr = st.number_input("Heart Rate", 40, 200, 72)
    sbp = st.number_input("Systolic BP", 70, 220, 120)
    spo2 = st.slider("SpO2", 70, 100, 98)
    temp = st.number_input("Temp", 34.0, 42.0, 36.6)
    pain = st.slider("Pain", 1, 10, 1)
    chronic = st.number_input("Chronic", 0, 10, 0)
    prev_er = st.number_input("ER Visits", 0, 20, 0)
    arrival = st.selectbox("Arrival", ["walk-in","ambulance","wheelchair","other"])
    travel = st.radio("Travel", ["No","Yes"])
    submit = st.form_submit_button("Run")

# Main
st.title("🏥 Federated AI Triage Dashboard")

if submit and m1 is not None:

    # Input processing
    arr = arrival.replace("-", "_")
    data = {
        'age': age,
        'heart_rate': hr,
        'systolic_blood_pressure': sbp,
        'oxygen_saturation': spo2,
        'body_temperature': temp,
        'pain_level': pain,
        'chronic_disease_count': chronic,
        'previous_er_visits': prev_er,
        'travel_history': 1 if travel=="Yes" else 0,
        'arrival_mode_ambulance': 1 if arr=="ambulance" else 0,
        'arrival_mode_other': 1 if arr=="other" else 0,
        'arrival_mode_walk_in': 1 if arr=="walk_in" else 0,
        'arrival_mode_wheelchair': 1 if arr=="wheelchair" else 0
    }

    df = pd.DataFrame([data])
    X = df[list(m3.feature_names_in_)].astype(np.float32)

    # Predictions
    p1 = int(np.argmax(m1.predict(X, verbose=0)))
    p2 = int(m2.predict(X)[0])
    p3 = int(m3.predict(X)[0])
    final = int(meta.predict(np.array([[p1,p2,p3]]))[0])

    # Result map
    triage_map = {
        0: ("LOW", "🟢 Stable"),
        1: ("MEDIUM", "🟡 Urgent"),
        2: ("HIGH", "🟠 Very Urgent"),
        3: ("CRITICAL", "🔴 Emergency")
    }

    label, desc = triage_map[final]

    # Display result
    st.metric("Final Triage", label)
    st.markdown(f"### {desc}")

    # Chart
    chart = pd.DataFrame({
        "Clinic":["A","B","C"],
        "Prediction":[p1,p2,p3]
    })
    st.bar_chart(chart.set_index("Clinic"))

    # -------- CHATBOT -------- #
    st.divider()
    st.subheader("💬 AI Doctor Chatbot")

    # Session memory
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Patient summary
    summary = f"""
    Age:{age}, HR:{hr}, BP:{sbp}, SpO2:{spo2},
    Temp:{temp}, Pain:{pain}, Chronic:{chronic},
    ER:{prev_er}, Travel:{travel}, Arrival:{arrival}
    """

    user_input = st.chat_input("Ask about patient...")

    if user_input:
        st.session_state.messages.append({"role":"user","content":user_input})
        st.chat_message("user").write(user_input)

        try:
            response = generate_medical_advice(summary + user_input, label)
        except Exception as e:
            response = f"Error: {e}"

        st.session_state.messages.append({"role":"assistant","content":response})
        st.chat_message("assistant").write(response)

else:
    st.info("Enter patient data and click Run")