import React, { useState } from 'react'

/**
 * PreviewCard — shows one saved URL preview with its screenshot.
 */
function PreviewCard({ preview }) {
  const [imgError, setImgError] = useState(false)

  // Format the saved date in a readable way
  const formattedDate = new Date(preview.created_at).toLocaleString()

  // Build the full image URL (screenshot served by FastAPI's /static endpoint)
  const imageUrl = preview.screenshot_path || null

  return (
    <div className="preview-card">
      {/* Screenshot Image */}
      {imageUrl && !imgError ? (
        <img
          src={imageUrl}
          alt={`Preview of ${preview.url}`}
          className="preview-card-image"
          onError={() => setImgError(true)}  // Show placeholder if image fails to load
        />
      ) : (
        <div className="preview-card-image-placeholder">
          <span className="icon">🖼️</span>
          <span>Preview unavailable</span>
        </div>
      )}

      {/* Card Body */}
      <div className="preview-card-body">
        <p className="preview-card-url" title={preview.url}>
          {preview.url}
        </p>
        <p className="preview-card-date">
          🕒 Saved on {formattedDate}
        </p>
      </div>

      {/* Open link */}
      <div className="preview-card-actions">
        <a href={preview.url} target="_blank" rel="noopener noreferrer">
          ↗ Open website
        </a>
      </div>
    </div>
  )
}

export default PreviewCard
