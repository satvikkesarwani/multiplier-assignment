import React, { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../api/api'

// Create the Auth Context
const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)          // Logged-in user object
  const [loading, setLoading] = useState(true)    // Checking if user is already logged in

  // On app load: try to restore session from localStorage token
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      authAPI.getMe()
        .then((res) => setUser(res.data))
        .catch(() => {
          // Token is invalid or expired — clear it
          localStorage.removeItem('access_token')
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  // Save token and fetch user info
  const login = async (token) => {
    localStorage.setItem('access_token', token)
    const res = await authAPI.getMe()
    setUser(res.data)
  }

  // Clear token and user state
  const logout = () => {
    localStorage.removeItem('access_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

// Custom hook for easy access to auth context
export function useAuth() {
  return useContext(AuthContext)
}
