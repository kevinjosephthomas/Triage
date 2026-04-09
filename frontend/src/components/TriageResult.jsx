import React from 'react'

const TRIAGE = {
  0: { label: 'LOW (Level 3)',      desc: 'Stable',       color: '#22c55e', pct: 25  },
  1: { label: 'MEDIUM (Level 2)',   desc: 'Urgent',       color: '#eab308', pct: 50  },
  2: { label: 'HIGH (Level 1)',     desc: 'Very Urgent',  color: '#f97316', pct: 75  },
  3: { label: 'CRITICAL (Level 0)', desc: 'Emergency',    color: '#ef4444', pct: 100 },
}

const EMOJIS = { 0: '🟢', 1: '🟡', 2: '🟠', 3: '🔴' }

export default function TriageResult({ result }) {
  if (!result) return null
  const { final_decision } = result
  const t = TRIAGE[final_decision] ?? TRIAGE[0]
  const hex = t.color
  // Hex → rgba dim helper
  const dim = hex + '26'   // ~15% opacity

  return (
    <div
      className="result-card"
      style={{ background: `linear-gradient(135deg, #111f35 70%, ${hex}12)` }}
    >
      <div
        className="card-title"
        style={{ marginBottom: 0 }}
      >
        Consolidated AI Decision
      </div>

      <div
        className="result-badge"
        style={{
          '--severity-color':     hex,
          '--severity-color-dim': dim,
          color: hex,
          background: dim,
          border: `1px solid ${hex}`,
        }}
      >
        <span className="badge-dot" style={{ background: hex }} />
        {EMOJIS[final_decision]} {t.desc}
      </div>

      <div className="result-level" style={{ color: hex }}>
        {t.label}
      </div>

      <div className="progress-bar-wrap">
        <div
          className="progress-bar-fill"
          style={{ width: `${t.pct}%`, background: hex, boxShadow: `0 0 10px ${hex}` }}
        />
      </div>

      <div className="result-desc">
        Meta-learner consensus across 3 federated clinic nodes
      </div>
    </div>
  )
}
