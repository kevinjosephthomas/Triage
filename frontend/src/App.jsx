import React, { useState, useEffect } from 'react'
import PatientForm from './components/PatientForm'
import VitalGauge from './components/VitalGauge'
import TriageResult from './components/TriageResult'
import ConsensusChart from './components/ConsensusChart'
import AiAnalysis from './components/AiAnalysis'

const SPO2_STOPS = [
  { at: 0, color: '#ef4444' },
  { at: 0.27, color: '#eab308' },   // ~90% on 70-100 scale
  { at: 0.45, color: '#22c55e' },   // ~95%
]

const HR_STOPS = [
  { at: 0, color: '#6b7280' },   // bradycardia
  { at: 0.12, color: '#22c55e' },   // normal 60-100
  { at: 0.37, color: '#ef4444' },   // tachycardia >100
]

export default function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [vitals, setVitals] = useState({ spo2: 98, hr: 72 })
  const [apiOk, setApiOk] = useState(null)

  // Health-check on mount
  useEffect(() => {
    fetch('/health')
      .then(r => r.json())
      .then(d => setApiOk(d.models_loaded === true))
      .catch(() => setApiOk(false))
  }, [])

  const handleResult = (data) => {
    setResult(data)
  }

  // Intercept form submission to also capture vitals for gauges
  const handleLoading = (v) => setLoading(v)

  // We need the raw form values for gauges; lift state approach:
  // PatientForm sends us the full result which includes what the API echoes.
  // But we also track the latest vitals separately via a hidden form ref trick —
  // Instead, we track vitals in App state and pass a setter down.
  const [formVitals, setFormVitals] = useState({
    age: 25, heart_rate: 72, systolic_blood_pressure: 120,
    oxygen_saturation: 98, body_temperature: 36.6,
    pain_level: 1, chronic_disease_count: 0, previous_er_visits: 0,
    arrival_mode: 'walk-in', travel_history: 'No',
  })

  const handleFormVitalChange = (v) => setFormVitals(v)

  return (
    <div className="app-shell">
      {/* LEFT: Patient Form */}
      <PatientFormWrapper
        onResult={handleResult}
        onLoading={handleLoading}
        onVitalsChange={handleFormVitalChange}
      />

      {/* RIGHT: Dashboard */}
      <main className="main">
        {/* Header */}
        <div className="main-header">
          <div>
            <h2>Federated AI Triage Dashboard</h2>
            <p>Multi-clinic consensus · Real-time patient prioritization</p>
          </div>
          <div className="status-pill">
            <span className="dot" style={apiOk === false ? { background: '#ef4444', animation: 'none' } : {}} />
            {apiOk === null ? 'Connecting…' : apiOk ? 'Models Online' : 'API Offline'}
          </div>
        </div>

        {!result && !loading && (
          <div className="empty-state">
            <div className="empty-icon">🏥</div>
            <h3>Awaiting Patient Data</h3>
            <p>Enter patient vitals in the panel on the left and click <strong>Run Federated Analysis</strong> to receive the AI triage decision.</p>
          </div>
        )}

        {loading && (
          <div className="empty-state">
            <div className="empty-icon" style={{ animation: 'spin 1.2s linear infinite', display: 'inline-block' }}>⚙️</div>
            <h3>Analyzing…</h3>
            <p>Running predictions across 3 clinic nodes and computing meta-learner consensus.</p>
          </div>
        )}

        {result && !loading && (
          <>
            {/* Vitals */}
            <div className="card" style={{ animationDelay: '0ms' }}>
              <div className="card-title">🫀 Vital Signs Monitoring</div>
              <div className="vitals-grid">
                <VitalGauge
                  label="Oxygen Saturation"
                  value={formVitals.oxygen_saturation}
                  min={70} max={100}
                  unit="%"
                  colorStops={SPO2_STOPS}
                />
                <VitalGauge
                  label="Heart Rate"
                  value={formVitals.heart_rate}
                  min={40} max={200}
                  unit="BPM"
                  colorStops={HR_STOPS}
                />
                <TriageResult result={result} />
              </div>
            </div>

            {/* Consensus */}
            <div className="card" style={{ animationDelay: '80ms' }}>
              <div className="card-title">🤝 Federated Model Consensus</div>
              <ConsensusChart result={result} />
              <p style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 14 }}>
                The meta-learner weights these inputs based on historical performance and patient complexity.
              </p>
            </div>

            {/* AI Analysis */}
            <AiAnalysis patientData={formVitals} triageResult={result} />
          </>
        )}
      </main>
    </div>
  )
}

// Wrapper to intercept vitals and pass up
function PatientFormWrapper({ onResult, onLoading, onVitalsChange }) {
  const [form, setForm] = useState({
    age: 25, heart_rate: 72, systolic_blood_pressure: 120,
    oxygen_saturation: 98, body_temperature: 36.6,
    pain_level: 1, chronic_disease_count: 0, previous_er_visits: 0,
    arrival_mode: 'walk-in', travel_history: 'No',
  })

  const handleChange = (updated) => {
    setForm(updated)
    onVitalsChange(updated)
  }

  return (
    <PatientForm
      onResult={onResult}
      onLoading={onLoading}
      formState={form}
      onFormChange={handleChange}
    />
  )
}
