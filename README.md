# 🏢 Hikvision Attendance Management System

Modern davomat nazorat tizimi - Hikvision yuz tanish terminallari orqali hodimlarning ish vaqtini avtomatik boshqarish.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)

## ✨ Asosiy Imkoniyatlar

- 🔐 **Avtomatik Davomat** - Hikvision DS-K1T343EFWX yuz tanish terminali orqali kirish/chiqishni qayd etish
- 📊 **Real-time Dashboard** - Jonli statistika va vizualizatsiya
- 📈 **Hisobotlar** - Kunlik, haftalik va oylik davomat hisobotlari
- ⏰ **Kechikish Monitoring** - Avtomatik kechikish va erta ketishni aniqlash
- 👥 **Hodimlar Boshqaruvi** - To'liq CRUD operatsiyalar
- 🔒 **JWT Autentifikatsiya** - Xavfsiz token-based auth
- 🔄 **Avtomatik Sinxronizatsiya** - Celery orqali background tasks
- 🎯 **Role-based Access Control** - Turli ruxsatlar tizimi

## 🛠 Texnologiyalar

### Backend
- **Django 4.2** - Web framework
- **Django REST Framework** - RESTful API
- **PostgreSQL** - Database
- **Celery** - Background tasks
- **Redis** - Message broker
- **Simple JWT** - Authentication

### Frontend
- **React 18** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Query** - Data fetching
- **Zustand** - State management
- **Recharts** - Data visualization
- **Axios** - HTTP client

## 🚀 Tezkor Boshlash

### Talablar

- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+

### 1️⃣ Repository'ni Clone qilish

```bash
git clone https://github.com/hojiakbar-py/hikvision_project.git
cd hikvision_project
```

### 2️⃣ Backend o'rnatish

```bash
cd backend

# Virtual environment yaratish
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Dependencies o'rnatish
pip install -r requirements.txt

# PostgreSQL bazasini yaratish
createdb attendance_db

# Environment o'rnatish
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# .env faylini tahrirlang (DB, Hikvision sozlamalari)

# Database migratsiyalari
python manage.py migrate

# Superuser yaratish
python manage.py createsuperuser

# Development serverni ishga tushirish
python manage.py runserver
```

Backend: http://localhost:8000

### 3️⃣ Frontend o'rnatish

```bash
cd frontend

# Dependencies o'rnatish
npm install

# Environment o'rnatish
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Development serverni ishga tushirish
npm run dev
```

Frontend: http://localhost:5173

### 4️⃣ Celery (Background Tasks)

```bash
# Terminal 1: Redis serverni ishga tushirish
redis-server

# Terminal 2: Celery worker
cd backend
celery -A config worker -l info

# Terminal 3: Celery beat (jadval bo'yicha sinxronizatsiya)
celery -A config beat -l info
```

## ⚙️ Environment Sozlamalari

`backend/.env` fayliga quyidagilarni kiriting:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-generate-new-one
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DB_NAME=attendance_db
DB_USER=postgres
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=5432

# Hikvision Device
HIKVISION_IP=192.168.1.64
HIKVISION_PORT=80
HIKVISION_USERNAME=admin
HIKVISION_PASSWORD=your-device-password

# Celery & Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# CORS (Frontend URL)
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

`frontend/.env` fayliga:

```env
VITE_API_URL=http://localhost:8000/api
```

## 📡 API Endpoints

### Authentication
```
POST   /api/auth/token/          # JWT token olish
POST   /api/auth/token/refresh/  # Token yangilash
GET    /api/auth/profile/        # Foydalanuvchi profili
POST   /api/auth/register/       # Ro'yxatdan o'tish
```

### Hodimlar (Employees)
```
GET    /api/employees/                    # Hodimlar ro'yxati
POST   /api/employees/                    # Yangi hodim qo'shish
GET    /api/employees/{id}/               # Hodim ma'lumotlari
PUT    /api/employees/{id}/               # Hodimni yangilash
DELETE /api/employees/{id}/               # Hodimni o'chirish
GET    /api/employees/departments/        # Bo'limlar ro'yxati
GET    /api/employees/positions/          # Lavozimlar ro'yxati
```

### Davomat (Attendance)
```
GET    /api/attendance/dashboard/         # Dashboard statistika
GET    /api/attendance/daily/             # Kunlik davomat
GET    /api/attendance/daily/today/       # Bugungi davomat
GET    /api/attendance/report/monthly/    # Oylik hisobot
GET    /api/attendance/report/employee/{id}/  # Hodim hisoboti
POST   /api/attendance/manual/            # Qo'lda davomat qo'shish
```

### Hikvision Devices
```
GET    /api/hikvision/devices/                   # Qurilmalar ro'yxati
POST   /api/hikvision/devices/                   # Yangi qurilma qo'shish
GET    /api/hikvision/devices/{id}/              # Qurilma ma'lumotlari
POST   /api/hikvision/devices/{id}/sync/         # Ma'lumotlarni sinxronizatsiya
POST   /api/hikvision/devices/{id}/test_connection/  # Aloqani tekshirish
GET    /api/hikvision/devices/{id}/logs/         # Qurilma loglari
```

## 📖 Foydalanish Qo'llanmasi

### 1. Admin Panel orqali Boshlash

1. **Admin panelga kiring**: http://localhost:8000/admin/
   - Login/parol: superuser yaratganda kiritgan ma'lumotlar

2. **Bo'limlar va Lavozimlar yaratish**:
   - Employees → Departments → Add
   - Employees → Positions → Add

3. **Hodimlarni qo'shish**:
   - Employees → Employees → Add Employee
   - ⚠️ **Muhim**: `employee_id` Hikvision qurilmadagi ID bilan bir xil bo'lishi kerak!

4. **Hikvision qurilmani ulash**:
   - Hikvision → Devices → Add Device
   - IP, username, password kiriting
   - "Test Connection" tugmasini bosing

5. **Davomat ma'lumotlarini sinxronizatsiya**:
   - Device sahifasida "Sync" tugmasini bosing
   - Yoki Celery Beat avtomatik sinxronizatsiya qiladi

### 2. Frontend orqali Foydalanish

1. **Login**: http://localhost:5173/login
2. **Dashboard**: Real-time statistika ko'rish
3. **Hodimlar**: Hodimlarni boshqarish
4. **Bugungi Davomat**: Jonli kirish/chiqish ma'lumotlari
5. **Hisobotlar**: Oylik hisobotlarni eksport qilish
6. **Qurilmalar**: Hikvision qurilmalarni boshqarish

## 🔧 Hikvision Qurilma Sozlamalari

### Qurilmani tarmoqqa ulash

1. **IP manzilini aniqlash**:
   - SADP Tool (Hikvision) yordamida qurilmani toping
   - Yoki qurilmaning displaysidan: Menu → Network → TCP/IP

2. **Web interfeys orqali sozlash**:
   ```
   http://QURILMA-IP-MANZILI
   ```
   - Default login: `admin`
   - Password: qurilmaga birinchi kirish paytida o'rnatiladi

3. **ISAPI protokolini yoqish**:
   - Configuration → Network → Advanced Settings → Integration Protocol
   - ✅ Enable ISAPI
   - Enable Hikvision-CGI
   - Save

4. **Hodimlarni qurilmaga qo'shish**:
   - Access Control → Person → Add
   - **Employee No**: Backend'dagi `employee_id` bilan bir xil bo'lishi kerak!
   - Yuz rasmini yuklang va o'rgating

5. **Event parametrlarini sozlash**:
   - Event → Access Control → Configure
   - Access Control Event tipini tanlang
   - Notification Method: Notify Surveillance Center

### Troubleshooting

**Qurilmaga ulanib bo'lmasa**:
- Ping orqali aloqani tekshiring: `ping QURILMA-IP`
- Firewall sozlamalarini tekshiring
- ISAPI protokoli yoqilganligini tasdiqlang

**Davomat ma'lumotlari kelmasa**:
- Employee ID'lar mos kelishini tekshiring
- Event notifications yoqilganligini tekshiring
- Celery worker va beat ishlab turganligini tekshiring

## 🏗 Loyiha Strukturasi

```
hikvision_project/
├── backend/
│   ├── apps/
│   │   ├── accounts/      # Foydalanuvchilar va autentifikatsiya
│   │   ├── employees/     # Hodimlar boshqaruvi
│   │   ├── attendance/    # Davomat tizimi
│   │   ├── hikvision/     # Hikvision integratsiya
│   │   └── core/          # Umumiy models va utilities
│   ├── config/            # Django settings
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/          # API client
│   │   ├── components/   # React komponentlar
│   │   ├── pages/        # Sahifalar
│   │   └── store/        # State management
│   └── package.json
└── README.md
```

## 🤝 Hissa Qo'shish

1. Fork qiling
2. Feature branch yarating (`git checkout -b feature/AjoyibFunksiya`)
3. O'zgarishlarni commit qiling (`git commit -m 'Ajoyib funksiya qo'shildi'`)
4. Branch'ga push qiling (`git push origin feature/AjoyibFunksiya`)
5. Pull Request oching

## 📝 License

Ushbu loyiha [MIT License](LICENSE) ostida litsenziyalangan.

## 👨‍💻 Muallif

**Hojiakbar** - [GitHub](https://github.com/hojiakbar-py)

Bu loyiha Claude AI yordamida ishlab chiqildi.

---

⭐ Agar loyiha foydali bo'lsa, GitHub'da star qo'yishni unutmang!
