/**
 * useAuth Hook
 *
 * Authentication va user ma'lumotlarini boshqarish.
 */

import { createContext, useContext, useState, useEffect } from 'react'
import { formatUser } from '../utils/permissions'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // Local storage'dan token va user olish
  useEffect(() => {
    const loadUser = () => {
      try {
        const token = localStorage.getItem('token')
        const storedUser = localStorage.getItem('user')

        if (token && storedUser) {
          const parsedUser = JSON.parse(storedUser)
          const formattedUser = formatUser(parsedUser)
          setUser(formattedUser)
          setIsAuthenticated(true)
        }
      } catch (error) {
        console.error('Error loading user:', error)
        logout()
      } finally {
        setIsLoading(false)
      }
    }

    loadUser()
  }, [])

  // Login funksiyasi
  const login = (token, userData) => {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(userData))

    const formattedUser = formatUser(userData)
    setUser(formattedUser)
    setIsAuthenticated(true)
  }

  // Logout funksiyasi
  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
    setIsAuthenticated(false)
  }

  // User ma'lumotlarini yangilash
  const updateUser = (userData) => {
    localStorage.setItem('user', JSON.stringify(userData))
    const formattedUser = formatUser(userData)
    setUser(formattedUser)
  }

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    updateUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export default useAuth
