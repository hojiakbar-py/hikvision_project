import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  Calendar,
  FileText,
  Settings,
  LogOut,
  Menu,
  X,
  Server,
  Clock,
  DollarSign,
  CheckCircle,
  Upload,
} from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { ROLES } from '../utils/permissions'
import RoleBadge from './RoleBadge'

// Role-based navigation
// Har bir menu item uchun qaysi rollar ko'rishi kerak
const navigationConfig = [
  {
    name: 'Dashboard',
    href: '/',
    icon: LayoutDashboard,
    roles: ['*'], // Barcha rollar
  },
  {
    name: 'Hodimlar',
    href: '/employees',
    icon: Users,
    roles: [ROLES.MANAGER, ROLES.ACCOUNTANT, ROLES.CHIEF_ACCOUNTANT, ROLES.SUPERUSER, ROLES.ADMIN, ROLES.HR],
  },
  {
    name: 'Bugungi davomat',
    href: '/attendance/today',
    icon: Calendar,
    roles: [ROLES.MANAGER, ROLES.ACCOUNTANT, ROLES.CHIEF_ACCOUNTANT, ROLES.SUPERUSER, ROLES.ADMIN, ROLES.HR],
  },
  {
    name: 'Ish haqi',
    href: '/salary',
    icon: DollarSign,
    roles: [ROLES.MANAGER, ROLES.ACCOUNTANT, ROLES.CHIEF_ACCOUNTANT, ROLES.SUPERUSER],
    badge: 'Yangi',
  },
  {
    name: 'Tasdiqlash',
    href: '/salary/approve',
    icon: CheckCircle,
    roles: [ROLES.ACCOUNTANT, ROLES.CHIEF_ACCOUNTANT, ROLES.SUPERUSER],
  },
  {
    name: '1C ga yuklash',
    href: '/salary/export',
    icon: Upload,
    roles: [ROLES.CHIEF_ACCOUNTANT, ROLES.SUPERUSER],
  },
  {
    name: 'Hisobotlar',
    href: '/reports',
    icon: FileText,
    roles: ['*'],
  },
  {
    name: 'Qurilmalar',
    href: '/devices',
    icon: Server,
    roles: [ROLES.SUPERUSER, ROLES.ADMIN],
  },
  {
    name: 'Sozlamalar',
    href: '/settings',
    icon: Settings,
    roles: ['*'],
  },
]

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  // Foydalanuvchi rolga mos navigation filter qilish
  const filteredNavigation = navigationConfig.filter((item) => {
    // Barcha rollarga ruxsat
    if (item.roles.includes('*')) return true

    // Foydalanuvchi rolini tekshirish
    return item.roles.includes(user?.role)
  })

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 z-50 h-full w-64 bg-white shadow-xl transform transition-transform duration-300 lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between px-6 py-5 border-b">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                <Clock className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <h1 className="font-bold text-gray-800">Davomat</h1>
                <p className="text-xs text-gray-500">Nazorat tizimi</p>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-gray-500"
            >
              <X size={24} />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            {filteredNavigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-50 text-primary-600'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <item.icon size={20} />
                  <span className="font-medium flex-1">{item.name}</span>
                  {item.badge && (
                    <span className="px-2 py-0.5 text-xs font-semibold bg-green-100 text-green-700 rounded-full">
                      {item.badge}
                    </span>
                  )}
                </Link>
              )
            })}
          </nav>

          {/* User info */}
          <div className="border-t p-4">
            <div className="space-y-3">
              <div className="flex items-center gap-3 px-2">
                <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center shadow-md">
                  <span className="text-white font-bold text-lg">
                    {user?.first_name?.[0] || user?.username?.[0] || 'U'}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-800 truncate">
                    {user?.first_name || user?.username}
                  </p>
                  <p className="text-xs text-gray-500 truncate">
                    {user?.email || user?.username}
                  </p>
                </div>
                <button
                  onClick={handleLogout}
                  className="text-gray-400 hover:text-red-500 transition-colors"
                  title="Chiqish"
                >
                  <LogOut size={20} />
                </button>
              </div>
              {/* Role Badge */}
              <div className="px-2">
                <RoleBadge user={user} size="sm" className="w-full justify-center" />
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:ml-64">
        {/* Top bar */}
        <header className="sticky top-0 z-30 bg-white border-b px-4 py-3 lg:px-6">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-gray-600"
            >
              <Menu size={24} />
            </button>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-500">
                {new Date().toLocaleDateString('uz-UZ', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 lg:p-6">{children}</main>
      </div>
    </div>
  )
}
