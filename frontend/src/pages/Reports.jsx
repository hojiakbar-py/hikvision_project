import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  FileText,
  Download,
  Calendar,
  Building2,
  TrendingUp,
  Clock,
} from 'lucide-react'
import { attendanceApi } from '../api/attendance'
import { employeesApi } from '../api/employees'

export default function Reports() {
  const currentDate = new Date()
  const [year, setYear] = useState(currentDate.getFullYear())
  const [month, setMonth] = useState(currentDate.getMonth() + 1)
  const [departmentId, setDepartmentId] = useState('')

  const { data: departments } = useQuery({
    queryKey: ['departments'],
    queryFn: employeesApi.getDepartments,
  })

  const { data: report, isLoading } = useQuery({
    queryKey: ['monthly-report', year, month, departmentId],
    queryFn: () => attendanceApi.getMonthlyReport(year, month, departmentId || undefined),
  })

  const months = [
    'Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'Iyun',
    'Iyul', 'Avgust', 'Sentabr', 'Oktabr', 'Noyabr', 'Dekabr'
  ]

  const years = Array.from({ length: 5 }, (_, i) => currentDate.getFullYear() - i)

  const exportToCSV = () => {
    if (!report?.employees) return

    const headers = [
      'Hodim ID', 'Ism', "Bo'lim", 'Lavozim', 'Ish kunlari', 'Kelgan kunlar',
      'Kelmagan', 'Kechikkan', 'Kechikish (daqiqa)', 'Ish soatlari', 'Davomat %'
    ]

    const rows = report.employees.map(emp => [
      emp.employee_id,
      emp.employee_name,
      emp.department || '',
      emp.position || '',
      emp.total_days,
      emp.present_days,
      emp.absent_days,
      emp.late_days,
      emp.total_late_minutes,
      emp.total_work_hours,
      emp.attendance_rate
    ])

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `davomat_${year}_${month}.csv`
    link.click()
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <h1 className="text-2xl font-bold text-gray-800">Oylik hisobot</h1>
        <button onClick={exportToCSV} className="btn-primary flex items-center gap-2">
          <Download size={20} />
          CSV yuklash
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">Yil</label>
            <select
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
              className="input-field"
            >
              {years.map(y => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">Oy</label>
            <select
              value={month}
              onChange={(e) => setMonth(Number(e.target.value))}
              className="input-field"
            >
              {months.map((m, i) => (
                <option key={i} value={i + 1}>{m}</option>
              ))}
            </select>
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">Bo'lim</label>
            <select
              value={departmentId}
              onChange={(e) => setDepartmentId(e.target.value)}
              className="input-field"
            >
              <option value="">Barcha bo'limlar</option>
              {departments?.results?.map((dept) => (
                <option key={dept.id} value={dept.id}>{dept.name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      {report && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="card">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <FileText className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Jami hodimlar</p>
                <p className="text-xl font-bold text-gray-800">{report.total_employees}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Calendar className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Davr</p>
                <p className="text-xl font-bold text-gray-800">{months[month - 1]}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Clock className="w-5 h-5 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">O'rtacha kechikish</p>
                <p className="text-xl font-bold text-gray-800">
                  {report.employees?.length > 0
                    ? Math.round(
                        report.employees.reduce((acc, e) => acc + e.total_late_minutes, 0) /
                          report.employees.length
                      )
                    : 0}{' '}
                  daqiqa
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <TrendingUp className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">O'rtacha davomat</p>
                <p className="text-xl font-bold text-gray-800">
                  {report.employees?.length > 0
                    ? Math.round(
                        report.employees.reduce((acc, e) => acc + e.attendance_rate, 0) /
                          report.employees.length
                      )
                    : 0}
                  %
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Report Table */}
      <div className="card overflow-hidden p-0">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left py-4 px-4 font-medium text-gray-500 text-sm">Hodim</th>
                  <th className="text-left py-4 px-4 font-medium text-gray-500 text-sm">Bo'lim</th>
                  <th className="text-center py-4 px-4 font-medium text-gray-500 text-sm">Ish kunlari</th>
                  <th className="text-center py-4 px-4 font-medium text-gray-500 text-sm">Kelgan</th>
                  <th className="text-center py-4 px-4 font-medium text-gray-500 text-sm">Kelmagan</th>
                  <th className="text-center py-4 px-4 font-medium text-gray-500 text-sm">Kechikkan</th>
                  <th className="text-center py-4 px-4 font-medium text-gray-500 text-sm">Kechikish</th>
                  <th className="text-center py-4 px-4 font-medium text-gray-500 text-sm">Ish soati</th>
                  <th className="text-center py-4 px-4 font-medium text-gray-500 text-sm">Davomat</th>
                </tr>
              </thead>
              <tbody>
                {report?.employees?.map((employee, index) => (
                  <tr key={index} className="border-t hover:bg-gray-50">
                    <td className="py-4 px-4">
                      <div>
                        <p className="font-medium text-gray-800">{employee.employee_name}</p>
                        <p className="text-sm text-gray-500">{employee.employee_id}</p>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-gray-600 text-sm">
                      {employee.department || '-'}
                    </td>
                    <td className="py-4 px-4 text-center text-gray-800">{employee.total_days}</td>
                    <td className="py-4 px-4 text-center">
                      <span className="text-green-600 font-medium">{employee.present_days}</span>
                    </td>
                    <td className="py-4 px-4 text-center">
                      <span className={`font-medium ${employee.absent_days > 0 ? 'text-red-600' : 'text-gray-400'}`}>
                        {employee.absent_days}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-center">
                      <span className={`font-medium ${employee.late_days > 0 ? 'text-yellow-600' : 'text-gray-400'}`}>
                        {employee.late_days}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-center">
                      <span className={`font-medium ${employee.total_late_minutes > 30 ? 'text-red-600' : 'text-gray-600'}`}>
                        {employee.total_late_minutes} d
                      </span>
                    </td>
                    <td className="py-4 px-4 text-center text-gray-800">
                      {employee.total_work_hours} s
                    </td>
                    <td className="py-4 px-4 text-center">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          employee.attendance_rate >= 90
                            ? 'bg-green-100 text-green-700'
                            : employee.attendance_rate >= 70
                            ? 'bg-yellow-100 text-yellow-700'
                            : 'bg-red-100 text-red-700'
                        }`}
                      >
                        {employee.attendance_rate}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {report?.employees?.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                Bu davr uchun ma'lumotlar topilmadi
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
