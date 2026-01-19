/**
 * RoleBadge Component
 *
 * User rolini ko'rsatuvchi badge component.
 */

import { getRoleLabel, getRoleColor, ROLES } from '../utils/permissions'

// Tailwind rang klasslar
const colorClasses = {
  gray: 'bg-gray-100 text-gray-800 border-gray-200',
  blue: 'bg-blue-100 text-blue-800 border-blue-200',
  green: 'bg-green-100 text-green-800 border-green-200',
  purple: 'bg-purple-100 text-purple-800 border-purple-200',
  red: 'bg-red-100 text-red-800 border-red-200',
  indigo: 'bg-indigo-100 text-indigo-800 border-indigo-200',
  yellow: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  pink: 'bg-pink-100 text-pink-800 border-pink-200',
}

// Role icon'lar
const roleIcons = {
  [ROLES.EMPLOYEE]: '👤',
  [ROLES.MANAGER]: '👔',
  [ROLES.ACCOUNTANT]: '📊',
  [ROLES.CHIEF_ACCOUNTANT]: '👨‍💼',
  [ROLES.SUPERUSER]: '⚡',
  [ROLES.ADMIN]: '⚡',
  [ROLES.HR]: '🎯',
  [ROLES.VIEWER]: '👁️',
}

export default function RoleBadge({
  role,
  user = null,
  size = 'md',
  showIcon = true,
  className = ''
}) {
  // User obyektidan rol olish
  const userRole = role || user?.role

  if (!userRole) return null

  const label = getRoleLabel(userRole)
  const color = getRoleColor(userRole)
  const icon = roleIcons[userRole] || '👤'

  // Size klasslar
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5',
  }

  return (
    <span
      className={`
        inline-flex items-center gap-1.5
        rounded-full border font-medium
        ${colorClasses[color] || colorClasses.gray}
        ${sizeClasses[size]}
        ${className}
      `}
    >
      {showIcon && <span className="text-base">{icon}</span>}
      <span>{label}</span>
    </span>
  )
}
