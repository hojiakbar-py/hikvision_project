# Davomat Nazorat Tizimi

Hikvision DS-K1T343EFWX yuz tanish terminali orqali hodimlarning ish vaqtini nazorat qilish tizimi.

## Imkoniyatlar

- Hodimlarning kirish/chiqish vaqtini avtomatik qayd etish
- Kechikish va erta ketishni hisoblash
- Kunlik, haftalik va oylik hisobotlar
- Dashboard - real vaqtda statistika
- Hikvision qurilmalar bilan integratsiya
- JWT autentifikatsiya

## Texnologiyalar

### Backend
- Django 4.2
- Django REST Framework
- PostgreSQL
- JWT (Simple JWT)
- Celery + Redis (avtomatik sinxronizatsiya)

### Frontend
- React 18
- Vite
- Tailwind CSS
- React Query
- Zustand
- Recharts

## O'rnatish

### 1. PostgreSQL bazasini yaratish

```sql
CREATE DATABASE attendance_db;
```

### 2. Backend o'rnatish

```bash
cd backend

# Virtual environment yaratish
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Dependencies o'rnatish
pip install -r requirements.txt

# .env faylini yaratish
copy .env.example .env
# .env faylini tahrirlang va sozlamalarni kiriting

# Migratsiyalar
python manage.py makemigrations apps.accounts apps.employees apps.attendance apps.hikvision
python manage.py migrate

# Superuser yaratish
python manage.py createsuperuser

# Serverni ishga tushirish
python manage.py runserver
```

### 3. Frontend o'rnatish

```bash
cd frontend

# Dependencies o'rnatish
npm install

# Development serverni ishga tushirish
npm run dev
```

### 4. Celery (avtomatik sinxronizatsiya uchun)

```bash
# Redis serverni ishga tushiring

# Celery worker
celery -A config worker -l info

# Celery beat (jadval bo'yicha tasklar)
celery -A config beat -l info
```

## Sozlamalar

### .env fayl

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True

# Database
DB_NAME=attendance_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Hikvision
HIKVISION_IP=192.168.1.64
HIKVISION_PORT=80
HIKVISION_USERNAME=admin
HIKVISION_PASSWORD=your-device-password

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
```

## API Endpoints

### Auth
- `POST /api/auth/token/` - JWT token olish
- `POST /api/auth/token/refresh/` - Token yangilash
- `GET /api/auth/profile/` - Profil

### Hodimlar
- `GET /api/employees/` - Hodimlar ro'yxati
- `POST /api/employees/` - Yangi hodim
- `GET /api/employees/{id}/` - Hodim ma'lumotlari
- `GET /api/employees/departments/` - Bo'limlar
- `GET /api/employees/positions/` - Lavozimlar

### Davomat
- `GET /api/attendance/dashboard/` - Dashboard statistika
- `GET /api/attendance/daily/` - Kunlik davomat
- `GET /api/attendance/daily/today/` - Bugungi davomat
- `GET /api/attendance/report/monthly/` - Oylik hisobot
- `GET /api/attendance/report/employee/{id}/` - Hodim hisoboti

### Hikvision
- `GET /api/hikvision/devices/` - Qurilmalar
- `POST /api/hikvision/devices/{id}/sync/` - Sinxronizatsiya
- `POST /api/hikvision/devices/{id}/test_connection/` - Aloqani tekshirish

## Foydalanish

1. Admin panelga kiring: http://localhost:8000/admin/
2. Hodimlarni qo'shing (employee_id Hikvision dagi ID bilan bir xil bo'lishi kerak)
3. Hikvision qurilmani qo'shing va test qiling
4. Sinxronizatsiya bosing - davomat ma'lumotlari avtomatik yuklanadi
5. Frontend: http://localhost:5173/

## Hikvision qurilma sozlamalari

1. Qurilmaning IP manzilini aniqlang
2. Web interfeysga kiring (http://IP-ADDRESS)
3. Hodimlarni qurilmaga qo'shing (Employee No = employee_id)
4. ISAPI ni yoqing (Network -> Advanced Settings -> Integration Protocol)

## Muallif

Bu loyiha Claude AI yordamida yaratildi.
