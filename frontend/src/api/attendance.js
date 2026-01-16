import api from './axios'

export const attendanceApi = {
  // Dashboard
  getDashboard: async () => {
    const response = await api.get('/attendance/dashboard/')
    return response.data
  },

  // Daily attendance
  getDaily: async (params = {}) => {
    const response = await api.get('/attendance/daily/', { params })
    return response.data
  },

  getToday: async () => {
    const response = await api.get('/attendance/daily/today/')
    return response.data
  },

  getLateToday: async () => {
    const response = await api.get('/attendance/daily/late_today/')
    return response.data
  },

  getDailyById: async (id) => {
    const response = await api.get(`/attendance/daily/${id}/`)
    return response.data
  },

  // Reports
  getEmployeeReport: async (employeeId, startDate, endDate) => {
    const response = await api.get(`/attendance/report/employee/${employeeId}/`, {
      params: { start_date: startDate, end_date: endDate },
    })
    return response.data
  },

  getMonthlyReport: async (year, month, departmentId = null) => {
    const params = { year, month }
    if (departmentId) params.department = departmentId
    const response = await api.get('/attendance/report/monthly/', { params })
    return response.data
  },

  // Raw records
  getRecords: async (params = {}) => {
    const response = await api.get('/attendance/records/', { params })
    return response.data
  },

  // Work schedules
  getSchedules: async () => {
    const response = await api.get('/attendance/schedules/')
    return response.data
  },

  createSchedule: async (data) => {
    const response = await api.post('/attendance/schedules/', data)
    return response.data
  },
}
