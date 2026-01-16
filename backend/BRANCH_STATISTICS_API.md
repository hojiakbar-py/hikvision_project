# Branch Statistics API Documentation

Filiallar uchun davomat statistikasini olish API dokumentatsiyasi.

## Base URL

```
/api/branches/
```

## Authentication

Barcha endpointlar autentifikatsiya talab qiladi. Request header ga token qo'shish kerak:

```
Authorization: Bearer <your_token>
```

## Endpoints

### 1. Kunlik Davomat Statistikasi

**GET** `/api/branches/{branch_id}/attendance_stats/`

Filial uchun kunlik davomat statistikasini olish.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| date | string | No | today | YYYY-MM-DD formatda sana |
| include_children | boolean | No | false | Pastki filiallar ham qo'shilsinmi |

#### Request Example

```bash
GET /api/branches/1/attendance_stats/?date=2024-01-15&include_children=false
```

#### Response Example

```json
{
  "date": "2024-01-15",
  "total_employees": 50,
  "present": 45,
  "absent": 3,
  "late": 8,
  "half_day": 1,
  "on_leave": 2,
  "present_percentage": 90.0,
  "late_percentage": 16.0
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| date | string | Statistika sanasi |
| total_employees | integer | Jami faol hodimlar soni |
| present | integer | Kelgan hodimlar |
| absent | integer | Kelmaganlar |
| late | integer | Kechikkanlar |
| half_day | integer | Yarim kun ishlaganlar |
| on_leave | integer | Ta'tilda olanlar |
| present_percentage | float | Kelish foizi |
| late_percentage | float | Kechikish foizi |

---

### 2. Davr Bo'yicha Xulosa

**GET** `/api/branches/{branch_id}/attendance_summary/`

Ma'lum davr uchun umumiy davomat xulosasi.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| start_date | string | **Yes** | - | Boshlanish sanasi (YYYY-MM-DD) |
| end_date | string | **Yes** | - | Tugash sanasi (YYYY-MM-DD) |
| include_children | boolean | No | false | Pastki filiallar ham qo'shilsinmi |

#### Request Example

```bash
GET /api/branches/1/attendance_summary/?start_date=2024-01-01&end_date=2024-01-31
```

#### Response Example

```json
{
  "period": {
    "start": "2024-01-01",
    "end": "2024-01-31",
    "days": 31
  },
  "total_employees": 50,
  "total_records": 1100,
  "total_late_minutes": 2340,
  "total_overtime_minutes": 1200,
  "average_work_hours": 8.5,
  "present_count": 1000,
  "late_count": 150,
  "absent_count": 50,
  "average_present_per_day": 45.45,
  "average_late_per_day": 6.82,
  "average_absent_per_day": 2.27
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| period.start | string | Davr boshlanishi |
| period.end | string | Davr tugashi |
| period.days | integer | Kunlar soni |
| total_employees | integer | Jami hodimlar |
| total_records | integer | Jami davomat yozuvlari |
| total_late_minutes | integer | Jami kechikish daqiqalari |
| total_overtime_minutes | integer | Jami overtime daqiqalari |
| average_work_hours | float | O'rtacha ish soatlari |
| present_count | integer | Kelganlar soni |
| late_count | integer | Kechikkanlar soni |
| absent_count | integer | Kelmaganlar soni |
| average_present_per_day | float | Kuniga o'rtacha kelganlar |
| average_late_per_day | float | Kuniga o'rtacha kechikkanlar |
| average_absent_per_day | float | Kuniga o'rtacha kelmaganlar |

---

### 3. Bo'limlar Bo'yicha Taqsimot

**GET** `/api/branches/{branch_id}/department_breakdown/`

Har bir bo'lim uchun alohida davomat statistikasi.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| date | string | No | today | YYYY-MM-DD formatda sana |

#### Request Example

```bash
GET /api/branches/1/department_breakdown/?date=2024-01-15
```

#### Response Example

```json
[
  {
    "department_id": 1,
    "department_name": "IT Bo'limi",
    "department_code": "IT",
    "total_employees": 15,
    "present": 14,
    "late": 3,
    "absent": 1,
    "half_day": 0,
    "on_leave": 0,
    "present_percentage": 93.33
  },
  {
    "department_id": 2,
    "department_name": "HR Bo'limi",
    "department_code": "HR",
    "total_employees": 8,
    "present": 7,
    "late": 1,
    "absent": 1,
    "half_day": 0,
    "on_leave": 0,
    "present_percentage": 87.5
  }
]
```

#### Response Fields (Array)

| Field | Type | Description |
|-------|------|-------------|
| department_id | integer | Bo'lim ID |
| department_name | string | Bo'lim nomi |
| department_code | string | Bo'lim kodi |
| total_employees | integer | Bo'limdagi jami hodimlar |
| present | integer | Kelganlar |
| late | integer | Kechikkanlar |
| absent | integer | Kelmaganlar |
| half_day | integer | Yarim kun |
| on_leave | integer | Ta'tilda |
| present_percentage | float | Kelish foizi |

---

### 4. Eng Ko'p Kechikkanlar

**GET** `/api/branches/{branch_id}/top_latecomers/`

Ma'lum davrda eng ko'p kechikkan hodimlar ro'yxati.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| start_date | string | **Yes** | - | Boshlanish sanasi (YYYY-MM-DD) |
| end_date | string | **Yes** | - | Tugash sanasi (YYYY-MM-DD) |
| limit | integer | No | 10 | Nechta hodim qaytarish |

#### Request Example

```bash
GET /api/branches/1/top_latecomers/?start_date=2024-01-01&end_date=2024-01-31&limit=5
```

#### Response Example

```json
[
  {
    "employee_id": 5,
    "personnel_number": "EMP001",
    "employee_name": "Ali Valiyev",
    "department": "IT Bo'limi",
    "late_count": 12,
    "total_late_minutes": 180,
    "average_late_minutes": 15.0
  },
  {
    "employee_id": 12,
    "personnel_number": "EMP008",
    "employee_name": "Vali Aliyev",
    "department": "HR Bo'limi",
    "late_count": 8,
    "total_late_minutes": 96,
    "average_late_minutes": 12.0
  }
]
```

#### Response Fields (Array)

| Field | Type | Description |
|-------|------|-------------|
| employee_id | integer | Hodim ID |
| personnel_number | string | Hodim raqami |
| employee_name | string | Hodim FIO |
| department | string | Bo'lim nomi |
| late_count | integer | Kechikishlar soni |
| total_late_minutes | integer | Jami kechikish daqiqalari |
| average_late_minutes | float | O'rtacha kechikish (daqiqa) |

---

## Access Control

API access control tizimi orqali faqat dostup berilgan filiallarga murojaat qilish mumkin:

### Admin
Barcha filiallarga dostup:
```python
user.role == 'admin'  # Barcha filiallar
```

### HR / Viewer
UserAccess orqali berilgan filiallarga dostup:
```python
# Misol: Toshkent filialiga dostup
UserAccess.objects.create(
    user=hr_user,
    access_type='branch',
    branch=tashkent_branch,
    can_view=True
)
```

### Manager (Employee)
Agar user hodim bo'lsa va employee bog'langan bo'lsa, o'z filialiga dostup:
```python
user.employee.branch  # Faqat o'z filialni ko'radi
```

---

## Error Responses

### 400 Bad Request

Noto'g'ri parametrlar berilgan bo'lsa:

```json
{
  "error": "Invalid date format. Use YYYY-MM-DD"
}
```

yoki

```json
{
  "error": "Both start_date and end_date are required"
}
```

### 401 Unauthorized

Token berilmagan yoki noto'g'ri bo'lsa:

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden

Filialga dostup yo'q bo'lsa:

```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found

Filial topilmagan bo'lsa:

```json
{
  "detail": "Not found."
}
```

---

## Usage Examples

### Python (requests)

```python
import requests
from datetime import date, timedelta

# Token olish
token = "your_access_token_here"
headers = {"Authorization": f"Bearer {token}"}

# Bugungi statistika
response = requests.get(
    "http://api.example.com/api/branches/1/attendance_stats/",
    headers=headers
)
stats = response.json()
print(f"Bugun {stats['present']} hodim keldi")

# Oylik xulosa
today = date.today()
start_of_month = today.replace(day=1)

response = requests.get(
    "http://api.example.com/api/branches/1/attendance_summary/",
    headers=headers,
    params={
        "start_date": str(start_of_month),
        "end_date": str(today)
    }
)
summary = response.json()
print(f"Bu oy: {summary['present_count']} kelgan, {summary['late_count']} kechikkan")
```

### JavaScript (fetch)

```javascript
const token = "your_access_token_here";
const headers = {
  "Authorization": `Bearer ${token}`,
  "Content-Type": "application/json"
};

// Bugungi statistika
fetch("/api/branches/1/attendance_stats/", { headers })
  .then(res => res.json())
  .then(stats => {
    console.log(`Bugun ${stats.present} hodim keldi`);
    console.log(`Kelish foizi: ${stats.present_percentage}%`);
  });

// Bo'limlar bo'yicha
fetch("/api/branches/1/department_breakdown/", { headers })
  .then(res => res.json())
  .then(breakdown => {
    breakdown.forEach(dept => {
      console.log(`${dept.department_name}: ${dept.present}/${dept.total_employees}`);
    });
  });
```

### cURL

```bash
# Kunlik statistika
curl -H "Authorization: Bearer your_token" \
  "http://api.example.com/api/branches/1/attendance_stats/?date=2024-01-15"

# Oylik xulosa
curl -H "Authorization: Bearer your_token" \
  "http://api.example.com/api/branches/1/attendance_summary/?start_date=2024-01-01&end_date=2024-01-31"

# Eng ko'p kechikkanlar
curl -H "Authorization: Bearer your_token" \
  "http://api.example.com/api/branches/1/top_latecomers/?start_date=2024-01-01&end_date=2024-01-31&limit=10"
```

---

## Frontend Integration Example

### React Component

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function BranchStatistics({ branchId }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(
          `/api/branches/${branchId}/attendance_stats/`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          }
        );
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [branchId]);

  if (loading) return <div>Loading...</div>;
  if (!stats) return <div>No data</div>;

  return (
    <div className="branch-statistics">
      <h2>Bugungi Statistika</h2>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>{stats.total_employees}</h3>
          <p>Jami Hodimlar</p>
        </div>
        <div className="stat-card success">
          <h3>{stats.present}</h3>
          <p>Kelganlar ({stats.present_percentage}%)</p>
        </div>
        <div className="stat-card warning">
          <h3>{stats.late}</h3>
          <p>Kechikkanlar ({stats.late_percentage}%)</p>
        </div>
        <div className="stat-card danger">
          <h3>{stats.absent}</h3>
          <p>Kelmaganlar</p>
        </div>
      </div>
    </div>
  );
}

export default BranchStatistics;
```

### Vue.js Component

```vue
<template>
  <div class="branch-statistics">
    <h2>Filial Statistikasi</h2>
    <div v-if="loading">Yuklanmoqda...</div>
    <div v-else-if="stats" class="stats-grid">
      <div class="stat-card">
        <h3>{{ stats.total_employees }}</h3>
        <p>Jami Hodimlar</p>
      </div>
      <div class="stat-card success">
        <h3>{{ stats.present }}</h3>
        <p>Kelganlar ({{ stats.present_percentage }}%)</p>
      </div>
      <div class="stat-card warning">
        <h3>{{ stats.late }}</h3>
        <p>Kechikkanlar</p>
      </div>
      <div class="stat-card danger">
        <h3>{{ stats.absent }}</h3>
        <p>Kelmaganlar</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: ['branchId'],
  data() {
    return {
      stats: null,
      loading: true
    };
  },
  mounted() {
    this.fetchStats();
  },
  methods: {
    async fetchStats() {
      try {
        const response = await axios.get(
          `/api/branches/${this.branchId}/attendance_stats/`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          }
        );
        this.stats = response.data;
      } catch (error) {
        console.error('Error:', error);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

---

## Dashboard Example Structure

### Recommended Dashboard Layout

```
┌─────────────────────────────────────────────────────┐
│  Filial: Toshkent Bosh Ofis      Sana: 2024-01-15  │
├─────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │   50     │  │   45     │  │    8     │          │
│  │  Jami    │  │ Kelgan   │  │ Kechik.  │          │
│  └──────────┘  └──────────┘  └──────────┘          │
├─────────────────────────────────────────────────────┤
│  Bo'limlar Bo'yicha:                                │
│  ┌───────────────────────────────────────────────┐  │
│  │  IT Bo'limi:      14/15  (93%)    [Progress] │  │
│  │  HR Bo'limi:       7/8   (87%)    [Progress] │  │
│  │  Sales:           20/22  (91%)    [Progress] │  │
│  └───────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│  Eng Ko'p Kechikkanlar (Bu Oy):                     │
│  1. Ali Valiyev      - 12 marta  (avg: 15 min)     │
│  2. Vali Aliyev      - 8 marta   (avg: 12 min)     │
│  3. Olim Karimov     - 6 marta   (avg: 10 min)     │
└─────────────────────────────────────────────────────┘
```

---

## Notes

1. Barcha sanalar **YYYY-MM-DD** formatda bo'lishi kerak
2. Foizlar 2 ta raqamgacha yaxlitlanadi
3. `include_children=true` parametri pastki filiallarni ham qo'shadi
4. Access control UserAccess modeliga asoslanadi
5. Barcha vaqtlar server timezone ga muvofiq qaytariladi
