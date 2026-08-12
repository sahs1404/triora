import { useEffect, useState } from 'react'
import { apiGet } from '../../api/client.js'

export default function RecoveryCard({ projectName, materialId }) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!materialId) return
    setLoading(true)
    setError(null)
    apiGet(`/project/${projectName}/material/${materialId}/recovery`)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [projectName, materialId])

  if (!materialId) return null
  if (loading) return <p style={{ color: 'var(--muted)', fontSize: 12 }}>Loading recovery options…</p>
  if (error) return <p style={{ color: 'var(--critical)', fontSize: 12 }}>Failed to load recovery options: {error}</p>
  if (!data) return null

  return (
    <div style={{
      marginTop: 16, background: 'var(--panel-2)', border: '1px solid var(--line)',
      borderRadius: 10, padding: 16,
    }}>
      <h4 style={{ margin: '0 0 4px', fontSize: 13 }}>Recovery Options</h4>
      <p style={{ color: 'var(--muted)', fontSize: 11.5, margin: '0 0 12px' }}>
        Recommended: <strong style={{ color: 'var(--paper)' }}>{data.recommended_action}</strong>
      </p>

      {data.options.map((opt, i) => (
        <div
          key={opt.action}
          style={{
            padding: '10px 0',
            borderBottom: i < data.options.length - 1 ? '1px solid var(--line)' : 'none',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: 12.5, fontWeight: 700 }}>
              {i === 0 && '⭐ '}{opt.action}
            </span>
            <span style={{ fontSize: 11, color: 'var(--muted)' }}>
              +{opt.estimated_days_recovered}d recovered
            </span>
          </div>
          <p style={{ fontSize: 11.5, color: 'var(--muted)', margin: '4px 0 6px' }}>{opt.description}</p>
          <div style={{ display: 'flex', gap: 12, fontSize: 10.5, color: 'var(--muted)' }}>
            <span>Cost: <strong>{opt.estimated_cost}</strong></span>
            <span>Feasibility: <strong>{opt.feasibility}</strong></span>
          </div>
        </div>
      ))}
    </div>
  )
}