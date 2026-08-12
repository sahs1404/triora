import { useEffect, useState } from 'react'
import { getProject, getVendors, runWhatIf } from '../api/projectApi.js'

const PROJECT_NAME = "demo_project" // matches Dashboard.jsx for now — router.jsx will fix this

const CHANGE_TYPES = [
  { value: 'expedite_material', label: 'Expedite a material (reduce lead time)' },
  { value: 'delay_material', label: 'Delay a material (increase lead time)' },
  { value: 'change_duration', label: "Change an activity's duration" },
  { value: 'reassign_vendor', label: 'Reassign a material to a different vendor' },
]

export default function Simulation() {
  const [project, setProject] = useState(null)
  const [vendors, setVendors] = useState([])
  const [error, setError] = useState(null)

  const [changeType, setChangeType] = useState('expedite_material')
  const [targetId, setTargetId] = useState('')
  const [value, setValue] = useState('')

  const [result, setResult] = useState(null)
  const [running, setRunning] = useState(false)
  const [runError, setRunError] = useState('')

  useEffect(() => {
    Promise.all([getProject(PROJECT_NAME), getVendors(PROJECT_NAME)])
      .then(([proj, vend]) => {
        setProject(proj)
        setVendors(vend)
      })
      .catch((err) => setError(err.message))
  }, [])

  const isActivityChange = changeType === 'change_duration'
  const isVendorChange = changeType === 'reassign_vendor'

  const targetOptions = isActivityChange
    ? project?.summary.critical_path.map((id) => ({ id, label: id })) // simplified: critical path ids as a starting set
    : project?.materials.map((m) => ({ id: m.material_id, label: `${m.name} (${m.material_id})` }))

  async function handleRun(e) {
    e.preventDefault()
    if (!targetId || value === '') return

    setRunning(true)
    setRunError('')
    setResult(null)

    try {
      const changeValue = isVendorChange ? value : parseFloat(value)
      const response = await runWhatIf(PROJECT_NAME, [
        { change_type: changeType, target_id: targetId, value: changeValue },
      ])
      setResult(response)
    } catch (err) {
      setRunError(err.message)
    } finally {
      setRunning(false)
    }
  }

  if (error) {
    return (
      <div className="app-shell">
        <p style={{ color: 'var(--critical)' }}>Failed to load project: {error}</p>
      </div>
    )
  }

  if (!project) {
    return <div className="app-shell"><p style={{ color: 'var(--muted)' }}>Loading…</p></div>
  }

  return (
    <div className="app-shell">
      <header style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 32, margin: 0 }}>
          Tri<span style={{ color: 'var(--critical)' }}>ora</span>
        </h1>
        <p style={{ color: 'var(--muted)', margin: '4px 0 0' }}>What-if simulator — {project.summary.project_name}</p>
      </header>

      <form onSubmit={handleRun} style={{
        background: 'var(--panel)', border: '1px solid var(--line)',
        borderRadius: 12, padding: 20, maxWidth: 560, marginBottom: 24,
      }}>
        <Field label="Change type">
          <select
            value={changeType}
            onChange={(e) => { setChangeType(e.target.value); setTargetId(''); setValue('') }}
            style={inputStyle}
          >
            {CHANGE_TYPES.map((c) => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>
        </Field>

        <Field label={isActivityChange ? 'Target activity' : 'Target material'}>
          <select value={targetId} onChange={(e) => setTargetId(e.target.value)} style={inputStyle}>
            <option value="">Select…</option>
            {targetOptions?.map((t) => (
              <option key={t.id} value={t.id}>{t.label}</option>
            ))}
          </select>
        </Field>

        {isVendorChange ? (
          <Field label="New vendor">
            <select value={value} onChange={(e) => setValue(e.target.value)} style={inputStyle}>
              <option value="">Select…</option>
              {vendors.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name} ({Math.round(v.historical_delay_rate * 100)}% delay rate)
                </option>
              ))}
            </select>
          </Field>
        ) : (
          <Field label={isActivityChange ? 'New duration (days)' : 'Days to shift'}>
            <input
              type="number"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              style={inputStyle}
              min={isActivityChange ? 1 : 0}
            />
          </Field>
        )}

        {runError && (
          <div style={{
            background: 'var(--critical-dim)', color: 'var(--critical)',
            padding: 10, borderRadius: 8, fontSize: 13, marginBottom: 14,
          }}>
            {runError}
          </div>
        )}

        <button
          type="submit"
          disabled={!targetId || value === '' || running}
          style={{
            width: '100%', padding: '11px', borderRadius: 8, border: 'none',
            background: (!targetId || value === '') ? 'var(--line)' : 'var(--critical)',
            color: (!targetId || value === '') ? 'var(--muted)' : '#1a0e08',
            fontWeight: 700, fontSize: 14,
            cursor: (!targetId || value === '') ? 'not-allowed' : 'pointer',
          }}
        >
          {running ? 'Running simulation…' : 'Run What-If'}
        </button>
      </form>

      {result && <ResultPanel result={result} />}
    </div>
  )
}

function ResultPanel({ result }) {
  const { before, after, project_duration_delta_days, materials_changed_status } = result
  const deltaColor = project_duration_delta_days > 0 ? 'var(--critical)'
    : project_duration_delta_days < 0 ? 'var(--safe)' : 'var(--muted)'

  return (
    <div style={{ display: 'grid', gap: 16, maxWidth: 900 }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        <StatBox label="Duration before" value={`${before.summary.project_duration_days}d`} />
        <StatBox label="Duration after" value={`${after.summary.project_duration_days}d`} />
        <StatBox
          label="Delta"
          value={`${project_duration_delta_days > 0 ? '+' : ''}${project_duration_delta_days}d`}
          color={deltaColor}
        />
      </div>

      <div style={{ background: 'var(--panel)', border: '1px solid var(--line)', borderRadius: 12, padding: 18 }}>
        <h3 style={{ margin: '0 0 12px', fontSize: 14 }}>
          Materials whose status changed ({materials_changed_status.length})
        </h3>
        {materials_changed_status.length === 0 ? (
          <p style={{ color: 'var(--muted)', fontSize: 13 }}>No status changes from this scenario.</p>
        ) : (
          materials_changed_status.map((id) => {
            const beforeM = before.materials.find((m) => m.material_id === id)
            const afterM = after.materials.find((m) => m.material_id === id)
            return (
              <div key={id} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '10px 0', borderBottom: '1px solid var(--line)',
              }}>
                <span style={{ fontSize: 13.5, fontWeight: 600 }}>{beforeM.name}</span>
                <span style={{ fontSize: 13, color: 'var(--muted)' }}>
                  <StatusTag status={beforeM.status} /> ({beforeM.cwrs.toFixed(3)})
                  {' → '}
                  <StatusTag status={afterM.status} /> ({afterM.cwrs.toFixed(3)})
                </span>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}

function Field({ label, children }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <label style={{ display: 'block', fontSize: 12, color: 'var(--muted)', marginBottom: 6 }}>{label}</label>
      {children}
    </div>
  )
}

function StatBox({ label, value, color }) {
  return (
    <div style={{ background: 'var(--panel)', border: '1px solid var(--line)', borderRadius: 10, padding: 14 }}>
      <div style={{ fontSize: 22, fontWeight: 700, color: color || 'var(--paper)' }}>{value}</div>
      <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 4 }}>{label}</div>
    </div>
  )
}

function StatusTag({ status }) {
  const color = status === 'critical' ? 'var(--critical)' : status === 'watch' ? 'var(--yellow)' : 'var(--safe)'
  return <span style={{ color, fontWeight: 700, textTransform: 'uppercase', fontSize: 11 }}>{status}</span>
}

const inputStyle = {
  width: '100%', padding: '9px 10px', borderRadius: 6,
  border: '1px solid var(--line)', background: 'var(--ink)',
  color: 'var(--paper)', fontSize: 13,
}