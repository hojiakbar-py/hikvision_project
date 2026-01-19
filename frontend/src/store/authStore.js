import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { formatUser, hasPermission, hasRole, ROLES } from '../utils/permissions'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      token: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,

      setToken: (token) => set({ token }),

      login: (token, refreshToken, user) => {
        const formattedUser = formatUser(user)
        set({
          token,
          refreshToken,
          user: formattedUser,
          isAuthenticated: true,
        })
      },

      logout: () =>
        set({
          token: null,
          refreshToken: null,
          user: null,
          isAuthenticated: false,
        }),

      setUser: (user) => {
        const formattedUser = formatUser(user)
        set({ user: formattedUser })
      },

      // Role utility metodlar
      hasRole: (role) => {
        const { user } = get()
        return hasRole(user, role)
      },

      hasPermission: (permission) => {
        const { user } = get()
        return hasPermission(user, permission)
      },

      isEmployee: () => get().user?.role === ROLES.EMPLOYEE,
      isManager: () => get().user?.role === ROLES.MANAGER,
      isAccountant: () => get().user?.role === ROLES.ACCOUNTANT,
      isChiefAccountant: () => get().user?.role === ROLES.CHIEF_ACCOUNTANT,
      isSuperuser: () => {
        const role = get().user?.role
        return role === ROLES.SUPERUSER || role === ROLES.ADMIN
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
