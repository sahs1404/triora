import { useEffect, useState } from 'react'
import { getProject } from '../api/projectApi.js'

const PROJECT_NAME = "demo_project" // hardcoded for now — Upload page will make this dynamic

export default function Dashboard() {
  const [state, setState] = useState(null)
  const [error, setError] = useState(null)
  const [selectedId, setSelectedId] = useState(null)

  useEffect(() => {
    getProject(PROJECT_NAME)
      .then(setState)
      .catch((err) => setError(err.message))
  }, [])

  if (error) {
    return (
      <div className="app-shell">
        <p style={{ color: 'var(--critical)' }}>
          Failed to load project: {error}
          <br />
          Is the backend running at http://127.0.0.1:8000?
        </p>
      </div>
    )
  }

  if (!state) {
    return <div className="app-shell"><p style={{ color: 'var(--muted)' }}>Loading Triora dashboard…</p></div>
  }

  const { summary, materials } = state
  const selected = materials.find((m) => m.material_id === selectedId) || materials[0]

  return (
    <div className="app-shell">
      <header style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 32, margin: 0 }}>
          Tri<span style={{ color: 'var(--critical)' }}>ora</span>
        </h1>
        <p style={{ color: 'var(--muted)', margin: '4px 0 0' }}>{summary.project_name}</p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 28 }}>
        <KpiCard label="Total Materials" value={summary.total_materials} />
        <KpiCard label="Critical" value={summary.critical_count} color="var(--critical)" />
        <KpiCard label="Watch" value={summary.watch_count} color="var(--yellow)" />
        <KpiCard label="Project Duration" value={`${summary.project_duration_days}d`} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: 20 }}>
        <div style={{ background: 'var(--panel)', borderRadius: 12, border: '1px solid var(--line)', overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--line)', fontSize: 13, color: 'var(--muted)' }}>
            RANKED BY CWRS
          </div>
          <div style={{ maxHeight: 520, overflowY: 'auto' }}>
            {materials.map((m) => (
              <div
                key={m.material_id}
                className="material-row"
                onClick={() => setSelectedId(m.material_id)}
                style={{
                  padding: '10px 16px',
                  borderBottom: '1px solid var(--line)',
                  cursor: 'pointer',
                  background: selected?.material_id === m.material_id ? 'var(--panel-2)' : 'transparent',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <div>
                  <div style={{ fontSize: 13.5, fontWeight: 600 }}>
                    #{m.rank} {m.name}
                    <StatusBadge status={m.status} />
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--muted)' }}>{m.activity_name}</div>
                </div>
                <div style={{ fontWeight: 700, color: statusColor(m.status) }}>{m.cwrs.toFixed(3)}</div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ background: 'var(--panel)', borderRadius: 12, border: '1px solid var(--line)', padding: 20 }}>
          {selected ? (
            <>
              <h3 style={{ margin: '0 0 4px' }}>{selected.name}</h3>
              <p style={{ color: 'var(--muted)', fontSize: 12, margin: '0 0 16px' }}>
                {selected.activity_name} · {selected.material_id}
              </p>
              <Factor label="P(delay)" value={`${Math.round(selected.p_delay * 100)}%`} />
              <Factor label="Schedule float" value={`${selected.activity_float_days} days`} />
              <Factor label="Downstream impact" value={`${selected.blast_radius} activities`} />
              <Factor label="CWRS" value={selected.cwrs.toFixed(3)} />
              <div style={{
                marginTop: 16, padding: 12, borderRadius: 8, fontSize: 12.5, lineHeight: 1.5,
                background: statusDimColor(selected.status), color: 'var(--paper)',
              }}>
                {selected.reason}
              </div>
            </>
          ) : (
            <p style={{ color: 'var(--muted)' }}>Select a material to see details.</p>
          )}
        </div>
      </div>
    </div>
  )
}

function KpiCard({ label, value, color }) {
  return (
    <div style={{ background: 'var(--panel)', border: '1px solid var(--line)', borderRadius: 10, padding: 14 }}>
      <div style={{ fontSize: 24, fontWeight: 700, color: color || 'var(--paper)' }}>{value}</div>
      <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 4 }}>{label}</div>
    </div>
  )
}

function StatusBadge({ status }) {
  return (
    <span style={{
      marginLeft: 8, fontSize: 9.5, padding: '2px 6px', borderRadius: 4,
      background: statusDimColor(status), color: statusColor(status), textTransform: 'uppercase',
    }}>
      {status}
    </span>
  )
}

function Factor({ label, value }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--line)', fontSize: 13 }}>
      <span style={{ color: 'var(--muted)' }}>{label}</span>
      <span style={{ fontWeight: 600 }}>{value}</span>
    </div>
  )
}

function statusColor(status) {
  if (status === 'critical') return 'var(--critical)'
  if (status === 'watch') return 'var(--yellow)'
  return 'var(--safe)'
}

function statusDimColor(status) {
  if (status === 'critical') return 'var(--critical-dim)'
  if (status === 'watch') return 'var(--watch-dim)'
  return 'var(--safe-dim)'
}