import { useEffect, useState } from 'react'
import { getVendors } from '../api/projectApi.js'
import { apiPost } from '../api/client.js'

const PROJECT_NAME = "demo_project"

export default function VendorPanel() {
  const [vendors, setVendors] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [updatingId, setUpdatingId] = useState(null)

  useEffect(() => {
    loadVendors()
  }, [])

  function loadVendors() {
    setLoading(true)
    getVendors(PROJECT_NAME)
      .then((data) => {
        setVendors(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }

  async function recordOutcome(vendorId, wasDelayed) {
    setUpdatingId(vendorId)
    try {
      await apiPost(`/project/${PROJECT_NAME}/vendors/${vendorId}/job-outcome`, {
        was_delayed: wasDelayed,
      })
      await loadVendors()
    } catch (err) {
      setError(err.message)
    } finally {
      setUpdatingId(null)
    }
  }

  if (error) {
    return (
      <div className="app-shell">
        <p style={{ color: 'var(--critical)' }}>Failed to load vendors: {error}</p>
      </div>
    )
  }

  return (
    <div className="app-shell">
      <header style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 32, margin: 0 }}>
          Tri<span style={{ color: 'var(--critical)' }}>ora</span>
        </h1>
        <p style={{ color: 'var(--muted)', margin: '4px 0 0' }}>Vendor reliability — {PROJECT_NAME}</p>
      </header>

      {loading ? (
        <p style={{ color: 'var(--muted)' }}>Loading vendors…</p>
      ) : (
        <div style={{ background: 'var(--panel)', border: '1px solid var(--line)', borderRadius: 12, overflow: 'hidden' }}>
          <div style={{
            display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr 1.5fr',
            padding: '12px 16px', borderBottom: '1px solid var(--line)',
            fontSize: 11, color: 'var(--muted)', textTransform: 'uppercase',
          }}>
            <span>Vendor</span>
            <span>Delay Rate</span>
            <span>Jobs</span>
            <span>Delayed</span>
            <span>Record Outcome</span>
          </div>
          {vendors.map((v) => (
            <div key={v.id} style={{
              display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr 1.5fr',
              padding: '12px 16px', borderBottom: '1px solid var(--line)',
              alignItems: 'center', fontSize: 13.5,
            }}>
              <span style={{ fontWeight: 600 }}>{v.name}</span>
              <span style={{
                fontWeight: 700,
                color: v.historical_delay_rate > 0.5 ? 'var(--critical)'
                  : v.historical_delay_rate > 0.25 ? 'var(--yellow)' : 'var(--safe)',
              }}>
                {Math.round(v.historical_delay_rate * 100)}%
              </span>
              <span style={{ color: 'var(--muted)' }}>{v.jobs_completed}</span>
              <span style={{ color: 'var(--muted)' }}>{v.jobs_delayed}</span>
              <span style={{ display: 'flex', gap: 6 }}>
                <button
                  disabled={updatingId === v.id}
                  onClick={() => recordOutcome(v.id, false)}
                  style={{
                    padding: '5px 10px', borderRadius: 6, border: '1px solid var(--safe)',
                    background: 'transparent', color: 'var(--safe)', fontSize: 11.5, cursor: 'pointer',
                  }}
                >
                  On-time
                </button>
                <button
                  disabled={updatingId === v.id}
                  onClick={() => recordOutcome(v.id, true)}
                  style={{
                    padding: '5px 10px', borderRadius: 6, border: '1px solid var(--critical)',
                    background: 'transparent', color: 'var(--critical)', fontSize: 11.5, cursor: 'pointer',
                  }}
                >
                  Delayed
                </button>
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}