import React from 'react'
import PreviewCard from './PreviewCard'

/**
 * PreviewGrid — renders a responsive grid of PreviewCard items.
 * Shows an empty state message when there are no saved previews.
 */
function PreviewGrid({ previews }) {
  return (
    <section className="preview-section">
      <h2>
        🗂️ Saved Previews
        {previews.length > 0 && (
          <span className="badge" style={{ marginLeft: '0.5rem' }}>
            {previews.length}
          </span>
        )}
      </h2>

      <div className="preview-grid">
        {previews.length === 0 ? (
          <div className="empty-state">
            <div className="icon">🔍</div>
            <p>No previews yet. Submit a URL above to get started!</p>
          </div>
        ) : (
          previews.map((preview) => (
            <PreviewCard key={preview.id} preview={preview} />
          ))
        )}
      </div>
    </section>
  )
}

export default PreviewGrid
