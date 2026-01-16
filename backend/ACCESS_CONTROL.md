# Access Control Tizimi

Bu loyihada role-based access control (RBAC) va hierarchical access control tizimi joriy qilingan.

## Asosiy Konsepsiyalar

### 1. User Rollari

Har bir foydalanuvchi quyidagi rollardan biriga ega:

- **ADMIN**: Tizimda to'liq huquqlarga ega. Barcha tashkilot, filial, bo'lim va hodimlarni ko'rishi va boshqarishi mumkin.
- **HR**: HR menejeri - hodimlar va davomat bilan ishlash huquqi bor. Faqat o'ziga berilgan dostup doirasida ishlaydi.
- **VIEWER**: Ko'ruvchi - faqat o'qish huquqi. UserAccess orqali belgilangan resurslarga dostup.

### 2. Access Control Ierarxiyasi

```
Organization (Tashkilot)
    ├── Branch (Filial)
    │   └── Department (Bo'lim)
    │       └── Employee (Hodim)
    └── Branch
        └── Department
            └── Employee
```

### 3. UserAccess Modeli

`UserAccess` modeli orqali foydalanuvchilarga granular dostup beriladi:

**Access Turlari:**
- `organization`: Butun tashkilotga dostup (barcha filial va hodimlar)
- `branch`: Ma'lum filialga dostup (filial va uning barcha bo'lim/hodimlar)
- `department`: Ma'lum bo'limga dostup (faqat shu bo'limdagi hodimlar)

**Huquqlar:**
- `can_view`: Ko'rish huquqi
- `can_edit`: Tahrirlash huquqi
- `can_delete`: O'chirish huquqi

## Foydalanish

### 1. Hodim-Rahbar Ierarxiyasi

Agar foydalanuvchi hodim bo'lsa va boshqa hodimlarning rahbari bo'lsa, u avtomatik ravishda o'z qo'l ostidagi barcha hodimlarni ko'radi (rekursiv).

**Misol:**
```python
# User yaratish va hodimga bog'lash
user = User.objects.create_user(
    username='ali_manager',
    email='ali@company.uz',
    password='secure_password',
    role='viewer'
)

# Hodim yaratish
manager_employee = Employee.objects.get(id=5)
user.employee = manager_employee
user.save()

# Endi bu user o'z qo'l ostidagi barcha hodimlarni ko'radi
accessible_employees = user.get_accessible_employees()
# Bu yerda manager_employee ning barcha subordinates qaytadi
```

### 2. Filialga Dostup Berish

**Admin panel orqali:**
1. Users -> UserAccess -> Add UserAccess
2. User: Dostup beriladigan foydalanuvchi
3. Access type: "branch"
4. Branch: Tanlash
5. Huquqlarni belgilash (can_view, can_edit, can_delete)

**Kod orqali:**
```python
from apps.accounts.models import User, UserAccess
from apps.core.models import Branch

hr_user = User.objects.get(username='hr_tashkent')
tashkent_branch = Branch.objects.get(code='TSH-01')

UserAccess.objects.create(
    user=hr_user,
    access_type='branch',
    branch=tashkent_branch,
    can_view=True,
    can_edit=True,
    can_delete=False,
    granted_by=request.user  # Admin user
)

# Endi hr_user Toshkent filialidagi barcha hodimlarni ko'radi
employees = hr_user.get_accessible_employees()
```

### 3. Bo'limga Dostup Berish

```python
from apps.accounts.models import User, UserAccess
from apps.employees.models import Department

viewer = User.objects.get(username='it_viewer')
it_dept = Department.objects.get(code='IT')

UserAccess.objects.create(
    user=viewer,
    access_type='department',
    department=it_dept,
    can_view=True,
    granted_by=admin_user
)

# Endi viewer faqat IT bo'limidagi hodimlarni ko'radi
employees = viewer.get_accessible_employees()
```

### 4. Butun Tashkilotga Dostup

```python
from apps.accounts.models import User, UserAccess
from apps.core.models import Organization

super_hr = User.objects.get(username='super_hr')
mega_org = Organization.objects.get(code='MEGA')

UserAccess.objects.create(
    user=super_hr,
    access_type='organization',
    organization=mega_org,
    can_view=True,
    can_edit=True,
    granted_by=admin_user
)

# Endi super_hr butun tashkilotdagi barcha hodimlarni ko'radi
employees = super_hr.get_accessible_employees()
```

### 5. Vaqtinchalik Dostup

```python
from datetime import datetime, timedelta

# 30 kunlik dostup berish
UserAccess.objects.create(
    user=temp_user,
    access_type='branch',
    branch=branch,
    can_view=True,
    expires_at=datetime.now() + timedelta(days=30),
    granted_by=admin_user,
    notes="Vaqtinchalik audit uchun dostup"
)
```

## API Metodlari

### User Model Metodlari

#### get_accessible_organizations()
```python
user.get_accessible_organizations()
# Returns: QuerySet[Organization]
# Foydalanuvchi dostup qila oladigan tashkilotlar
```

#### get_accessible_branches()
```python
user.get_accessible_branches()
# Returns: QuerySet[Branch]
# Foydalanuvchi dostup qila oladigan filiallar
```

#### get_accessible_departments()
```python
user.get_accessible_departments()
# Returns: QuerySet[Department]
# Foydalanuvchi dostup qila oladigan bo'limlar
```

#### get_accessible_employees()
```python
user.get_accessible_employees()
# Returns: QuerySet[Employee]
# Foydalanuvchi ko'ra oladigan barcha hodimlar
# Quyidagilarni o'z ichiga oladi:
# 1. Admin bo'lsa - barcha hodimlar
# 2. Employee bo'lsa - o'zi + o'z qo'l ostidagilar (rekursiv)
# 3. UserAccess orqali berilgan dostuplar
```

#### has_access_to_employee(employee)
```python
if user.has_access_to_employee(some_employee):
    # Dostup bor
    print(some_employee.full_name)
else:
    # Dostup yo'q
    raise PermissionDenied()
```

#### has_access_to_branch(branch)
```python
if user.has_access_to_branch(branch):
    # Filialga dostup bor
    pass
```

#### has_access_to_department(department)
```python
if user.has_access_to_department(dept):
    # Bo'limga dostup bor
    pass
```

## Django REST Framework Integration

ViewSet yoki APIView da foydalanish:

```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class EmployeeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Faqat dostup berilgan hodimlarni qaytarish"""
        user = self.request.user
        return user.get_accessible_employees()

class BranchViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Faqat dostup berilgan filiallarni qaytarish"""
        user = self.request.user
        return user.get_accessible_branches()
```

## Custom Permission Class

```python
from rest_framework import permissions

class HasEmployeeAccess(permissions.BasePermission):
    """
    Foydalanuvchi hodimga dostup borligini tekshiradi.
    """

    def has_object_permission(self, request, view, obj):
        # obj - Employee instance
        return request.user.has_access_to_employee(obj)

# Ishlatish
class EmployeeDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, HasEmployeeAccess]
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
```

## Misollar

### Misol 1: Filial Rahbari
```python
# Toshkent filiali rahbariga to'liq dostup
branch_manager = User.objects.create_user(
    username='ali_tashkent',
    role='hr'
)

tashkent = Branch.objects.get(code='TSH-01')

UserAccess.objects.create(
    user=branch_manager,
    access_type='branch',
    branch=tashkent,
    can_view=True,
    can_edit=True,
    can_delete=True,
    granted_by=admin
)

# Ali endi Toshkent filialidagi barcha hodimlarni boshqarishi mumkin
```

### Misol 2: Bo'lim Rahbari
```python
# IT bo'limi rahbariga o'z bo'limi ustidan nazorat
it_head = Employee.objects.get(personnel_number='EMP001')
it_head_user = User.objects.create_user(
    username='it_head',
    role='hr'
)
it_head_user.employee = it_head
it_head_user.save()

# IT bo'limiga dostup
it_dept = Department.objects.get(code='IT')
UserAccess.objects.create(
    user=it_head_user,
    access_type='department',
    department=it_dept,
    can_view=True,
    can_edit=True,
    granted_by=admin
)

# IT rahbari:
# 1. O'zining qo'l ostidagi hodimlarni ko'radi (employee.subordinates orqali)
# 2. Butun IT bo'limini ko'radi (UserAccess orqali)
```

### Misol 3: Viewer Foydalanuvchi
```python
# Faqat ko'rish huquqi
viewer = User.objects.create_user(
    username='viewer1',
    role='viewer'
)

# Bir nechta bo'limga faqat ko'rish huquqi
for dept_code in ['IT', 'HR', 'FINANCE']:
    dept = Department.objects.get(code=dept_code)
    UserAccess.objects.create(
        user=viewer,
        access_type='department',
        department=dept,
        can_view=True,
        can_edit=False,
        can_delete=False,
        granted_by=admin
    )

# Viewer faqat IT, HR va FINANCE bo'limlaridagi hodimlarni ko'radi
```

## Xavfsizlik

1. **Validatsiya**: UserAccess modelida `clean()` metodi orqali validatsiya amalga oshiriladi
2. **Rekursiv Dostup**: Rahbarlar o'z qo'l ostidagilarni rekursiv ko'radi
3. **Ierarxik Dostup**: Tashkilotga dostup bo'lsa, uning barcha filial va bo'limlari ko'rinadi
4. **Vaqtinchalik Dostup**: `expires_at` orqali vaqtinchalik dostup berish mumkin
5. **Audit Trail**: `granted_by` va `granted_at` orqali kim va qachon dostup berganini bilish mumkin

## Database Schema

```sql
-- UserAccess jadvali
CREATE TABLE accounts_useraccess (
    id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES accounts_user,
    access_type VARCHAR(20),
    organization_id BIGINT REFERENCES core_organization NULL,
    branch_id BIGINT REFERENCES core_branch NULL,
    department_id BIGINT REFERENCES employees_department NULL,
    can_view BOOLEAN DEFAULT TRUE,
    can_edit BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    granted_by_id BIGINT REFERENCES accounts_user NULL,
    granted_at TIMESTAMP,
    expires_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT NULL
);

-- User model ga qo'shimcha
ALTER TABLE accounts_user ADD COLUMN employee_id BIGINT REFERENCES employees_employee NULL;
```

## Migratsiya

```bash
cd backend
python manage.py migrate accounts
```

## Testlar

```python
from django.test import TestCase
from apps.accounts.models import User, UserAccess
from apps.core.models import Organization, Branch
from apps.employees.models import Department, Employee

class AccessControlTestCase(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Test Org", code="TEST")
        self.branch = Branch.objects.create(
            organization=self.org,
            name="Test Branch",
            code="TB1"
        )
        self.user = User.objects.create_user(username="test", role="viewer")

    def test_branch_access(self):
        """Filialga dostup tekshirish"""
        UserAccess.objects.create(
            user=self.user,
            access_type='branch',
            branch=self.branch,
            can_view=True
        )

        self.assertTrue(self.user.has_access_to_branch(self.branch))
        accessible = self.user.get_accessible_branches()
        self.assertIn(self.branch, accessible)
```
