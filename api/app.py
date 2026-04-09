import os
import sys
import json
import urllib.request
import urllib.error
import numpy as np
import pandas as pd
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

app = Flask(__name__)
CORS(app)

# ── Model paths (relative to this file's directory) ──────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(BASE, '..')   # hca_project_1/

m1 = m2 = m3 = meta = None

def load_models():
    global m1, m2, m3, meta
    try:
        import tensorflow as tf
        m1   = tf.keras.models.load_model(os.path.join(ROOT, 'clinic_1_model.h5'))
        m2   = joblib.load(os.path.join(ROOT, 'clinic_2_model.pkl'))
        m3   = joblib.load(os.path.join(ROOT, 'clinic_3_model.pkl'))
        meta = joblib.load(os.path.join(ROOT, 'consolidated_global_model.pkl'))
        print("✅  All models loaded successfully.")
    except Exception as e:
        print(f"❌  Error loading models: {e}", file=sys.stderr)
        raise

load_models()

# ── Triage map ────────────────────────────────────────────────────────────────
TRIAGE_MAP = {
    0: {"label": "LOW (Level 3)",      "desc": "Stable",       "color": "#22c55e"},
    1: {"label": "MEDIUM (Level 2)",   "desc": "Urgent",       "color": "#eab308"},
    2: {"label": "HIGH (Level 1)",     "desc": "Very Urgent",  "color": "#f97316"},
    3: {"label": "CRITICAL (Level 0)", "desc": "Emergency",    "color": "#ef4444"},
}

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(force=True)

        arrival = data.get('arrival_mode', 'walk-in')
        sanitized = arrival.replace('-', '_').replace(' ', '_')

        input_dict = {
            'age':                        float(data['age']),
            'heart_rate':                 float(data['heart_rate']),
            'systolic_blood_pressure':    float(data['systolic_blood_pressure']),
            'oxygen_saturation':          float(data['oxygen_saturation']),
            'body_temperature':           float(data['body_temperature']),
            'pain_level':                 float(data['pain_level']),
            'chronic_disease_count':      float(data['chronic_disease_count']),
            'previous_er_visits':         float(data['previous_er_visits']),
            'travel_history':             1.0 if data.get('travel_history') == 'Yes' else 0.0,
            'arrival_mode_ambulance':     1.0 if sanitized == 'ambulance'  else 0.0,
            'arrival_mode_other':         1.0 if sanitized == 'other'      else 0.0,
            'arrival_mode_walk_in':       1.0 if sanitized == 'walk_in'    else 0.0,
            'arrival_mode_wheelchair':    1.0 if sanitized == 'wheelchair' else 0.0,
        }

        input_df = pd.DataFrame([input_dict])
        golden_features = list(m3.feature_names_in_)
        X_final = input_df[golden_features].astype(np.float32)

        p1 = int(np.argmax(m1.predict(X_final, verbose=0), axis=1)[0])
        p2 = int(m2.predict(X_final)[0])
        p3 = int(m3.predict(X_final)[0])

        final_decision = int(meta.predict(np.array([[p1, p2, p3]]))[0])

        result = TRIAGE_MAP[final_decision]
        return jsonify({
            'p1': p1,
            'p2': p2,
            'p3': p3,
            'final_decision': final_decision,
            'label':  result['label'],
            'desc':   result['desc'],
            'color':  result['color'],
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json(force=True)
        patient_data = data.get('patient_data')
        triage_result = data.get('triage_result')

        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            return jsonify({'error': 'GROQ_API_KEY is missing.'}), 500

        system_prompt = """You are a senior clinical decision support AI. Your task is to provide clinical recommendations based on the provided patient data.
You MUST strictly follow this format and ONLY this format for your response:

### Clinical Impression
(Write a concise 2-3 sentence clinical impression based on the case)

### Actionable Recommendations
- (Point 1)
- (Point 2)
- (Point 3)

CRITICAL RULE: DO NOT list or repeat the patient's vitals. DO NOT list or repeat the triage status. ONLY output the Clinical Impression and Actionable Recommendations."""
        user_prompt = f"Patient Vitals & History:\n{patient_data}\n\nTriage Assessment:\n{triage_result}"

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2
        }

        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req) as response:
                result_json = json.loads(response.read().decode('utf-8'))
                analysis = result_json["choices"][0]["message"]["content"]
                return jsonify({"analysis": analysis})
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            return jsonify({'error': f"Groq API Error: {error_body}"}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'models_loaded': m1 is not None})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
