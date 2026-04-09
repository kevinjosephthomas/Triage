import React from 'react'

// SVG half-circle gauge
// min/max: numeric range, value: current reading, color: arc color, unit: label
export default function VitalGauge({ label, value, min, max, unit, colorStops }) {
  const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v))
  const clamped = clamp(value, min, max)
  const pct = (clamped - min) / (max - min)          // 0–1
  const angle = pct * 180                             // 0°–180°

  // Arc radius & geometry (viewBox 140x80)
  const cx = 70, cy = 76, r = 60

  const polar = (deg) => {
    const rad = ((deg - 180) * Math.PI) / 180
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) }
  }

  const start = polar(0)
  const end   = polar(angle)
  const largeArc = angle > 180 ? 1 : 0

  // Background arc (full semicircle)
  const bgEnd = polar(180)

  // Determine color from stops
  function getColor() {
    if (!colorStops) return '#3b82f6'
    for (let i = colorStops.length - 1; i >= 0; i--) {
      if (pct >= colorStops[i].at) return colorStops[i].color
    }
    return colorStops[0]?.color ?? '#3b82f6'
  }
  const arcColor = getColor()

  return (
    <div className="gauge-wrap">
      <div className="gauge-svg-wrap" style={{ width: 140, height: 90 }}>
        <svg viewBox="0 0 140 80" width="140" height="80">
          {/* Background track */}
          <path
            d={`M ${start.x} ${start.y} A ${r} ${r} 0 1 1 ${bgEnd.x} ${bgEnd.y}`}
            fill="none"
            stroke="rgba(56,139,253,0.12)"
            strokeWidth="10"
            strokeLinecap="round"
          />
          {/* Value arc */}
          {angle > 0 && (
            <path
              d={`M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 1 ${end.x} ${end.y}`}
              fill="none"
              stroke={arcColor}
              strokeWidth="10"
              strokeLinecap="round"
              style={{ filter: `drop-shadow(0 0 6px ${arcColor})`, transition: 'all 0.8s cubic-bezier(0.34,1.56,0.64,1)' }}
            />
          )}
          {/* Needle dot */}
          <circle cx={end.x} cy={end.y} r="5" fill={arcColor}
            style={{ filter: `drop-shadow(0 0 4px ${arcColor})`, transition: 'all 0.8s cubic-bezier(0.34,1.56,0.64,1)' }}
          />
        </svg>
        <div className="gauge-value-label">
          {value}<span className="gauge-unit">{unit}</span>
        </div>
      </div>
      <div className="gauge-label">{label}</div>
    </div>
  )
}
