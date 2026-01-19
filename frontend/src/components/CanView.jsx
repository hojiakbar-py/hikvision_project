/**
 * CanView Component
 *
 * Permission-based conditional rendering.
 * Faqat permission bo'lsa, children'ni ko'rsatadi.
 */

import { useAuthStore } from '../store/authStore'
import { hasPermission, hasRole } from '../utils/permissions'

export default function CanView({
  children,
  permission = null,
  role = null,
  roles = null,
  fallback = null,
  employee = null,
  customCheck = null
}) {
  const { user } = useAuthStore()

  // Custom check function
  if (customCheck && typeof customCheck === 'function') {
    const canView = customCheck(user, employee)
    return canView ? children : (fallback || null)
  }

  // Permission check
  if (permission) {
    const can = hasPermission(user, permission)
    return can ? children : (fallback || null)
  }

  // Role check (single)
  if (role) {
    const can = hasRole(user, role)
    return can ? children : (fallback || null)
  }

  // Role check (multiple)
  if (roles) {
    const can = hasRole(user, roles)
    return can ? children : (fallback || null)
  }

  // Default - ko'rsatish
  return children
}
