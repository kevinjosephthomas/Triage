import React, { useState } from 'react'

export default function AiAnalysis({ patientData, triageResult }) {
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalyze = async () => {
    setLoading(true)
    setError(null)
    setAnalysis(null)

    try {
      const response = await fetch('/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          patient_data: patientData,
          triage_result: triageResult
        })
      })

      const data = await response.json()
      if (!response.ok) {
        throw new Error(data.error?.message || data.error || 'Failed to fetch AI analysis')
      }

      setAnalysis(data.analysis)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card ai-card" style={{ animationDelay: '160ms' }}>
      <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ fontSize: '16px' }}>✨</span> AI Clinical Insights
      </div>

      <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 16 }}>
        Generate a comprehensive clinical summary using live data fed into an advanced language model.
      </p>

      <div className="ai-controls">
        <button
          className="submit-btn ai-btn"
          onClick={handleAnalyze}
          disabled={loading || !patientData}
          style={{ marginTop: 0, padding: '9px 16px', width: 'auto' }}
        >
          {loading ? <><span className="spinner" /> Analyzing...</> : 'Generate Insights'}
        </button>
      </div>

      {error && <div className="error-banner" style={{ marginTop: '16px' }}>⚠️ {error}</div>}

      {analysis && (
        <div className="ai-result">
          <div className="ai-result-header">Analysis complete:</div>
          <div className="ai-result-content">
            {analysis}
          </div>
        </div>
      )}
    </div>
  )
}
