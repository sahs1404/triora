import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { API_BASE_URL } from '../api/client.js'

const STAGE_OPTIONS = [
  { value: 'delivery', label: 'Delivery (expect truck/vehicle in frame)' },
  { value: 'fabrication', label: 'Fabrication (expect person/activity)' },
  { value: 'installation', label: 'Installation (expect person present)' },
  { value: 'inspection', label: 'Inspection (expect person present)' },
  { value: 'site_prep', label: 'Site Prep (expect vehicle or person)' },
]

export default function CVUpload() {
  const [searchParams] = useSearchParams()
  const PROJECT_NAME = searchParams.get('project') || 'demo_project'

  const [materialId, setMaterialId] = useState('')
  const [activityId, setActivityId] = useState('')
  const [expectedStage, setExpectedStage] = useState('delivery')
  const [photo, setPhoto] = useState(null)

  const [status, setStatus] = useState('idle')
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const canSubmit = materialId.trim() && activityId.trim() && photo

  async function handleSubmit(e) {
    e.preventDefault()
    if (!canSubmit) return

    setStatus('submitting')
    setError(null)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('project_name', PROJECT_NAME)
      formData.append('material_id', materialId.trim())
      formData.append('activity_id', activityId.trim())
      formData.append('expected_stage', expectedStage)
      formData.append('photo', photo)

      const res = await fetch(API_BASE_URL + '/evidence/photo', {
        method: 'POST',
        body: formData,
      })
      if (!res.ok) {
        const body = await res.text()
        throw new Error('Request failed (' + res.status + '): ' + body)
      }
      const data = await res.json()
      setResult(data)
      setStatus('idle')
    } catch (err) {
      setStatus('error')
      setError(err.message)
    }
  }

  return (
    <div className="app-shell">
      <header style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 32, margin: 0 }}>
          Site Photo <span style={{ color: 'var(--critical)' }}>Verification</span>
        </h1>
        <p style={{ color: 'var(--muted)', margin: '4px 0 0' }}>
          Upload a site photo to verify it matches the expected construction stage.
        </p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, alignItems: 'start' }}>
        <form
          onSubmit={handleSubmit}
          style={{
            background: 'var(--panel)', border: '1px solid var(--line)',
            borderRadius: 12, padding: 24,
            display: 'flex', flexDirection: 'column', gap: 16,
          }}
        >
          <Field label="Material ID (e.g. M135)">
            <input value={materialId} onChange={(e) => setMaterialId(e.target.value)} style={inputStyle} />
          </Field>

          <Field label="Activity ID (e.g. A09)">
            <input value={activityId} onChange={(e) => setActivityId(e.target.value)} style={inputStyle} />
          </Field>

          <Field label="Expected Stage">
            <select value={expectedStage} onChange={(e) => setExpectedStage(e.target.value)} style={inputStyle}>
              {STAGE_OPTIONS.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
          </Field>

          <Field label="Site Photo">
            <input type="file" accept="image/*" onChange={(e) => setPhoto(e.target.files[0] || null)} />
          </Field>

          {error && <p style={{ color: 'var(--critical)', fontSize: 13, margin: 0 }}>{error}</p>}

          <button
            type="submit"
            disabled={!canSubmit || status === 'submitting'}
            style={{
              padding: '10px 16px', borderRadius: 8, border: 'none',
              background: canSubmit ? 'var(--critical)' : 'var(--line)',
              color: canSubmit ? '#1a0e08' : 'var(--muted)',
              fontWeight: 700, cursor: canSubmit ? 'pointer' : 'not-allowed',
            }}
          >
            {status === 'submitting' ? 'Verifying...' : 'Verify Photo'}
          </button>
        </form>

        {result && <ResultPanel result={result} />}
      </div>
    </div>
  )
}

function ResultPanel({ result }) {
  const cv_result = result.cv_result
  const updated_p_delay = result.updated_p_delay
  const verdictColor = {
    match: 'var(--safe)',
    mismatch: 'var(--critical)',
    uncertain: 'var(--yellow)',
    unsupported_stage: 'var(--muted)',
  }[cv_result.match_result] || 'var(--muted)'

  const detectedText = cv_result.detected_classes.length
    ? cv_result.detected_classes.join(', ')
    : 'nothing above confidence threshold'

  return (
    <div style={{
      background: 'var(--panel)', border: '1px solid var(--line)',
      borderRadius: 12, padding: 20,
    }}>
      <div style={{ fontSize: 13, fontWeight: 700, color: verdictColor, textTransform: 'uppercase', marginBottom: 8 }}>
        {cv_result.match_result.replace('_', ' ')}
      </div>
      <p style={{ fontSize: 13, margin: '0 0 12px', lineHeight: 1.5 }}>{cv_result.explanation}</p>
      {cv_result.annotated_image_base64 && (
        <img
          src={"data:image/jpeg;base64," + cv_result.annotated_image_base64}
          alt="Annotated detection result"
          style={{ width: '100%', borderRadius: 8, marginBottom: 12 }}
        />
      )}
      <p style={{ fontSize: 12, color: 'var(--muted)', margin: '0 0 4px' }}>
        Detected: {detectedText}
      </p>
      <p style={{ fontSize: 12, color: 'var(--muted)', margin: 0 }}>
        Updated P(delay) for this material: <strong>{Math.round(updated_p_delay * 100)}%</strong>
      </p>
    </div>
  )
}

function Field({ label, children }) {
  return (
    <label style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: 13 }}>
      <span style={{ color: 'var(--muted)' }}>{label}</span>
      {children}
    </label>
  )
}

const inputStyle = {
  padding: '8px 10px', borderRadius: 6, border: '1px solid var(--line)',
  background: 'var(--panel-2)', color: 'var(--paper)', fontSize: 13,
}