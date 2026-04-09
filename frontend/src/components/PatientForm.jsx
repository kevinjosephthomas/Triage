import React, { useState } from 'react'

const DEFAULTS = {
  age: 25,
  heart_rate: 72,
  systolic_blood_pressure: 120,
  oxygen_saturation: 98,
  body_temperature: 36.6,
  pain_level: 1,
  chronic_disease_count: 0,
  previous_er_visits: 0,
  arrival_mode: 'walk-in',
  travel_history: 'No',
}

export default function PatientForm({ onResult, onLoading, formState, onFormChange }) {
  // If parent manages state (lifted), use it; otherwise use local state
  const [localForm, setLocalForm] = useState(DEFAULTS)
  const form   = formState   ?? localForm
  const setAll = onFormChange ?? setLocalForm

  const set = (key, val) => setAll({ ...form, [key]: val })

  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    onLoading?.(true)
    setError(null)

    try {
      const res  = await fetch('/predict', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(form),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error ?? 'Prediction failed')
      onResult?.(data)
    } catch (err) {
      setError(err.message)
      onResult?.(null)
    } finally {
      setLoading(false)
      onLoading?.(false)
    }
  }

  return (
    <form className="sidebar" onSubmit={handleSubmit}>
      {/* Brand */}
      <div className="brand">
        <div className="brand-icon">🏥</div>
        <div className="brand-text">
          <h1>AI Triage</h1>
          <p>Federated Clinical Model</p>
        </div>
      </div>

      {/* Vitals */}
      <div className="form-section-label">Patient Vitals</div>

      <div className="form-group">
        <label htmlFor="f-age">Age (years)</label>
        <input id="f-age" type="number" min={0} max={120}
          value={form.age} onChange={e => set('age', Number(e.target.value))} />
      </div>

      <div className="form-group">
        <label htmlFor="f-hr">Heart Rate (BPM)</label>
        <input id="f-hr" type="number" min={40} max={200}
          value={form.heart_rate} onChange={e => set('heart_rate', Number(e.target.value))} />
      </div>

      <div className="form-group">
        <label htmlFor="f-sbp">Systolic BP (mmHg)</label>
        <input id="f-sbp" type="number" min={70} max={220}
          value={form.systolic_blood_pressure}
          onChange={e => set('systolic_blood_pressure', Number(e.target.value))} />
      </div>

      <div className="form-group">
        <label>Oxygen Saturation (%)</label>
        <div className="slider-wrap">
          <input id="f-spo2" type="range" min={70} max={100}
            value={form.oxygen_saturation}
            onChange={e => set('oxygen_saturation', Number(e.target.value))} />
          <span className="slider-val">{form.oxygen_saturation}</span>
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="f-temp">Temperature (°C)</label>
        <input id="f-temp" type="number" min={34} max={42} step={0.1}
          value={form.body_temperature}
          onChange={e => set('body_temperature', parseFloat(e.target.value))} />
      </div>

      <div className="form-group">
        <label>Pain Level (1–10)</label>
        <div className="slider-wrap">
          <input id="f-pain" type="range" min={1} max={10}
            value={form.pain_level}
            onChange={e => set('pain_level', Number(e.target.value))} />
          <span className="slider-val">{form.pain_level}</span>
        </div>
      </div>

      {/* History */}
      <div className="form-section-label">Medical History</div>

      <div className="form-group">
        <label htmlFor="f-chronic">Chronic Conditions (count)</label>
        <input id="f-chronic" type="number" min={0} max={10}
          value={form.chronic_disease_count}
          onChange={e => set('chronic_disease_count', Number(e.target.value))} />
      </div>

      <div className="form-group">
        <label htmlFor="f-prev-er">Previous ER Visits</label>
        <input id="f-prev-er" type="number" min={0} max={20}
          value={form.previous_er_visits}
          onChange={e => set('previous_er_visits', Number(e.target.value))} />
      </div>

      <div className="form-group">
        <label htmlFor="f-arrival">Arrival Mode</label>
        <select id="f-arrival" value={form.arrival_mode}
          onChange={e => set('arrival_mode', e.target.value)}>
          <option value="walk-in">Walk-in</option>
          <option value="ambulance">Ambulance</option>
          <option value="wheelchair">Wheelchair</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div className="form-group">
        <label>Recent International Travel?</label>
        <div className="radio-group">
          {['No', 'Yes'].map(opt => (
            <button key={opt} type="button"
              className={`radio-btn ${form.travel_history === opt ? 'active' : ''}`}
              onClick={() => set('travel_history', opt)}
            >
              {opt === 'Yes' ? '✈️ Yes' : '🚫 No'}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="error-banner">⚠️ {error}</div>
      )}

      <button id="run-analysis-btn" type="submit" className="submit-btn" disabled={loading}>
        {loading
          ? <><span className="spinner" />Analyzing…</>
          : '🔬 Run Federated Analysis'
        }
      </button>
    </form>
  )
}
