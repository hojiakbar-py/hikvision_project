/**
 * Permission Utilities
 *
 * Frontend uchun role-based permission checking.
 * Backend'dagi User model permission metodlari bilan mos.
 */

// Rollar (backend bilan bir xil)
export const ROLES = {
  EMPLOYEE: 'employee',
  MANAGER: 'manager',
  ACCOUNTANT: 'accountant',
  CHIEF_ACCOUNTANT: 'chief_accountant',
  SUPERUSER: 'superuser',

  // Legacy support
  ADMIN: 'admin',
  HR: 'hr',
  VIEWER: 'viewer',
}

// Role display nomlar
export const ROLE_LABELS = {
  [ROLES.EMPLOYEE]: 'Oddiy xodim',
  [ROLES.MANAGER]: "Bo'lim boshlig'i",
  [ROLES.ACCOUNTANT]: 'Buxgalter',
  [ROLES.CHIEF_ACCOUNTANT]: 'Glavniy buxgalter',
  [ROLES.SUPERUSER]: 'Administrator',
  [ROLES.ADMIN]: 'Administrator',
  [ROLES.HR]: 'HR Manager',
  [ROLES.VIEWER]: "Ko'ruvchi",
}

// Role ranglar (badge uchun)
export const ROLE_COLORS = {
  [ROLES.EMPLOYEE]: 'gray',
  [ROLES.MANAGER]: 'blue',
  [ROLES.ACCOUNTANT]: 'green',
  [ROLES.CHIEF_ACCOUNTANT]: 'purple',
  [ROLES.SUPERUSER]: 'red',
  [ROLES.ADMIN]: 'red',
  [ROLES.HR]: 'indigo',
  [ROLES.VIEWER]: 'gray',
}

/**
 * Foydalanuvchining roli borligini tekshirish
 *
 * @param {Object} user - Foydalanuvchi obyekti
 * @param {string|string[]} roles - Tekshiriladigan rol(lar)
 * @returns {boolean}
 */
export const hasRole = (user, roles) => {
  if (!user || !user.role) return false

  const roleArray = Array.isArray(roles) ? roles : [roles]
  return roleArray.includes(user.role)
}

/**
 * Foydalanuvchi permission ga ega yoki yo'qligini tekshirish
 *
 * Backend'dagi has_permission() metodi bilan mos.
 *
 * @param {Object} user - Foydalanuvchi obyekti
 * @param {string} permission - Permission nomi
 * @returns {boolean}
 */
export const hasPermission = (user, permission) => {
  if (!user || !user.role) return false

  // Superuser har doim ruxsat oladi
  if (user.role === ROLES.SUPERUSER || user.role === ROLES.ADMIN) {
    return true
  }

  // Permission mapping (backend bilan bir xil)
  const permissionMap = {
    // Legacy permissions
    can_manage_users: [ROLES.ADMIN, ROLES.SUPERUSER],
    can_edit_employees: [ROLES.ADMIN, ROLES.HR, ROLES.SUPERUSER],
    can_view_reports: [
      ROLES.ADMIN, ROLES.HR, ROLES.VIEWER,
      ROLES.MANAGER, ROLES.ACCOUNTANT,
      ROLES.CHIEF_ACCOUNTANT, ROLES.SUPERUSER
    ],
    can_manage_devices: [ROLES.ADMIN, ROLES.SUPERUSER],
    can_sync_attendance: [ROLES.ADMIN, ROLES.HR, ROLES.SUPERUSER],

    // TZ bo'yicha yangi permissions
    can_view_own_data: [
      ROLES.EMPLOYEE, ROLES.MANAGER,
      ROLES.ACCOUNTANT, ROLES.CHIEF_ACCOUNTANT,
      ROLES.SUPERUSER
    ],
    can_edit_department_salary: [ROLES.MANAGER],
    can_submit_to_accountant: [ROLES.MANAGER],
    can_approve_salary: [
      ROLES.ACCOUNTANT,
      ROLES.CHIEF_ACCOUNTANT,
      ROLES.SUPERUSER
    ],
    can_return_to_manager: [
      ROLES.ACCOUNTANT,
      ROLES.CHIEF_ACCOUNTANT,
      ROLES.SUPERUSER
    ],
    can_final_approve: [ROLES.CHIEF_ACCOUNTANT, ROLES.SUPERUSER],
    can_export_to_1c: [ROLES.CHIEF_ACCOUNTANT, ROLES.SUPERUSER],
    can_unlock_documents: [ROLES.SUPERUSER],
    can_view_all_departments: [
      ROLES.ACCOUNTANT,
      ROLES.CHIEF_ACCOUNTANT,
      ROLES.SUPERUSER
    ],
    can_edit_with_comment: [
      ROLES.MANAGER,
      ROLES.ACCOUNTANT,
      ROLES.CHIEF_ACCOUNTANT,
      ROLES.SUPERUSER
    ],
  }

  const allowedRoles = permissionMap[permission] || []
  return allowedRoles.includes(user.role)
}

/**
 * Role-based utility funksiyalar
 */
export const isEmployee = (user) => user?.role === ROLES.EMPLOYEE
export const isManager = (user) => user?.role === ROLES.MANAGER
export const isAccountant = (user) => user?.role === ROLES.ACCOUNTANT
export const isChiefAccountant = (user) => user?.role === ROLES.CHIEF_ACCOUNTANT
export const isSuperuser = (user) => user?.role === ROLES.SUPERUSER || user?.role === ROLES.ADMIN

/**
 * Hodimni tahrirlash huquqi bormi
 *
 * @param {Object} user - Foydalanuvchi
 * @param {Object} employee - Hodim (optional)
 * @returns {boolean}
 */
export const canEditEmployee = (user, employee = null) => {
  if (!user) return false

  // Superuser va Chief Accountant - hammani
  if (isSuperuser(user) || isChiefAccountant(user)) {
    return true
  }

  // Accountant - hammani (izoh bilan)
  if (isAccountant(user)) {
    return true
  }

  // Manager - faqat o'z bo'limidagi hodimlar
  if (isManager(user) && employee) {
    // Employee.department_id === user.managed_department?.id
    return employee.department?.id === user.employee?.department?.id
  }

  // Employee - hech kimni tahrirlolmaydi
  return false
}

/**
 * Hodimni ko'rish huquqi bormi
 *
 * @param {Object} user - Foydalanuvchi
 * @param {Object} employee - Hodim (optional)
 * @returns {boolean}
 */
export const canViewEmployee = (user, employee = null) => {
  if (!user) return false

  // O'zi bo'lsa
  if (employee && user.employee?.id === employee.id) {
    return true
  }

  // Superuser, Chief, Accountant - hammani
  if (isSuperuser(user) || isChiefAccountant(user) || isAccountant(user)) {
    return true
  }

  // Manager - o'z bo'limidagi hodimlar
  if (isManager(user) && employee) {
    return employee.department?.id === user.employee?.department?.id
  }

  // Employee - faqat o'ziniki
  if (isEmployee(user)) {
    return employee && user.employee?.id === employee.id
  }

  return false
}

/**
 * Ish haqini tahrirlash huquqi
 *
 * TZ talabi:
 * - Employee: Yo'q
 * - Manager: Faqat o'z bo'limidagi hodimlar
 * - Accountant: Hamma (izoh bilan)
 * - Chief Accountant: Hamma
 * - Superuser: Hamma
 */
export const canEditSalary = (user, employee = null) => {
  if (!user) return false

  // Employee - yo'q
  if (isEmployee(user)) return false

  // Superuser va Chief - hamma
  if (isSuperuser(user) || isChiefAccountant(user)) return true

  // Accountant - hamma
  if (isAccountant(user)) return true

  // Manager - faqat o'z bo'limi
  if (isManager(user) && employee) {
    return employee.department?.id === user.managed_department?.id
  }

  return false
}

/**
 * Ish haqini ko'rish huquqi
 */
export const canViewSalary = (user, employee = null) => {
  if (!user) return false

  // O'zi bo'lsa
  if (employee && user.employee?.id === employee.id) return true

  // Superuser, Chief, Accountant - hamma
  if (isSuperuser(user) || isChiefAccountant(user) || isAccountant(user)) {
    return true
  }

  // Manager - o'z bo'limi
  if (isManager(user) && employee) {
    return employee.department?.id === user.managed_department?.id
  }

  // Employee - faqat o'ziniki
  if (isEmployee(user)) {
    return employee && user.employee?.id === employee.id
  }

  return false
}

/**
 * Ish haqini tasdiqlash huquqi
 */
export const canApproveSalary = (user) => {
  return hasPermission(user, 'can_approve_salary')
}

/**
 * Yakuniy tasdiqlash va 1C ga yuklash huquqi
 */
export const canFinalApprove = (user) => {
  return hasPermission(user, 'can_final_approve')
}

/**
 * Managerga qaytarish huquqi
 */
export const canReturnToManager = (user) => {
  return hasPermission(user, 'can_return_to_manager')
}

/**
 * 1C ga export qilish huquqi
 */
export const canExportTo1C = (user) => {
  return hasPermission(user, 'can_export_to_1c')
}

/**
 * Barcha bo'limlarni ko'rish huquqi
 */
export const canViewAllDepartments = (user) => {
  return hasPermission(user, 'can_view_all_departments')
}

/**
 * Rolni display qilish uchun label olish
 */
export const getRoleLabel = (role) => {
  return ROLE_LABELS[role] || role
}

/**
 * Rolni display qilish uchun rang olish
 */
export const getRoleColor = (role) => {
  return ROLE_COLORS[role] || 'gray'
}

/**
 * User ma'lumotlarini formatlash
 */
export const formatUser = (user) => {
  if (!user) return null

  return {
    ...user,
    roleLabel: getRoleLabel(user.role),
    roleColor: getRoleColor(user.role),
    isEmployee: isEmployee(user),
    isManager: isManager(user),
    isAccountant: isAccountant(user),
    isChiefAccountant: isChiefAccountant(user),
    isSuperuser: isSuperuser(user),
  }
}

export default {
  ROLES,
  ROLE_LABELS,
  ROLE_COLORS,
  hasRole,
  hasPermission,
  isEmployee,
  isManager,
  isAccountant,
  isChiefAccountant,
  isSuperuser,
  canEditEmployee,
  canViewEmployee,
  canEditSalary,
  canViewSalary,
  canApproveSalary,
  canFinalApprove,
  canReturnToManager,
  canExportTo1C,
  canViewAllDepartments,
  getRoleLabel,
  getRoleColor,
  formatUser,
}
