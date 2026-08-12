import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Papa from 'papaparse'
import { buildProjectInput } from '../utils/csvToProjectInput.js'
import { buildProject } from '../api/projectApi.js'

function parseCsvFile(file) {
  return new Promise((resolve, reject) => {
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => resolve(results.data),
      error: reject,
    })
  })
}

export default function Upload() {
  const navigate = useNavigate()

  const [projectName, setProjectName] = useState('')
  const [activitiesFile, setActivitiesFile] = useState(null)
  const [materialsFile, setMaterialsFile] = useState(null)
  const [vendorsFile, setVendorsFile] = useState(null)

  const [status, setStatus] = useState('idle') // idle | loading | error
  const [errorMsg, setErrorMsg] = useState('')

  const canSubmit = projectName.trim() && activitiesFile && materialsFile && vendorsFile

  async function handleSubmit(e) {
    e.preventDefault()
    if (!canSubmit) return

    setStatus('loading')
    setErrorMsg('')

    try {
      const [activityRows, materialRows, vendorRows] = await Promise.all([
        parseCsvFile(activitiesFile),
        parseCsvFile(materialsFile),
        parseCsvFile(vendorsFile),
      ])

      const payload = buildProjectInput(projectName.trim(), activityRows, materialRows, vendorRows)
      await buildProject(payload)

      navigate(`/?project=${encodeURIComponent(projectName.trim())}`)
    } catch (err) {
      setStatus('error')
      setErrorMsg(err.message || 'Something went wrong while building the project.')
    }
  }

  return (
    <div className="app-shell">
      <header style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 32, margin: 0 }}>
          Tri<span style={{ color: 'var(--critical)' }}>ora</span>
        </h1>
        <p style={{ color: 'var(--muted)', margin: '4px 0 0' }}>Upload a project</p>
      </header>

      <form
        onSubmit={handleSubmit}
        style={{
          background: 'var(--panel)', border: '1px solid var(--line)',
          borderRadius: 12, padding: 24, maxWidth: 520,
        }}
      >
        <Field label="Project name">
          <input
            type="text"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            placeholder="e.g. demo_project"
            style={inputStyle}
          />
        </Field>

        <FileField label="Activities CSV" file={activitiesFile} onChange={setActivitiesFile} />
        <FileField label="Materials CSV" file={materialsFile} onChange={setMaterialsFile} />
        <FileField label="Vendors CSV" file={vendorsFile} onChange={setVendorsFile} />

        {status === 'error' && (
          <div style={{
            background: 'var(--critical-dim)', color: 'var(--critical)',
            padding: 12, borderRadius: 8, fontSize: 13, marginBottom: 16,
          }}>
            {errorMsg}
          </div>
        )}

        <button
          type="submit"
          disabled={!canSubmit || status === 'loading'}
          style={{
            width: '100%', padding: '12px', borderRadius: 8, border: 'none',
            background: canSubmit ? 'var(--critical)' : 'var(--line)',
            color: canSubmit ? '#1a0e08' : 'var(--muted)',
            fontWeight: 700, fontSize: 14, cursor: canSubmit ? 'pointer' : 'not-allowed',
          }}
        >
          {status === 'loading' ? 'Building project…' : 'Upload & Score Project'}
        </button>
      </form>

      <p style={{ color: 'var(--muted)', fontSize: 12, marginTop: 16, maxWidth: 520 }}>
        CSV column format must match <code>datasets/README.md</code>. Activities need an{' '}
        <code>id, name, duration_days, predecessors</code> header row; materials need{' '}
        <code>id, name, activity_id, vendor_id, lead_time_days, ...</code>; vendors need{' '}
        <code>id, name, historical_delay_rate, jobs_completed, jobs_delayed</code>.
      </p>
    </div>
  )
}

function Field({ label, children }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <label style={{ display: 'block', fontSize: 12, color: 'var(--muted)', marginBottom: 6 }}>
        {label}
      </label>
      {children}
    </div>
  )
}

function FileField({ label, file, onChange }) {
  return (
    <Field label={label}>
      <input
        type="file"
        accept=".csv"
        onChange={(e) => onChange(e.target.files[0] || null)}
        style={inputStyle}
      />
      {file && <span style={{ fontSize: 11, color: 'var(--safe)' }}>{file.name} selected</span>}
    </Field>
  )
}

const inputStyle = {
  width: '100%', padding: '9px 10px', borderRadius: 6,
  border: '1px solid var(--line)', background: 'var(--ink)',
  color: 'var(--paper)', fontSize: 13,
}
