import React, { useState, useEffect } from 'react'
import Navbar from '../components/Navbar'
import URLForm from '../components/URLForm'
import PreviewGrid from '../components/PreviewGrid'
import { previewAPI } from '../api/api'

/**
 * Dashboard Page — main page after login.
 * Shows the URL input form and all saved previews.
 */
function Dashboard() {
  const [previews, setPreviews] = useState([])
  const [fetchError, setFetchError] = useState('')

  // Load all saved previews on page mount
  useEffect(() => {
    previewAPI.list()
      .then((res) => setPreviews(res.data))
      .catch(() => setFetchError('Failed to load saved previews.'))
  }, [])

  // Add a new preview to the top of the list when submitted
  const handlePreviewAdded = (newPreview) => {
    setPreviews((prev) => [newPreview, ...prev])
  }

  return (
    <>
      <Navbar />

      <main className="dashboard">
        <div className="container">
          {/* Page Header */}
          <div className="dashboard-header">
            <h1>URL Preview Dashboard</h1>
            <p>Enter any website URL to capture and save a visual preview.</p>
          </div>

          {/* URL Input Form */}
          <URLForm onPreviewAdded={handlePreviewAdded} />

          {/* Error loading previews */}
          {fetchError && <div className="alert alert-error">{fetchError}</div>}

          {/* Saved Previews Grid */}
          <PreviewGrid previews={previews} />
        </div>
      </main>
    </>
  )
}

export default Dashboard
