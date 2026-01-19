/**
 * CanEdit Component
 *
 * Edit permission-based conditional rendering.
 * Tahrirlash huquqi bo'lsa, children'ni ko'rsatadi.
 */

import { useAuthStore } from '../store/authStore'
import { canEditEmployee, canEditSalary } from '../utils/permissions'

export default function CanEdit({
  children,
  employee = null,
  salary = null,
  customCheck = null,
  fallback = null,
  showDisabled = false
}) {
  const { user } = useAuthStore()

  let canEdit = false

  // Custom check
  if (customCheck && typeof customCheck === 'function') {
    canEdit = customCheck(user, employee || salary)
  }
  // Employee edit check
  else if (employee) {
    canEdit = canEditEmployee(user, employee)
  }
  // Salary edit check
  else if (salary) {
    canEdit = canEditSalary(user, salary.employee || salary)
  }

  // Agar edit qila olmasa
  if (!canEdit) {
    // showDisabled = true bo'lsa, disabled holatda ko'rsatish
    if (showDisabled && children) {
      // Children'ni disabled qilish (agar form element bo'lsa)
      return (
        <div className="opacity-50 pointer-events-none cursor-not-allowed">
          {children}
        </div>
      )
    }

    // Fallback ko'rsatish yoki hech narsa
    return fallback || null
  }

  // Edit mumkin - children'ni ko'rsatish
  return children
}
