import api from './axios'

export const employeesApi = {
  getAll: async (params = {}) => {
    const response = await api.get('/employees/', { params })
    return response.data
  },

  getById: async (id) => {
    const response = await api.get(`/employees/${id}/`)
    return response.data
  },

  create: async (data) => {
    const response = await api.post('/employees/', data)
    return response.data
  },

  update: async (id, data) => {
    const response = await api.patch(`/employees/${id}/`, data)
    return response.data
  },

  delete: async (id) => {
    await api.delete(`/employees/${id}/`)
  },

  getStatistics: async () => {
    const response = await api.get('/employees/statistics/')
    return response.data
  },

  getProfile: async (id) => {
    const response = await api.get(`/employees/${id}/profile/`)
    return response.data
  },

  // Departments
  getDepartments: async () => {
    const response = await api.get('/employees/departments/')
    return response.data
  },

  createDepartment: async (data) => {
    const response = await api.post('/employees/departments/', data)
    return response.data
  },

  // Positions
  getPositions: async (departmentId = null) => {
    const params = departmentId ? { department: departmentId } : {}
    const response = await api.get('/employees/positions/', { params })
    return response.data
  },
  
}
