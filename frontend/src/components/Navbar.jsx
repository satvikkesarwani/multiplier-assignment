import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

/**
 * Top navigation bar showing brand name, logged-in user, and logout button.
 */
function Navbar() {
  const { user, logout } = useAuth()

  return (
    <nav className="navbar">
      <div className="container">
        <Link to="/dashboard" className="navbar-brand" style={{ textDecoration: 'none' }}>
          🔗 URL<span>Preview</span>
        </Link>

        {user && (
          <div className="navbar-user">
            <p>
              Hello, <strong>{user.username}</strong>
            </p>
            <button className="btn btn-outline" onClick={logout} style={{ padding: '0.45rem 1rem', fontSize: '0.85rem' }}>
              Logout
            </button>
          </div>
        )}
      </div>
    </nav>
  )
}

export default Navbar
