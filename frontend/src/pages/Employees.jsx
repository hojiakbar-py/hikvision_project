import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Download } from 'lucide-react'
import {
  Plus,
  Search,
  Edit2,
  Trash2,
  X,
  Building2,
  Phone,
  User,
  Clock,
  LogIn,
  LogOut,
  Eye,
} from 'lucide-react'
import { employeesApi } from '../api/employees'

export default function Employees() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingEmployee, setEditingEmployee] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [departmentFilter, setDepartmentFilter] = useState('')
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  const importMutation = useMutation({
    mutationFn: (deviceId) =>
      employeesApi.importFromDevice(deviceId),
    onSuccess: (data) => {
      queryClient.invalidateQueries(['employees'])
      toast.success(`${data.imported} ta hodim import qilindi`)
    },
    onError: () => toast.error("Import xatolik"),
  })

  const { data: employees = [], isLoading } = useQuery({
    queryKey: ['employees', { search: searchQuery, department: departmentFilter }],
    queryFn: async () => {
      const response = await employeesApi.getAll({
        search: searchQuery,
        department: departmentFilter || undefined,
        limit: 1000
      })
      // Agar pagination bo'lsa results, agar yo'q bo'lsa to'g'ridan-to'g'ri array
      return response.results || response || []
    }
  })

  const { data: departments } = useQuery({
    queryKey: ['departments'],
    queryFn: employeesApi.getDepartments,
  })

  const { data: positions } = useQuery({
    queryKey: ['positions'],
    queryFn: () => employeesApi.getPositions(),
  })

  const createMutation = useMutation({
    mutationFn: employeesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['employees'])
      toast.success("Hodim qo'shildi")
      closeModal()
    },
    onError: () => toast.error("Xatolik yuz berdi"),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => employeesApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['employees'])
      toast.success("Hodim yangilandi")
      closeModal()
    },
    onError: () => toast.error("Xatolik yuz berdi"),
  })

  const deleteMutation = useMutation({
    mutationFn: employeesApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['employees'])
      toast.success("Hodim o'chirildi")
    },
    onError: () => toast.error("Xatolik yuz berdi"),
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm()

  const openModal = (employee = null) => {
    if (employee) {
      setEditingEmployee(employee)
      reset(employee)
    } else {
      setEditingEmployee(null)
      reset({
        work_start_time: '09:00',
        work_end_time: '18:00',
        status: 'active',
      })
    }
    setIsModalOpen(true)
  }

  const closeModal = () => {
    setIsModalOpen(false)
    setEditingEmployee(null)
    reset()
  }

  const onSubmit = (data) => {
    if (editingEmployee) {
      updateMutation.mutate({ id: editingEmployee.id, data })
    } else {
      createMutation.mutate(data)
    }
  }

  const handleDelete = (id, e) => {
    e.stopPropagation()
    if (window.confirm("Hodimni o'chirishni tasdiqlaysizmi?")) {
      deleteMutation.mutate(id)
    }
  }

  const getStatusBadge = (status) => {
    const styles = {
      active: 'bg-green-100 text-green-700',
      inactive: 'bg-gray-100 text-gray-700',
      on_leave: 'bg-yellow-100 text-yellow-700',
    }
    const labels = {
      active: 'Faol',
      inactive: 'Nofaol',
      on_leave: "Ta'tilda",
    }
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    )
  }

  const getTodayStatusBadge = (status) => {
    const styles = {
      present: 'bg-green-100 text-green-700',
      absent: 'bg-red-100 text-red-700',
      late: 'bg-orange-100 text-orange-700',
      early_leave: 'bg-yellow-100 text-yellow-700',
      late_and_early: 'bg-red-100 text-red-700',
    }
    const labels = {
      present: 'Kelgan',
      absent: 'Kelmagan',
      late: 'Kechikkan',
      early_leave: 'Erta ketgan',
      late_and_early: 'Kech/Erta',
    }
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] || 'bg-gray-100 text-gray-700'}`}>
        {labels[status] || status}
      </span>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <h1 className="text-2xl font-bold text-gray-800">Hodimlar</h1>
        <div className="flex gap-2">
          <button 
            onClick={() => {
              const deviceId = prompt('Qurilma ID ni kiriting:')
              if (deviceId) importMutation.mutate(parseInt(deviceId))
            }}
            className="btn-secondary flex items-center gap-2"
            disabled={importMutation.isPending}
          >
            {importMutation.isPending ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <Download size={20} />
            )}
            Import qilish
          </button>
          <button onClick={() => openModal()} className="btn-primary flex items-center gap-2">
            <Plus size={20} />
            Yangi hodim
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Ism, familiya, ID yoki telefon bo'yicha qidirish..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-field pl-10"
            />
          </div>
          <select
            value={departmentFilter}
            onChange={(e) => setDepartmentFilter(e.target.value)}
            className="input-field sm:w-48"
          >
            <option value="">Barcha bo'limlar</option>
            {departments?.results?.map((dept) => (
              <option key={dept.id} value={dept.id}>
                {dept.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
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
                  <th className="text-left py-4 px-4 font-medium text-gray-500">Hodim</th>
                  <th className="text-left py-4 px-4 font-medium text-gray-500">ID</th>
                  <th className="text-left py-4 px-4 font-medium text-gray-500">Bo'lim</th>
                  <th className="text-left py-4 px-4 font-medium text-gray-500">Telefon</th>
                  <th className="text-left py-4 px-4 font-medium text-gray-500">Holat</th>
                  <th className="text-center py-4 px-4 font-medium text-gray-500">
                    <div className="flex items-center justify-center gap-1">
                      <LogIn size={14} />
                      Kirish
                    </div>
                  </th>
                  <th className="text-center py-4 px-4 font-medium text-gray-500">
                    <div className="flex items-center justify-center gap-1">
                      <LogOut size={14} />
                      Chiqish
                    </div>
                  </th>
                  <th className="text-center py-4 px-4 font-medium text-gray-500">Bugun</th>
                  <th className="text-right py-4 px-4 font-medium text-gray-500">Amallar</th>
                </tr>
              </thead>
              <tbody>
                {Array.isArray(employees) && employees.map((employee) => (
                  <tr
                    key={employee.id}
                    className="border-t hover:bg-gray-50 cursor-pointer"
                    onClick={() => navigate(`/employees/${employee.id}`)}
                  >
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-primary-600 font-medium">
                            {employee.first_name?.[0] || '?'}
                          </span>
                        </div>
                        <div className="min-w-0">
                          <p className="font-medium text-gray-800 truncate">{employee.full_name}</p>
                          <p className="text-sm text-gray-500 truncate">{employee.position_name || '-'}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-mono text-sm text-gray-600">{employee.employee_id}</span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2 text-gray-600 text-sm">
                        <Building2 size={14} className="flex-shrink-0" />
                        <span className="truncate">{employee.department_name || '-'}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2 text-gray-600 text-sm">
                        <Phone size={14} className="flex-shrink-0" />
                        {employee.phone || '-'}
                      </div>
                    </td>
                    <td className="py-3 px-4">{getStatusBadge(employee.status)}</td>
                    <td className="py-3 px-4 text-center">
                      {employee.today_check_in ? (
                        <span className="font-mono text-sm text-green-600 font-medium">
                          {employee.today_check_in}
                        </span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-center">
                      {employee.today_check_out ? (
                        <span className="font-mono text-sm text-blue-600 font-medium">
                          {employee.today_check_out}
                        </span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-center">
                      {getTodayStatusBadge(employee.today_status)}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            navigate(`/employees/${employee.id}`)
                          }}
                          className="p-2 text-gray-500 hover:text-primary-600 hover:bg-primary-50 rounded-lg"
                          title="Profilni ko'rish"
                        >
                          <Eye size={18} />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            openModal(employee)
                          }}
                          className="p-2 text-gray-500 hover:text-primary-600 hover:bg-primary-50 rounded-lg"
                          title="Tahrirlash"
                        >
                          <Edit2 size={18} />
                        </button>
                        <button
                          onClick={(e) => handleDelete(employee.id, e)}
                          className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg"
                          title="O'chirish"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {(!employees || employees.length === 0) && (
              <div className="text-center py-12 text-gray-500">
                Hodimlar topilmadi. Qurilmadan import qiling yoki qo'lda qo'shing.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Jami */}
      {employees && employees.length > 0 && (
        <div className="text-sm text-gray-500 text-right">
          Jami: {employees.length} ta hodim
        </div>
      )}

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-xl font-bold text-gray-800">
                {editingEmployee ? "Hodimni tahrirlash" : "Yangi hodim qo'shish"}
              </h2>
              <button onClick={closeModal} className="text-gray-400 hover:text-gray-600">
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Hodim ID (Hikvision) *
                  </label>
                  <input
                    {...register('employee_id', { required: 'Majburiy' })}
                    className="input-field"
                    placeholder="001"
                  />
                  {errors.employee_id && (
                    <p className="text-red-500 text-sm mt-1">{errors.employee_id.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Ism *
                  </label>
                  <input
                    {...register('first_name', { required: 'Majburiy' })}
                    className="input-field"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Familiya *
                  </label>
                  <input
                    {...register('last_name', { required: 'Majburiy' })}
                    className="input-field"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Otasining ismi
                  </label>
                  <input {...register('middle_name')} className="input-field" />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Bo'lim
                  </label>
                  <select {...register('department')} className="input-field">
                    <option value="">Tanlang</option>
                    {departments?.results?.map((dept) => (
                      <option key={dept.id} value={dept.id}>
                        {dept.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Lavozim
                  </label>
                  <select {...register('position')} className="input-field">
                    <option value="">Tanlang</option>
                    {positions?.results?.map((pos) => (
                      <option key={pos.id} value={pos.id}>
                        {pos.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Telefon
                  </label>
                  <input
                    {...register('phone')}
                    className="input-field"
                    placeholder="+998901234567"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    {...register('email')}
                    className="input-field"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Ish boshlanish vaqti
                  </label>
                  <input
                    type="time"
                    {...register('work_start_time')}
                    className="input-field"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Ish tugash vaqti
                  </label>
                  <input
                    type="time"
                    {...register('work_end_time')}
                    className="input-field"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Ishga qabul sanasi *
                  </label>
                  <input
                    type="date"
                    {...register('hire_date', { required: 'Majburiy' })}
                    className="input-field"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Holat
                  </label>
                  <select {...register('status')} className="input-field">
                    <option value="active">Faol</option>
                    <option value="inactive">Nofaol</option>
                    <option value="on_leave">Ta'tilda</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t">
                <button type="button" onClick={closeModal} className="btn-secondary">
                  Bekor qilish
                </button>
                <button type="submit" className="btn-primary">
                  {editingEmployee ? 'Saqlash' : "Qo'shish"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}