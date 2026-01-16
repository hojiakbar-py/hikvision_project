import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import {
  Server,
  Plus,
  Wifi,
  WifiOff,
  RefreshCw,
  Settings,
  Trash2,
  X,
  CheckCircle,
  AlertCircle,
  Download,
} from 'lucide-react'
import { hikvisionApi } from '../api/hikvision'

export default function Devices() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [testingDevice, setTestingDevice] = useState(null)
  const [syncingDevice, setSyncingDevice] = useState(null)
  const [importingDevice, setImportingDevice] = useState(null)
  const queryClient = useQueryClient()

  const { data: devices, isLoading } = useQuery({
    queryKey: ['devices'],
    queryFn: hikvisionApi.getDevices,
  })

  const { data: syncLogs } = useQuery({
    queryKey: ['sync-logs'],
    queryFn: hikvisionApi.getSyncLogs,
  })

  const { data: branches } = useQuery({
    queryKey: ['branches'],
    queryFn: hikvisionApi.getBranches,
  })

  const createMutation = useMutation({
    mutationFn: hikvisionApi.createDevice,
    onSuccess: () => {
      queryClient.invalidateQueries(['devices'])
      toast.success("Qurilma qo'shildi")
      setIsModalOpen(false)
      reset()
    },
    onError: (error) => {
      const errorMsg = error.response?.data?.detail || error.response?.data?.branch?.[0] || "Xatolik yuz berdi"
      toast.error(errorMsg)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: hikvisionApi.deleteDevice,
    onSuccess: () => {
      queryClient.invalidateQueries(['devices'])
      toast.success("Qurilma o'chirildi")
    },
    onError: () => toast.error("Xatolik yuz berdi"),
  })

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: {
      port: 80,
      username: 'admin',
    },
  })

  const testConnection = async (deviceId) => {
    setTestingDevice(deviceId)
    try {
      const result = await hikvisionApi.testConnection(deviceId)
      if (result.status === 'online') {
        toast.success(`Qurilma online: ${result.model || 'Unknown model'}`)
      } else {
        toast.error(`Qurilma offline: ${result.error || 'Unknown error'}`)
      }
      queryClient.invalidateQueries(['devices'])
    } catch (error) {
      toast.error("Test muvaffaqiyatsiz")
    } finally {
      setTestingDevice(null)
    }
  }

  const syncDevice = async (deviceId) => {
    setSyncingDevice(deviceId)
    try {
      const result = await hikvisionApi.syncDevice(deviceId, 24)
      toast.success(`Sinxronizatsiya muvaffaqiyatli: ${result.records_processed || 0} ta yozuv`)
      queryClient.invalidateQueries(['devices', 'sync-logs'])
    } catch (error) {
      const errorMsg = error.response?.data?.error || error.message || "Noma'lum xatolik"
      toast.error(`Sinxronizatsiyada xatolik: ${errorMsg}`)
      console.error('Sync error:', error.response?.data || error)
    } finally {
      setSyncingDevice(null)
    }
  }

  const importUsers = async (deviceId) => {
    setImportingDevice(deviceId)
    try {
      const result = await hikvisionApi.importUsers(deviceId)
      toast.success(`${result.imported} ta hodim import qilindi (${result.skipped} ta o'tkazib yuborildi)`)
      queryClient.invalidateQueries(['employees'])
    } catch (error) {
      const errorMsg = error.response?.data?.error || error.message || "Noma'lum xatolik"
      toast.error(`Import xatoligi: ${errorMsg}`)
      console.error('Import error:', error.response?.data || error)
    } finally {
      setImportingDevice(null)
    }
  }

  const onSubmit = (data) => {
    createMutation.mutate(data)
  }

  const handleDelete = (id) => {
    if (window.confirm("Qurilmani o'chirishni tasdiqlaysizmi?")) {
      deleteMutation.mutate(id)
    }
  }

  const getStatusBadge = (status) => {
    if (status === 'online') {
      return (
        <span className="flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
          <Wifi size={12} />
          Online
        </span>
      )
    }
    return (
      <span className="flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">
        <WifiOff size={12} />
        Offline
      </span>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <h1 className="text-2xl font-bold text-gray-800">Hikvision Qurilmalar</h1>
        <button onClick={() => setIsModalOpen(true)} className="btn-primary flex items-center gap-2">
          <Plus size={20} />
          Yangi qurilma
        </button>
      </div>

      {/* Devices Grid */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {devices?.results?.map((device) => (
            <div key={device.id} className="card">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`p-3 rounded-lg ${device.status === 'online' ? 'bg-green-100' : 'bg-gray-100'}`}>
                    <Server className={`w-6 h-6 ${device.status === 'online' ? 'text-green-600' : 'text-gray-400'}`} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800">{device.name}</h3>
                    <p className="text-sm text-gray-500">{device.ip_address}:{device.port}</p>
                  </div>
                </div>
                {getStatusBadge(device.status)}
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Model:</span>
                  <span className="text-gray-800">{device.model || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Seriya:</span>
                  <span className="text-gray-800 font-mono text-xs">{device.serial_number || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Oxirgi sync:</span>
                  <span className="text-gray-800">
                    {device.last_sync
                      ? new Date(device.last_sync).toLocaleString('uz-UZ')
                      : 'Hali yo\'q'}
                  </span>
                </div>
              </div>

              <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t">
                <button
                  onClick={() => testConnection(device.id)}
                  disabled={testingDevice === device.id}
                  className="flex-1 btn-secondary flex items-center justify-center gap-2 text-sm"
                >
                  {testingDevice === device.id ? (
                    <RefreshCw size={16} className="animate-spin" />
                  ) : (
                    <Wifi size={16} />
                  )}
                  Test
                </button>
                <button
                  onClick={() => syncDevice(device.id)}
                  disabled={syncingDevice === device.id}
                  className="flex-1 btn-primary flex items-center justify-center gap-2 text-sm"
                >
                  {syncingDevice === device.id ? (
                    <RefreshCw size={16} className="animate-spin" />
                  ) : (
                    <RefreshCw size={16} />
                  )}
                  Sync
                </button>
                <button
                  onClick={() => importUsers(device.id)}
                  disabled={importingDevice === device.id || device.status !== 'online'}
                  className="flex-1 btn-secondary flex items-center justify-center gap-2 text-sm"
                  title="Qurilmadagi foydalanuvchilarni hodimlar sifatida import qilish"
                >
                  {importingDevice === device.id ? (
                    <RefreshCw size={16} className="animate-spin" />
                  ) : (
                    <Download size={16} />
                  )}
                  Import
                </button>
                <button
                  onClick={() => handleDelete(device.id)}
                  className="p-2 text-red-500 hover:bg-red-50 rounded-lg"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}

          {devices?.results?.length === 0 && (
            <div className="col-span-full text-center py-12 text-gray-500">
              Qurilmalar topilmadi. Yangi qurilma qo'shing.
            </div>
          )}
        </div>
      )}

      {/* Recent Sync Logs */}
      {syncLogs?.results?.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Oxirgi sinxronizatsiyalar</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Qurilma</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Vaqt</th>
                  <th className="text-center py-3 px-4 font-medium text-gray-500 text-sm">Holat</th>
                  <th className="text-center py-3 px-4 font-medium text-gray-500 text-sm">Yozuvlar</th>
                </tr>
              </thead>
              <tbody>
                {syncLogs.results.slice(0, 10).map((log) => (
                  <tr key={log.id} className="border-b last:border-0">
                    <td className="py-3 px-4">{log.device_name}</td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {new Date(log.started_at).toLocaleString('uz-UZ')}
                    </td>
                    <td className="py-3 px-4 text-center">
                      {log.status === 'success' ? (
                        <span className="flex items-center justify-center gap-1 text-green-600">
                          <CheckCircle size={16} />
                          <span className="text-sm">Muvaffaqiyatli</span>
                        </span>
                      ) : (
                        <span className="flex items-center justify-center gap-1 text-red-600">
                          <AlertCircle size={16} />
                          <span className="text-sm">Xatolik</span>
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="bg-gray-100 px-2 py-1 rounded text-sm">
                        {log.records_processed} / {log.records_fetched}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add Device Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-xl font-bold text-gray-800">Yangi qurilma qo'shish</h2>
              <button onClick={() => setIsModalOpen(false)} className="text-gray-400 hover:text-gray-600">
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Filial *
                </label>
                <select
                  {...register('branch', { required: 'Majburiy' })}
                  className="input-field"
                >
                  <option value="">Filialni tanlang</option>
                  {branches?.results?.map((branch) => (
                    <option key={branch.id} value={branch.id}>
                      {branch.name}
                    </option>
                  ))}
                </select>
                {errors.branch && <p className="text-red-500 text-sm mt-1">{errors.branch.message}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Qurilma nomi *
                </label>
                <input
                  {...register('name', { required: 'Majburiy' })}
                  className="input-field"
                  placeholder="Asosiy kirish"
                />
                {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  IP manzil *
                </label>
                <input
                  {...register('ip_address', { required: 'Majburiy' })}
                  className="input-field"
                  placeholder="192.168.1.64"
                />
                {errors.ip_address && <p className="text-red-500 text-sm mt-1">{errors.ip_address.message}</p>}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Port</label>
                  <input
                    type="number"
                    {...register('port', { valueAsNumber: true })}
                    className="input-field"
                    placeholder="80"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Joylashuv</label>
                  <input
                    {...register('location')}
                    className="input-field"
                    placeholder="1-qavat"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Login *
                </label>
                <input
                  {...register('username', { required: 'Majburiy' })}
                  className="input-field"
                  placeholder="admin"
                  autoComplete="username"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Parol *
                </label>
                <input
                  type="password"
                  {...register('password', { required: 'Majburiy' })}
                  className="input-field"
                  autoComplete="new-password"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button type="button" onClick={() => setIsModalOpen(false)} className="btn-secondary">
                  Bekor qilish
                </button>
                <button type="submit" className="btn-primary">
                  Qo'shish
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
