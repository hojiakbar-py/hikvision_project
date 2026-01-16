import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import {
  Settings as SettingsIcon,
  Clock,
  Plus,
  Trash2,
  Building2,
  Users,
} from 'lucide-react'
import { attendanceApi } from '../api/attendance'
import { employeesApi } from '../api/employees'

export default function Settings() {
  const [activeTab, setActiveTab] = useState('schedules')
  const queryClient = useQueryClient()

  const { data: schedules } = useQuery({
    queryKey: ['schedules'],
    queryFn: attendanceApi.getSchedules,
  })

  const { data: departments } = useQuery({
    queryKey: ['departments'],
    queryFn: employeesApi.getDepartments,
  })

  const createScheduleMutation = useMutation({
    mutationFn: attendanceApi.createSchedule,
    onSuccess: () => {
      queryClient.invalidateQueries(['schedules'])
      toast.success("Jadval qo'shildi")
      scheduleReset()
    },
    onError: () => toast.error("Xatolik yuz berdi"),
  })

  const createDepartmentMutation = useMutation({
    mutationFn: employeesApi.createDepartment,
    onSuccess: () => {
      queryClient.invalidateQueries(['departments'])
      toast.success("Bo'lim qo'shildi")
      departmentReset()
    },
    onError: () => toast.error("Xatolik yuz berdi"),
  })

  const {
    register: scheduleRegister,
    handleSubmit: handleScheduleSubmit,
    reset: scheduleReset,
    formState: { errors: scheduleErrors },
  } = useForm({
    defaultValues: {
      start_time: '09:00',
      end_time: '18:00',
      late_threshold_minutes: 5,
      early_leave_threshold_minutes: 5,
    },
  })

  const {
    register: departmentRegister,
    handleSubmit: handleDepartmentSubmit,
    reset: departmentReset,
  } = useForm()

  const onScheduleSubmit = (data) => {
    createScheduleMutation.mutate(data)
  }

  const onDepartmentSubmit = (data) => {
    createDepartmentMutation.mutate(data)
  }

  const tabs = [
    { id: 'schedules', name: 'Ish jadvallari', icon: Clock },
    { id: 'departments', name: "Bo'limlar", icon: Building2 },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Sozlamalar</h1>

      {/* Tabs */}
      <div className="border-b">
        <nav className="flex gap-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 py-3 px-4 border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <tab.icon size={20} />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Work Schedules Tab */}
      {activeTab === 'schedules' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Existing Schedules */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Mavjud jadvallar</h2>
            <div className="space-y-3">
              {schedules?.results?.map((schedule) => (
                <div
                  key={schedule.id}
                  className={`p-4 rounded-lg border ${
                    schedule.is_default ? 'border-primary-200 bg-primary-50' : 'border-gray-200'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Clock size={18} className="text-gray-500" />
                      <span className="font-medium text-gray-800">{schedule.name}</span>
                    </div>
                    {schedule.is_default && (
                      <span className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full">
                        Standart
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-gray-600">
                    <p>
                      <span className="text-gray-500">Vaqt:</span>{' '}
                      {schedule.start_time} - {schedule.end_time}
                    </p>
                    <p>
                      <span className="text-gray-500">Kechikish chegarasi:</span>{' '}
                      {schedule.late_threshold_minutes} daqiqa
                    </p>
                  </div>
                </div>
              ))}

              {schedules?.results?.length === 0 && (
                <p className="text-gray-500 text-center py-4">Jadvallar topilmadi</p>
              )}
            </div>
          </div>

          {/* Add New Schedule */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Yangi jadval qo'shish</h2>
            <form onSubmit={handleScheduleSubmit(onScheduleSubmit)} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Jadval nomi *
                </label>
                <input
                  {...scheduleRegister('name', { required: 'Majburiy' })}
                  className="input-field"
                  placeholder="Standart ish vaqti"
                />
                {scheduleErrors.name && (
                  <p className="text-red-500 text-sm mt-1">{scheduleErrors.name.message}</p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Boshlanish vaqti
                  </label>
                  <input
                    type="time"
                    {...scheduleRegister('start_time')}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tugash vaqti
                  </label>
                  <input
                    type="time"
                    {...scheduleRegister('end_time')}
                    className="input-field"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Kechikish chegarasi (daqiqa)
                  </label>
                  <input
                    type="number"
                    {...scheduleRegister('late_threshold_minutes')}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Erta ketish chegarasi (daqiqa)
                  </label>
                  <input
                    type="number"
                    {...scheduleRegister('early_leave_threshold_minutes')}
                    className="input-field"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  {...scheduleRegister('is_default')}
                  id="is_default"
                  className="w-4 h-4 text-primary-600 rounded"
                />
                <label htmlFor="is_default" className="text-sm text-gray-700">
                  Standart jadval sifatida belgilash
                </label>
              </div>

              <button type="submit" className="w-full btn-primary flex items-center justify-center gap-2">
                <Plus size={20} />
                Qo'shish
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Departments Tab */}
      {activeTab === 'departments' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Existing Departments */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Mavjud bo'limlar</h2>
            <div className="space-y-3">
              {departments?.results?.map((dept) => (
                <div
                  key={dept.id}
                  className="p-4 rounded-lg border border-gray-200 flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-gray-100 rounded-lg">
                      <Building2 size={20} className="text-gray-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-800">{dept.name}</p>
                      <p className="text-sm text-gray-500">{dept.employee_count} hodim</p>
                    </div>
                  </div>
                </div>
              ))}

              {departments?.results?.length === 0 && (
                <p className="text-gray-500 text-center py-4">Bo'limlar topilmadi</p>
              )}
            </div>
          </div>

          {/* Add New Department */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Yangi bo'lim qo'shish</h2>
            <form onSubmit={handleDepartmentSubmit(onDepartmentSubmit)} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Bo'lim nomi *
                </label>
                <input
                  {...departmentRegister('name', { required: 'Majburiy' })}
                  className="input-field"
                  placeholder="IT bo'limi"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tavsif
                </label>
                <textarea
                  {...departmentRegister('description')}
                  className="input-field"
                  rows={3}
                  placeholder="Bo'lim haqida qisqacha..."
                />
              </div>

              <button type="submit" className="w-full btn-primary flex items-center justify-center gap-2">
                <Plus size={20} />
                Qo'shish
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
