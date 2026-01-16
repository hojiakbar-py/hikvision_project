import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  ArrowLeft,
  User,
  Building2,
  Phone,
  Mail,
  Calendar,
  Clock,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Timer,
} from 'lucide-react'
import { employeesApi } from '../api/employees'

export default function EmployeeProfile() {
  const { id } = useParams()
  const navigate = useNavigate()

  const { data, isLoading, error } = useQuery({
    queryKey: ['employee-profile', id],
    queryFn: () => employeesApi.getProfile(id),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">Xatolik yuz berdi</p>
        <button onClick={() => navigate('/employees')} className="btn-primary mt-4">
          Orqaga qaytish
        </button>
      </div>
    )
  }

  const { employee, today, monthly_stats, attendance_history } = data

  const formatMinutes = (minutes) => {
    if (!minutes) return '0 daq'
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    if (hours > 0) {
      return `${hours} soat ${mins} daq`
    }
    return `${mins} daq`
  }

  const getStatusColor = (status) => {
    const colors = {
      present: 'text-green-600 bg-green-100',
      absent: 'text-red-600 bg-red-100',
      late: 'text-orange-600 bg-orange-100',
      early_leave: 'text-yellow-600 bg-yellow-100',
      late_and_early: 'text-red-600 bg-red-100',
    }
    return colors[status] || 'text-gray-600 bg-gray-100'
  }

  const getStatusLabel = (status) => {
    const labels = {
      present: 'Kelgan',
      absent: 'Kelmagan',
      late: 'Kechikkan',
      early_leave: 'Erta ketgan',
      late_and_early: 'Kech/Erta',
      half_day: 'Yarim kun',
      on_leave: "Ta'tilda",
      holiday: 'Dam olish',
    }
    return labels[status] || status
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/employees')}
          className="p-2 hover:bg-gray-100 rounded-lg"
        >
          <ArrowLeft size={24} />
        </button>
        <h1 className="text-2xl font-bold text-gray-800">Hodim profili</h1>
      </div>

      {/* Main Info */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Employee Card */}
        <div className="card">
          <div className="flex flex-col items-center text-center">
            <div className="w-24 h-24 bg-primary-100 rounded-full flex items-center justify-center mb-4">
              <span className="text-3xl font-bold text-primary-600">
                {employee.first_name?.[0]}{employee.last_name?.[0]}
              </span>
            </div>
            <h2 className="text-xl font-bold text-gray-800">{employee.full_name}</h2>
            <p className="text-gray-500">{employee.position_name || 'Lavozim belgilanmagan'}</p>

            <div className="w-full mt-6 space-y-3">
              <div className="flex items-center gap-3 text-gray-600">
                <User size={18} className="text-gray-400" />
                <span>ID: {employee.employee_id}</span>
              </div>
              <div className="flex items-center gap-3 text-gray-600">
                <Building2 size={18} className="text-gray-400" />
                <span>{employee.department_name || '-'}</span>
              </div>
              <div className="flex items-center gap-3 text-gray-600">
                <Phone size={18} className="text-gray-400" />
                <span>{employee.phone || '-'}</span>
              </div>
              <div className="flex items-center gap-3 text-gray-600">
                <Mail size={18} className="text-gray-400" />
                <span>{employee.email || '-'}</span>
              </div>
              <div className="flex items-center gap-3 text-gray-600">
                <Calendar size={18} className="text-gray-400" />
                <span>Ishga qabul: {employee.hire_date}</span>
              </div>
              <div className="flex items-center gap-3 text-gray-600">
                <Clock size={18} className="text-gray-400" />
                <span>Ish vaqti: {employee.work_start_time} - {employee.work_end_time}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Today Status */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Bugungi holat</h3>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <span className="text-gray-600">Holat</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(today.status)}`}>
                {getStatusLabel(today.status)}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-green-50 rounded-lg">
                <p className="text-sm text-gray-500 mb-1">Kirish vaqti</p>
                <p className="text-2xl font-bold text-green-600">
                  {today.check_in || '-'}
                </p>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-gray-500 mb-1">Chiqish vaqti</p>
                <p className="text-2xl font-bold text-blue-600">
                  {today.check_out || '-'}
                </p>
              </div>
            </div>

            {today.late_minutes > 0 && (
              <div className="flex items-center gap-2 p-3 bg-orange-50 rounded-lg text-orange-700">
                <AlertTriangle size={18} />
                <span>Kechikish: {formatMinutes(today.late_minutes)}</span>
              </div>
            )}

            {today.early_leave_minutes > 0 && (
              <div className="flex items-center gap-2 p-3 bg-yellow-50 rounded-lg text-yellow-700">
                <AlertTriangle size={18} />
                <span>Erta ketish: {formatMinutes(today.early_leave_minutes)}</span>
              </div>
            )}

            {today.work_minutes > 0 && (
              <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg text-gray-700">
                <Timer size={18} />
                <span>Ishlagan vaqt: {formatMinutes(today.work_minutes)}</span>
              </div>
            )}
          </div>
        </div>

        {/* Monthly Stats */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Oylik statistika ({monthly_stats.month})
          </h3>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-green-50 rounded-lg text-center">
                <p className="text-2xl font-bold text-green-600">{monthly_stats.present_days}</p>
                <p className="text-xs text-gray-500">Kelgan kun</p>
              </div>
              <div className="p-3 bg-red-50 rounded-lg text-center">
                <p className="text-2xl font-bold text-red-600">{monthly_stats.absent_days}</p>
                <p className="text-xs text-gray-500">Kelmagan</p>
              </div>
              <div className="p-3 bg-orange-50 rounded-lg text-center">
                <p className="text-2xl font-bold text-orange-600">{monthly_stats.late_days}</p>
                <p className="text-xs text-gray-500">Kechikkan</p>
              </div>
              <div className="p-3 bg-yellow-50 rounded-lg text-center">
                <p className="text-2xl font-bold text-yellow-600">{monthly_stats.early_leave_days}</p>
                <p className="text-xs text-gray-500">Erta ketgan</p>
              </div>
            </div>

            <div className="border-t pt-4 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 flex items-center gap-2">
                  <TrendingDown size={16} className="text-orange-500" />
                  Jami kechikish
                </span>
                <span className="font-semibold text-orange-600">
                  {formatMinutes(monthly_stats.total_late_minutes)}
                </span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-gray-600 flex items-center gap-2">
                  <TrendingDown size={16} className="text-yellow-500" />
                  Jami erta ketish
                </span>
                <span className="font-semibold text-yellow-600">
                  {formatMinutes(monthly_stats.total_early_leave_minutes)}
                </span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-gray-600 flex items-center gap-2">
                  <TrendingUp size={16} className="text-green-500" />
                  Jami ish vaqti
                </span>
                <span className="font-semibold text-green-600">
                  {monthly_stats.total_work_hours} soat
                </span>
              </div>

              {monthly_stats.late_days > 0 && (
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">O'rtacha kechikish</span>
                  <span className="font-semibold text-gray-800">
                    {formatMinutes(monthly_stats.avg_late_minutes)}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Attendance History */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Davomat tarixi (oxirgi 30 kun)</h3>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Sana</th>
                <th className="text-center py-3 px-4 font-medium text-gray-500">Holat</th>
                <th className="text-center py-3 px-4 font-medium text-gray-500">Kirish</th>
                <th className="text-center py-3 px-4 font-medium text-gray-500">Chiqish</th>
                <th className="text-center py-3 px-4 font-medium text-gray-500">Kechikish</th>
                <th className="text-center py-3 px-4 font-medium text-gray-500">Erta ketish</th>
                <th className="text-center py-3 px-4 font-medium text-gray-500">Ish vaqti</th>
              </tr>
            </thead>
            <tbody>
              {attendance_history.map((record, index) => (
                <tr key={index} className="border-t">
                  <td className="py-3 px-4">
                    <span className="font-medium">{record.date}</span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(record.status)}`}>
                      {getStatusLabel(record.status)}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    {record.first_check_in ? (
                      <span className="text-green-600 font-mono text-sm">
                        {new Date(record.first_check_in).toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-center">
                    {record.last_check_out ? (
                      <span className="text-blue-600 font-mono text-sm">
                        {new Date(record.last_check_out).toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-center">
                    {record.late_minutes > 0 ? (
                      <span className="text-orange-600 font-medium">{record.late_minutes} daq</span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-center">
                    {record.early_leave_minutes > 0 ? (
                      <span className="text-yellow-600 font-medium">{record.early_leave_minutes} daq</span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-center">
                    {record.total_work_minutes > 0 ? (
                      <span className="text-gray-700">{formatMinutes(record.total_work_minutes)}</span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                </tr>
              ))}

              {attendance_history.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-gray-500">
                    Davomat ma'lumotlari topilmadi
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
