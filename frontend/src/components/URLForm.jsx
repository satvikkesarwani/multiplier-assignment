import React, { useState } from 'react'
import { previewAPI } from '../api/api'

/**
 * URLForm — input box for submitting a URL.
 * Calls the backend to take a screenshot, then notifies the parent.
 */
function URLForm({ onPreviewAdded }) {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!url.trim()) return

    // Ensure URL has a protocol
    const fullUrl = url.startsWith('http') ? url : `https://${url}`

    setLoading(true)
    setError('')

    try {
      const res = await previewAPI.create(fullUrl)
      onPreviewAdded(res.data)  // Pass new preview to parent (Dashboard)
      setUrl('')                // Clear input after success
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate preview. Try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card url-form-card">
      <h2>🌐 Add a URL Preview</h2>

      {error && <div className="alert alert-error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="url-input-row">
          <input
            id="url-input"
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.example.com"
            disabled={loading}
          />
          <button
            id="submit-url-btn"
            type="submit"
            className="btn btn-primary"
            disabled={loading || !url.trim()}
          >
            {loading ? (
              <>
                <div className="spinner" />
                Capturing...
              </>
            ) : (
              'Preview'
            )}
          </button>
        </div>
      </form>

      {loading && (
        <p style={{ marginTop: '1rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          ⏳ Taking screenshot... This may take up to 30 seconds for complex sites.
        </p>
      )}
    </div>
  )
}

export default URLForm
