import api from './axios'

export const hikvisionApi = {
  // Devices
  getDevices: async () => {
    const response = await api.get('/hikvision/devices/')
    return response.data
  },

  getDevice: async (id) => {
    const response = await api.get(`/hikvision/devices/${id}/`)
    return response.data
  },

  createDevice: async (data) => {
    const response = await api.post('/hikvision/devices/', data)
    return response.data
  },

  updateDevice: async (id, data) => {
    const response = await api.patch(`/hikvision/devices/${id}/`, data)
    return response.data
  },

  deleteDevice: async (id) => {
    await api.delete(`/hikvision/devices/${id}/`)
  },

  testConnection: async (id) => {
    const response = await api.post(`/hikvision/devices/${id}/test_connection/`)
    return response.data
  },

  syncDevice: async (id, hoursBack = 24) => {
    const response = await api.post(`/hikvision/devices/${id}/sync/`, {
      hours_back: hoursBack,
    })
    return response.data
  },

  getDeviceUsers: async (id) => {
    const response = await api.get(`/hikvision/devices/${id}/users/`)
    return response.data
  },

  getDeviceLogs: async (id) => {
    const response = await api.get(`/hikvision/devices/${id}/logs/`)
    return response.data
  },

  // Import users from device
  importUsers: async (id) => {
    const response = await api.post(`/hikvision/devices/${id}/import_users/`)
    return response.data
  },

  // Manual sync
  manualSync: async (deviceId = null, hoursBack = 24) => {
    const data = { hours_back: hoursBack }
    if (deviceId) data.device_id = deviceId
    const response = await api.post('/hikvision/sync/', data)
    return response.data
  },

  // Status
  getStatus: async () => {
    const response = await api.get('/hikvision/status/')
    return response.data
  },

  // Sync logs
  getSyncLogs: async () => {
    const response = await api.get('/hikvision/logs/')
    return response.data
  },

  // Branches
  getBranches: async () => {
    const response = await api.get('/core/branches/')
    return response.data
  },
}
