import api from './axios'

export const authApi = {
  login: async (username, password) => {
    const response = await api.post('/auth/token/', { username, password })
    return response.data
  },
  
  register: async (data) => {
    const response = await api.post('/auth/register/', data)
    return response.data
  },

  refreshToken: async (refresh) => {
    const response = await api.post('/auth/token/refresh/', { refresh })
    return response.data
  },

  getProfile: async () => {
    const response = await api.get('/auth/profile/')
    return response.data
  },

  updateProfile: async (data) => {
    const response = await api.patch('/auth/profile/', data)
    return response.data
  },

  changePassword: async (oldPassword, newPassword) => {
    const response = await api.post('/auth/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
    })
    return response.data
  },
  importFromDevice: async (deviceId) => {
    const response = await api.post('/employees/import_from_device/', {
      device_id: deviceId
    })
    return response.data
  },
}
