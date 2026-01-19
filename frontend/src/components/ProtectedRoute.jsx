/**
 * Protected Route Component
 *
 * Role-based route protection.
 * Faqat ruxsat berilgan rollarga dostup beradi.
 */

import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { hasRole, hasPermission } from '../utils/permissions'

export default function ProtectedRoute({
  children,
  requiredRole = null,
  requiredRoles = null,
  requiredPermission = null,
  fallback = null
}) {
  const { user, isAuthenticated } = useAuthStore()

  // Autentifikatsiya tekshiruvi
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Role tekshiruvi
  if (requiredRole && !hasRole(user, requiredRole)) {
    return fallback || (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="text-6xl mb-4">🚫</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Dostup taqiqlangan
          </h2>
          <p className="text-gray-600 mb-4">
            Bu sahifaga kirish uchun sizda yetarli huquq yo'q.
          </p>
          <p className="text-sm text-gray-500">
            Sizning rolingiz: <span className="font-semibold">{user?.role}</span>
          </p>
          <button
            onClick={() => window.history.back()}
            className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Orqaga qaytish
          </button>
        </div>
      </div>
    )
  }

  // Multiple roles tekshiruvi
  if (requiredRoles && !hasRole(user, requiredRoles)) {
    return fallback || (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="text-6xl mb-4">🚫</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Dostup taqiqlangan
          </h2>
          <p className="text-gray-600 mb-4">
            Bu sahifaga kirish uchun sizda yetarli huquq yo'q.
          </p>
          <p className="text-sm text-gray-500">
            Sizning rolingiz: <span className="font-semibold">{user?.role}</span>
          </p>
          <button
            onClick={() => window.history.back()}
            className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Orqaga qaytish
          </button>
        </div>
      </div>
    )
  }

  // Permission tekshiruvi
  if (requiredPermission && !hasPermission(user, requiredPermission)) {
    return fallback || (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="text-6xl mb-4">🔒</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Ruxsat kerak
          </h2>
          <p className="text-gray-600 mb-4">
            Bu amaliyot uchun sizda yetarli ruxsat yo'q.
          </p>
          <p className="text-sm text-gray-500">
            Kerakli ruxsat: <span className="font-semibold">{requiredPermission}</span>
          </p>
          <button
            onClick={() => window.history.back()}
            className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Orqaga qaytish
          </button>
        </div>
      </div>
    )
  }

  // Dostup berildi
  return children
}
