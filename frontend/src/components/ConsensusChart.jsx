import React from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const LEVEL_COLORS = ['#22c55e', '#eab308', '#f97316', '#ef4444']
const LEVEL_LABELS = ['Low', 'Medium', 'High', 'Critical']

const CLINIC_NAMES  = ['Urgent Care', 'Elderly Care', 'International']
const CLINIC_ICONS  = ['🏥', '👴', '✈️']

export default function ConsensusChart({ result }) {
  if (!result) return null
  const { p1, p2, p3 } = result
  const predictions = [p1, p2, p3]

  const data = {
    labels: CLINIC_NAMES.map((n, i) => `${CLINIC_ICONS[i]} ${n}`),
    datasets: [{
      label: 'Predicted Urgency',
      data: predictions,
      backgroundColor: predictions.map(v => LEVEL_COLORS[v] + 'cc'),
      borderColor:     predictions.map(v => LEVEL_COLORS[v]),
      borderWidth: 2,
      borderRadius: 8,
      borderSkipped: false,
    }],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 900, easing: 'easeOutQuart' },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: ctx => ` ${ctx.parsed.y} — ${LEVEL_LABELS[ctx.parsed.y] ?? 'Unknown'}`,
        },
        backgroundColor: '#0d1b2e',
        borderColor: 'rgba(56,139,253,0.3)',
        borderWidth: 1,
        titleColor: '#e2eaf6',
        bodyColor: '#7b93b8',
        padding: 10,
        cornerRadius: 8,
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(56,139,253,0.06)' },
        ticks: { color: '#7b93b8', font: { size: 12, weight: '600' } },
        border: { color: 'rgba(56,139,253,0.15)' },
      },
      y: {
        min: 0,
        max: 3,
        ticks: {
          stepSize: 1,
          color: '#7b93b8',
          font: { size: 11 },
          callback: v => LEVEL_LABELS[v] ?? v,
        },
        grid: { color: 'rgba(56,139,253,0.06)' },
        border: { color: 'rgba(56,139,253,0.15)' },
      },
    },
  }

  return (
    <>
      <div className="clinic-nodes">
        {CLINIC_NAMES.map((name, i) => {
          const val = predictions[i]
          const color = LEVEL_COLORS[val]
          return (
            <div className="clinic-node" key={name}
              style={{ borderColor: color + '55', background: color + '12' }}
            >
              <div className="node-name">{CLINIC_ICONS[i]} {name}</div>
              <div className="node-val" style={{ color }}>{val}</div>
              <div className="node-label">{LEVEL_LABELS[val]}</div>
            </div>
          )
        })}
      </div>

      <div className="chart-wrap" style={{ marginTop: 16 }}>
        <Bar data={data} options={options} />
      </div>
    </>
  )
}
