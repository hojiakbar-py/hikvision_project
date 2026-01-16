import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Users,
  UserCheck,
  UserX,
  Clock,
  TrendingUp,
  TrendingDown,
  Calendar,
  BarChart3,
  PieChart as PieChartIcon,
  Activity,
  AlertCircle,
  Filter,
  Download,
} from 'lucide-react'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ScatterChart,
  Scatter,
} from 'recharts'
import { attendanceApi } from '../api/attendance'

const COLORS = {
  present: '#10b981',
  late: '#f59e0b',
  absent: '#ef4444',
  onTime: '#3b82f6',
  primary: '#6366f1',
  secondary: '#8b5cf6',
}

export default function Dashboard() {
  const [selectedPeriod, setSelectedPeriod] = useState('week')

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['dashboard', selectedPeriod],
    queryFn: attendanceApi.getDashboard,
    refetchInterval: 60000,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="text-center">
          <div className="w-14 h-14 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600 font-medium">Ma'lumotlar yuklanimoqda...</p>
          <p className="text-sm text-gray-400 mt-2">Bir oz kuting</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-gradient-to-r from-red-50 to-red-100 border-l-4 border-red-500 text-red-700 p-6 rounded-lg shadow-md">
        <div className="flex items-center gap-3">
          <AlertCircle className="w-6 h-6" />
          <div>
            <p className="font-bold text-lg">Xatolik yuz berdi</p>
            <p className="text-sm mt-1">Ma'lumotlarni yuklashda muammo. Qayta urinib ko'ring.</p>
            <button
              onClick={() => refetch()}
              className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
            >
              Qayta yuklash
            </button>
          </div>
        </div>
      </div>
    )
  }

  const today = data?.today || {}
  const weeklyTrend = data?.weekly_trend || []
  const topLate = data?.top_late_employees || []

  // Hisoblash
  const totalEmployees = today.total_employees || 0
  const presentCount = today.present || 0
  const attendanceRate = totalEmployees > 0 ? ((presentCount / totalEmployees) * 100).toFixed(1) : 0
  const lateCount = today.late || 0
  const absentCount = today.absent || 0

  const pieData = [
    { name: 'Vaqtida kelgan', value: today.on_time || 0, color: COLORS.onTime },
    { name: 'Kechikkan', value: today.late || 0, color: COLORS.late },
    { name: 'Kelmagan', value: today.absent || 0, color: COLORS.absent },
  ].filter(item => item.value > 0)

  const statsCards = [
    {
      title: 'Jami hodimlar',
      value: totalEmployees,
      icon: Users,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-600',
      change: '+2.5%',
      positive: true,
    },
    {
      title: 'Kelganlar',
      value: presentCount,
      subtitle: `${attendanceRate}% davolat`,
      icon: UserCheck,
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-50',
      textColor: 'text-green-600',
      change: '+5.2%',
      positive: true,
    },
    {
      title: 'Kechikkanlar',
      value: lateCount,
      icon: Clock,
      color: 'from-yellow-500 to-yellow-600',
      bgColor: 'bg-yellow-50',
      textColor: 'text-yellow-600',
      change: '-1.8%',
      positive: false,
    },
    {
      title: 'Kelmaganlar',
      value: absentCount,
      icon: UserX,
      color: 'from-red-500 to-red-600',
      bgColor: 'bg-red-50',
      textColor: 'text-red-600',
      change: '0%',
      positive: false,
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <button className="p-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <Download className="w-5 h-5 text-gray-600" />
            </button>
          </div>
          <p className="text-gray-600">Davomat tizimining real vaqtda analitikasi</p>
        </div>
        {/* Stats Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {statsCards.map((stat, index) => {
            const Icon = stat.icon
            return (
              <div
                key={index}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-medium text-gray-600">{stat.title}</h3>
                  <Icon className="w-5 h-5 text-gray-400" />
                </div>

                <p className="text-3xl font-bold text-gray-900 mb-3">{stat.value}</p>

                {stat.subtitle && (
                  <p className="text-xs text-gray-500 mb-2">{stat.subtitle}</p>
                )}

                <div className="flex items-center gap-1">
                  {stat.positive ? (
                    <TrendingUp className="w-4 h-4 text-green-600" />
                  ) : (
                    <TrendingDown className="w-4 h-4 text-red-600" />
                  )}
                  <span
                    className={`text-xs font-semibold ${
                      stat.positive ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {stat.change}
                  </span>
                </div>
              </div>
            )
          })}
        </div>

        
        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Weekly Trend - Advanced Area Chart */}
          <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Haftalik trend</h2>
                <p className="text-sm text-gray-500 mt-1">7 kun davomidagi davomat</p>
              </div>
              <BarChart3 className="w-6 h-6 text-gray-400" />
            </div>

            {weeklyTrend.length > 0 ? (
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={weeklyTrend} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorPresent" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={COLORS.present} stopOpacity={0.4} />
                        <stop offset="95%" stopColor={COLORS.present} stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="colorLate" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={COLORS.late} stopOpacity={0.4} />
                        <stop offset="95%" stopColor={COLORS.late} stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="colorAbsent" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={COLORS.absent} stopOpacity={0.4} />
                        <stop offset="95%" stopColor={COLORS.absent} stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
                    <XAxis
                      dataKey="date"
                      tickFormatter={(value) => {
                        const date = new Date(value)
                        return date.toLocaleDateString('uz-UZ', { weekday: 'narrow' })
                      }}
                      stroke="#9ca3af"
                      style={{ fontSize: '12px' }}
                    />
                    <YAxis stroke="#9ca3af" style={{ fontSize: '12px' }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        border: '1px solid #e5e7eb',
                        borderRadius: '12px',
                        boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
                      }}
                      cursor={{ stroke: '#e5e7eb', strokeWidth: 1 }}
                    />
                    <Legend wrapperStyle={{ paddingTop: '20px' }} />
                    <Area
                      type="monotone"
                      dataKey="present"
                      stroke={COLORS.present}
                      fill="url(#colorPresent)"
                      name="✓ Kelgan"
                      isAnimationActive={true}
                    />
                    <Area
                      type="monotone"
                      dataKey="late"
                      stroke={COLORS.late}
                      fill="url(#colorLate)"
                      name="⏰ Kechikkan"
                    />
                    <Area
                      type="monotone"
                      dataKey="absent"
                      stroke={COLORS.absent}
                      fill="url(#colorAbsent)"
                      name="✗ Kelmagan"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-96 flex items-center justify-center text-gray-400">
                <p>Ma'lumot yo'q</p>
              </div>
            )}
          </div>

          {/* Today's Status - Donut Chart */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Bugungi holat</h2>
                <p className="text-sm text-gray-500 mt-1">Davomat tahlili</p>
              </div>
              <Activity className="w-6 h-6 text-gray-400" />
            </div>

            {pieData.length > 0 ? (
              <>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={55}
                        outerRadius={95}
                        paddingAngle={3}
                        dataKey="value"
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        formatter={(value) => `${value} kishi`}
                        contentStyle={{
                          backgroundColor: 'rgba(255, 255, 255, 0.95)',
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px',
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                {/* Legend */}
                <div className="space-y-2 mt-6">
                  {pieData.map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: item.color }}
                        />
                        <span className="text-sm text-gray-600">{item.name}</span>
                      </div>
                      <span className="text-sm font-semibold text-gray-900">{item.value}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-400">
                <p>Ma'lumot yo'q</p>
              </div>
            )}
          </div>
        </div>

        {/* Top Late Employees Table */}
        {topLate && topLate.length > 0 && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Ko'p kechikkan hodimlar</h2>
                <p className="text-sm text-gray-500 mt-1">Top 10 hodim</p>
              </div>
              <AlertCircle className="w-6 h-6 text-orange-500" />
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b-2 border-gray-100">
                    <th className="text-left py-4 px-6 font-bold text-gray-700">№</th>
                    <th className="text-left py-4 px-6 font-bold text-gray-700">Ismi</th>
                    <th className="text-left py-4 px-6 font-bold text-gray-700">Bo'lim</th>
                    <th className="text-right py-4 px-6 font-bold text-gray-700">Kechikish vaqti</th>
                    <th className="text-right py-4 px-6 font-bold text-gray-700">Soni</th>
                  </tr>
                </thead>
                <tbody>
                  {topLate.map((emp, index) => (
                    <tr
                      key={index}
                      className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                    >
                      <td className="py-4 px-6">
                        <span className="inline-flex items-center justify-center w-8 h-8 bg-gradient-to-br from-primary-100 to-primary-200 text-primary-700 rounded-full text-sm font-bold">
                          {index + 1}
                        </span>
                      </td>
                      <td className="py-4 px-6">
                        <p className="font-semibold text-gray-900">{emp.name}</p>
                      </td>
                      <td className="py-4 px-6">
                        <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                          {emp.department || 'Nomalo\'m'}
                        </span>
                      </td>
                      <td className="py-4 px-6 text-right">
                        <p className="font-bold text-orange-600">
                          {emp.total_late_hours?.toFixed(1) || 0} soat
                        </p>
                      </td>
                      <td className="py-4 px-6 text-right">
                        <span className="inline-flex items-center justify-center w-8 h-8 bg-orange-100 text-orange-700 rounded-full font-bold text-sm">
                          {emp.late_count || 0}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}