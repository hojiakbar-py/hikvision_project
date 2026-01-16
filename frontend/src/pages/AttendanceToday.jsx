import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  Calendar,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  ChevronRight,
  RefreshCw,
} from 'lucide-react'
import { format } from 'date-fns'
import { attendanceApi } from '../api/attendance'
import { hikvisionApi } from '../api/hikvision'
import toast from 'react-hot-toast'

export default function AttendanceToday() {
  const [syncing, setSyncing] = useState(false)

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['attendance-today'],
    queryFn: attendanceApi.getToday,
    refetchInterval: 30000, // Har 30 soniyada
  })

  const handleSync = async () => {
    setSyncing(true)
    try {
      await hikvisionApi.manualSync(null, 1) // Oxirgi 1 soat
      toast.success("Sinxronizatsiya boshlandi")
      setTimeout(() => {
        refetch()
        setSyncing(false)
      }, 3000)
    } catch (error) {
      toast.error("Sinxronizatsiyada xatolik")
      setSyncing(false)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'present':
        return <CheckCircle className="text-green-500" size={20} />
      case 'late':
      case 'late_and_early':
        return <AlertTriangle className="text-yellow-500" size={20} />
      case 'early_leave':
        return <Clock className="text-orange-500" size={20} />
      case 'absent':
        return <XCircle className="text-red-500" size={20} />
      default:
        return <Clock className="text-gray-400" size={20} />
    }
  }

  const getStatusText = (status) => {
    const texts = {
      present: 'Vaqtida keldi',
      late: 'Kechikdi',
      early_leave: 'Erta ketdi',
      late_and_early: 'Kechikdi va erta ketdi',
      absent: 'Kelmadi',
    }
    return texts[status] || status
  }

  const getStatusColor = (status) => {
    const colors = {
      present: 'bg-green-100 text-green-700',
      late: 'bg-yellow-100 text-yellow-700',
      early_leave: 'bg-orange-100 text-orange-700',
      late_and_early: 'bg-red-100 text-red-700',
      absent: 'bg-gray-100 text-gray-700',
    }
    return colors[status] || 'bg-gray-100 text-gray-700'
  }

  const attendance = data || []

  // Statistikalar
  const stats = {
    total: attendance.length,
    present: attendance.filter(a => a.status === 'present').length,
    late: attendance.filter(a => ['late', 'late_and_early'].includes(a.status)).length,
    absent: attendance.filter(a => a.status === 'absent').length,
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Bugungi davomat</h1>
          <p className="text-gray-500 mt-1">
            {format(new Date(), "d MMMM, yyyy")} - {format(new Date(), "EEEE")}
          </p>
        </div>
        <button
          onClick={handleSync}
          disabled={syncing}
          className="btn-primary flex items-center gap-2"
        >
          <RefreshCw size={20} className={syncing ? 'animate-spin' : ''} />
          {syncing ? 'Sinxronlanmoqda...' : 'Yangilash'}
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card flex items-center gap-4">
          <div className="p-3 bg-blue-100 rounded-lg">
            <Calendar className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <p className="text-sm text-gray-500">Jami</p>
            <p className="text-xl font-bold text-gray-800">{stats.total}</p>
          </div>
        </div>

        <div className="card flex items-center gap-4">
          <div className="p-3 bg-green-100 rounded-lg">
            <CheckCircle className="w-6 h-6 text-green-600" />
          </div>
          <div>
            <p className="text-sm text-gray-500">Vaqtida</p>
            <p className="text-xl font-bold text-gray-800">{stats.present}</p>
          </div>
        </div>

        <div className="card flex items-center gap-4">
          <div className="p-3 bg-yellow-100 rounded-lg">
            <AlertTriangle className="w-6 h-6 text-yellow-600" />
          </div>
          <div>
            <p className="text-sm text-gray-500">Kechikkan</p>
            <p className="text-xl font-bold text-gray-800">{stats.late}</p>
          </div>
        </div>

        <div className="card flex items-center gap-4">
          <div className="p-3 bg-red-100 rounded-lg">
            <XCircle className="w-6 h-6 text-red-600" />
          </div>
          <div>
            <p className="text-sm text-gray-500">Kelmagan</p>
            <p className="text-xl font-bold text-gray-800">{stats.absent}</p>
          </div>
        </div>
      </div>

      {/* Attendance List */}
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
                  <th className="text-left py-4 px-6 font-medium text-gray-500">Hodim</th>
                  <th className="text-left py-4 px-6 font-medium text-gray-500">Bo'lim</th>
                  <th className="text-center py-4 px-6 font-medium text-gray-500">Keldi</th>
                  <th className="text-center py-4 px-6 font-medium text-gray-500">Ketdi</th>
                  <th className="text-center py-4 px-6 font-medium text-gray-500">Kechikish</th>
                  <th className="text-center py-4 px-6 font-medium text-gray-500">Holat</th>
                  <th className="text-right py-4 px-6 font-medium text-gray-500"></th>
                </tr>
              </thead>
              <tbody>
                {attendance.map((record) => (
                  <tr key={record.id} className="border-t hover:bg-gray-50">
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(record.status)}
                        <div>
                          <p className="font-medium text-gray-800">{record.employee_name}</p>
                          <p className="text-sm text-gray-500">{record.employee_id}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-6 text-gray-600">{record.department_name || '-'}</td>
                    <td className="py-4 px-6 text-center">
                      <span className="font-mono text-gray-800">
                        {record.check_in_time || '-'}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="font-mono text-gray-800">
                        {record.check_out_time || '-'}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-center">
                      {record.late_minutes > 0 ? (
                        <span className="text-red-600 font-medium">
                          +{record.late_minutes} daqiqa
                        </span>
                      ) : (
                        <span className="text-green-600">-</span>
                      )}
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(record.status)}`}>
                        {getStatusText(record.status)}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-right">
                      <Link
                        to={`/reports/employee/${record.employee}`}
                        className="text-primary-600 hover:text-primary-700"
                      >
                        <ChevronRight size={20} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {attendance.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                Bugungi davomat ma'lumotlari topilmadi
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
