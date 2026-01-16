# Database Schema - Hikvision Attendance System

## Umumiy Arxitektura

```
┌─────────────────────────────────────────────────────────────────┐
│                         CORE MODULE                              │
│  ┌──────────────┐         ┌──────────────┐                      │
│  │ Organization │◄────────│ Organization │                      │
│  │              │         │   Settings   │                      │
│  └──────┬───────┘         └──────────────┘                      │
│         │                                                        │
│         │ 1:N                                                    │
│         ▼                                                        │
│  ┌──────────────┐                                               │
│  │    Branch    │◄────┐ (self-reference)                       │
│  │   (Filial)   │─────┘ parent/children                        │
│  └──────┬───────┘                                               │
└─────────┼──────────────────────────────────────────────────────┘
          │
          │ 1:N
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      EMPLOYEES MODULE                            │
│  ┌──────────────┐                                               │
│  │  Department  │◄────┐ (self-reference)                       │
│  │   (Bo'lim)   │─────┘ parent/subdepartments                  │
│  └──────┬───────┘                                               │
│         │                                                        │
│         │ 1:N              ┌──────────────┐                     │
│         └─────────────────►│   Position   │                     │
│                            │  (Lavozim)   │                     │
│                            └──────┬───────┘                     │
│                                   │                              │
│                                   │ 1:N                          │
│  ┌────────────────────────────────▼───────┐                     │
│  │           Employee (Hodim)             │                     │
│  │  ┌──────────────────────────────────┐  │                     │
│  │  │ - personnel_number               │  │                     │
│  │  │ - first_name, last_name         │  │                     │
│  │  │ - branch (REQUIRED)             │  │◄─── Branch          │
│  │  │ - department (optional)         │  │                     │
│  │  │ - position (optional)           │  │                     │
│  │  │ - manager (self-FK)  ◄──────────┼──┼─┐ subordinates     │
│  │  │ - status, hire_date             │  │ │                  │
│  │  └──────────────────────────────────┘  │ │                  │
│  └────────────────────────────────────────┘ │                  │
│                    │                         │                  │
│                    │                         │                  │
│  ┌─────────────────┼─────────────────────────┼───────────────┐ │
│  │                 ▼                         │               │ │
│  │  ┌─────────────────────┐  ┌──────────────┴──────┐        │ │
│  │  │ EmployeeDocument    │  │   LeaveRequest      │        │ │
│  │  │ - passport, ID, etc │  │   - vacation, sick  │        │ │
│  │  └─────────────────────┘  └─────────────────────┘        │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
          │
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ATTENDANCE MODULE                             │
│                                                                  │
│  ┌──────────────────────────────────────┐                       │
│  │      AttendanceRecord                │                       │
│  │  ┌────────────────────────────────┐  │                       │
│  │  │ - employee (FK)                │  │                       │
│  │  │ - event_type (check_in/out)    │  │                       │
│  │  │ - timestamp                    │  │                       │
│  │  │ - device_id                    │  │◄──── HikvisionDevice │
│  │  │ - card_no, verify_mode         │  │                       │
│  │  │ - temperature, mask_status     │  │                       │
│  │  │ - confidence, raw_data         │  │                       │
│  │  │ - photo_snapshot               │  │                       │
│  │  └────────────────────────────────┘  │                       │
│  └──────────────────────────────────────┘                       │
│                    │                                             │
│                    │ Aggregate                                   │
│                    ▼                                             │
│  ┌──────────────────────────────────────┐                       │
│  │      DailyAttendance                 │                       │
│  │  ┌────────────────────────────────┐  │                       │
│  │  │ - employee (FK)                │  │                       │
│  │  │ - date                         │  │                       │
│  │  │ - check_in, check_out          │  │                       │
│  │  │ - late_minutes, overtime       │  │                       │
│  │  │ - status, work_hours           │  │                       │
│  │  │ - approved_by, approved_at     │  │◄──── User (approval) │
│  │  │ - notes                        │  │                       │
│  │  └────────────────────────────────┘  │                       │
│  └──────────────────────────────────────┘                       │
│                                                                  │
│  ┌──────────────────────────────────────┐                       │
│  │        WorkSchedule                  │                       │
│  │  ┌────────────────────────────────┐  │                       │
│  │  │ - name, code                   │  │                       │
│  │  │ - start_time, end_time         │  │                       │
│  │  │ - break_start, break_end       │  │                       │
│  │  │ - late_threshold_minutes       │  │                       │
│  │  │ - working_days (JSON)          │  │                       │
│  │  │ - is_default, is_active        │  │                       │
│  │  └────────────────────────────────┘  │                       │
│  └──────────────────────────────────────┘                       │
│                                                                  │
│  ┌──────────────────────────────────────┐                       │
│  │          Holiday                     │                       │
│  │  - name, date, holiday_type          │                       │
│  │  - is_recurring (annual)             │                       │
│  └──────────────────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
          │
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    HIKVISION MODULE                              │
│                                                                  │
│  ┌──────────────────────────────────────┐                       │
│  │      HikvisionDevice                 │                       │
│  │  ┌────────────────────────────────┐  │                       │
│  │  │ - branch (FK) ◄────────────────┼──┼──── Branch          │
│  │  │ - name, serial_number          │  │                       │
│  │  │ - ip_address, port             │  │                       │
│  │  │ - username, password           │  │                       │
│  │  │ - device_type, model           │  │                       │
│  │  │ - location, description        │  │                       │
│  │  │ - is_active, last_sync         │  │                       │
│  │  └────────────────────────────────┘  │                       │
│  └──────────────────────────────────────┘                       │
│                    │                                             │
│                    │ 1:N                                         │
│                    ▼                                             │
│  ┌──────────────────────────────────────┐                       │
│  │        DeviceCommand                 │                       │
│  │  - device (FK)                       │                       │
│  │  - command_type (sync, reboot, etc)  │                       │
│  │  - status, response                  │                       │
│  │  - executed_at, executed_by          │                       │
│  └──────────────────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
          │
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     ACCOUNTS MODULE                              │
│                                                                  │
│  ┌──────────────────────────────────────┐                       │
│  │              User                    │                       │
│  │  ┌────────────────────────────────┐  │                       │
│  │  │ - username, email, password    │  │                       │
│  │  │ - role (admin/hr/viewer)       │  │                       │
│  │  │ - phone, avatar                │  │                       │
│  │  │ - is_verified, last_activity   │  │                       │
│  │  │ - employee (1:1 FK) ◄──────────┼──┼──── Employee        │
│  │  └────────────────────────────────┘  │                       │
│  └──────────────┬───────────────────────┘                       │
│                 │                                                │
│                 │ 1:N                                            │
│                 ▼                                                │
│  ┌──────────────────────────────────────┐                       │
│  │         UserAccess                   │                       │
│  │  ┌────────────────────────────────┐  │                       │
│  │  │ - user (FK to User)            │  │                       │
│  │  │ - access_type (choice):        │  │                       │
│  │  │   * organization               │  │                       │
│  │  │   * branch                     │  │                       │
│  │  │   * department                 │  │                       │
│  │  │ - organization (FK, optional)  │  │◄──── Organization    │
│  │  │ - branch (FK, optional)        │  │◄──── Branch          │
│  │  │ - department (FK, optional)    │  │◄──── Department      │
│  │  │ - can_view, can_edit, delete   │  │                       │
│  │  │ - granted_by (FK to User)      │  │                       │
│  │  │ - granted_at, expires_at       │  │                       │
│  │  │ - is_active, notes             │  │                       │
│  │  └────────────────────────────────┘  │                       │
│  └──────────────────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

## Batafsil Model Diagrammalari

### 1. CORE MODULE

```
┌─────────────────────────────────────┐
│         Organization                │
├─────────────────────────────────────┤
│ PK  id                              │
│     name                            │
│     legal_name                      │
│ UK  code                            │
│ UK  inn                             │
│     logo                            │
│     description                     │
│     address, phone, email, website  │
│     founded_date                    │
│     industry (CHOICES)              │
│     employee_count                  │
│     is_active                       │
│     timezone, currency, language    │
│     created_at, updated_at          │
└─────────────────┬───────────────────┘
                  │ 1
                  │
                  │ N
┌─────────────────▼───────────────────┐
│            Branch                   │
├─────────────────────────────────────┤
│ PK  id                              │
│ FK  organization_id                 │
│ FK  parent_id (self)                │
│     name                            │
│     code (UK with org)              │
│     branch_type (CHOICES):          │
│       - head_office                 │
│       - regional_office             │
│       - branch, warehouse, factory  │
│     address, city, region, country  │
│     latitude, longitude             │
│     phone, email                    │
│     work_start_time, work_end_time  │
│     timezone                        │
│     is_active, is_head_office       │
│     established_date, description   │
│     created_at, updated_at          │
├─────────────────────────────────────┤
│ Properties:                         │
│  - full_address                     │
│  - employee_count                   │
│  - department_count                 │
│  - device_count                     │
│  - full_path (hierarchy)            │
├─────────────────────────────────────┤
│ Methods:                            │
│  - get_department_tree()            │
│  - get_children_recursive()         │
│  - get_all_employees(include_child) │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│      OrganizationSettings           │
├─────────────────────────────────────┤
│ PK  id                              │
│ FK  organization_id (1:1)           │
│     late_threshold_minutes          │
│     early_leave_threshold_minutes   │
│     overtime_calculation_enabled    │
│     half_day_threshold_hours        │
│     working_days (JSON)             │
│     auto_sync_interval_minutes      │
│     sync_history_days               │
│     notification_email              │
│     send_daily_report               │
│     send_late_notifications         │
│     allow_remote_work               │
│     require_photo_on_check          │
│     allow_manual_attendance         │
│     created_at, updated_at          │
└─────────────────────────────────────┘
```

### 2. EMPLOYEES MODULE

```
┌─────────────────────────────────────┐
│          Department                 │
├─────────────────────────────────────┤
│ PK  id                              │
│ FK  branch_id                       │
│ FK  parent_id (self)                │
│ FK  head_id (Employee)              │
│     name                            │
│     code (UK with branch)           │
│     description, email, phone       │
│     is_active                       │
│     created_at, updated_at          │
├─────────────────────────────────────┤
│ Properties:                         │
│  - employee_count                   │
│  - full_name (with branch)          │
├─────────────────────────────────────┤
│ Methods:                            │
│  - get_position_tree()              │
│  - get_subdepartments()             │
└─────────────────┬───────────────────┘
                  │ 1
                  │
                  │ N
┌─────────────────▼───────────────────┐
│           Position                  │
├─────────────────────────────────────┤
│ PK  id                              │
│ FK  department_id                   │
│     title                           │
│     code (UK with dept)             │
│     description                     │
│     level (1-10):                   │
│       1: Intern                     │
│       3: Junior                     │
│       5: Middle/Senior              │
│       7: Team Lead                  │
│       8: Head                       │
│       10: Director/CEO              │
│     is_active                       │
│     created_at, updated_at          │
└─────────────────┬───────────────────┘
                  │ 1
                  │
                  │ N
┌─────────────────▼───────────────────┐
│           Employee                  │
├─────────────────────────────────────┤
│ PK  id                              │
│ UK  personnel_number                │
│ FK  branch_id (REQUIRED)            │
│ FK  department_id (optional)        │
│ FK  position_id (optional)          │
│ FK  manager_id (self)               │
│     first_name, last_name           │
│     middle_name                     │
│     birth_date, gender              │
│ UK  email                           │
│     phone_primary, phone_secondary  │
│     address, city, country          │
│     hire_date                       │
│     contract_type (permanent/temp)  │
│     employment_type (full/part)     │
│     status (active/inactive/leave)  │
│     termination_date, reason        │
│     salary                          │
│ FK  work_schedule_id                │
│     bio, profile_photo              │
│     notes                           │
│     created_at, updated_at          │
├─────────────────────────────────────┤
│ Properties:                         │
│  - full_name                        │
│  - age                              │
│  - years_of_service                 │
│  - is_active                        │
├─────────────────────────────────────┤
│ Relations:                          │
│  - subordinates (reverse manager)   │
│  - attendance_records               │
│  - daily_attendance                 │
│  - documents                        │
│  - leave_requests                   │
│  - user_account (1:1 reverse)       │
└─────────────────┬───────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌──────────────────┐ ┌──────────────────┐
│ EmployeeDocument │ │  LeaveRequest    │
├──────────────────┤ ├──────────────────┤
│ PK  id           │ │ PK  id           │
│ FK  employee_id  │ │ FK  employee_id  │
│     doc_type:    │ │ FK  approved_by  │
│     - passport   │ │     leave_type:  │
│     - id_card    │ │     - annual     │
│     - diploma    │ │     - sick       │
│     - contract   │ │     - unpaid     │
│     - other      │ │     - maternity  │
│     number       │ │     start_date   │
│     issue_date   │ │     end_date     │
│     expiry_date  │ │     total_days   │
│     file         │ │     reason       │
│     notes        │ │     status       │
│     uploaded_at  │ │     approved_at  │
└──────────────────┘ │     notes        │
                     │     created_at   │
                     └──────────────────┘
```

### 3. ATTENDANCE MODULE

```
┌─────────────────────────────────────┐
│       AttendanceRecord              │
├─────────────────────────────────────┤
│ PK  id                              │
│ FK  employee_id                     │
│     event_type (CHOICES):           │
│       - check_in                    │
│       - check_out                   │
│     timestamp                       │
│     device_id                       │
│     card_no                         │
│     verify_mode (CHOICES):          │
│       - face                        │
│       - fingerprint                 │
│       - card                        │
│       - password                    │
│       - multi (face + card)         │
│     temperature (30-45°C)           │
│     mask_status:                    │
│       - unknown, on, off            │
│     confidence (0-100%)             │
│     raw_data (JSON)                 │
│     photo_snapshot (image)          │
│     created_at                      │
├─────────────────────────────────────┤
│ Indexes:                            │
│  - (employee, timestamp)            │
│  - device_id                        │
│  - event_type                       │
└─────────────────┬───────────────────┘
                  │
                  │ Aggregated to
                  ▼
┌─────────────────────────────────────┐
│        DailyAttendance              │
├─────────────────────────────────────┤
│ PK  id                              │
│ FK  employee_id                     │
│ UK  (employee, date)                │
│     date                            │
│     check_in                        │
│     check_out                       │
│     status (CHOICES):               │
│       - present                     │
│       - absent                      │
│       - late                        │
│       - half_day                    │
│       - on_leave                    │
│     work_hours (calculated)         │
│     late_minutes                    │
│     overtime_minutes                │
│     early_leave_minutes             │
│ FK  approved_by_id                  │
│     approved_at                     │
│     notes                           │
│     created_at, updated_at          │
├─────────────────────────────────────┤
│ Properties:                         │
│  - is_late                          │
│  - is_early_leave                   │
│  - has_overtime                     │
├─────────────────────────────────────┤
│ Methods:                            │
│  - calculate_work_hours()           │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│         WorkSchedule                │
├─────────────────────────────────────┤
│ PK  id                              │
│ UK  name                            │
│ UK  code                            │
│     start_time                      │
│     end_time                        │
│     late_threshold_minutes          │
│     early_leave_threshold_minutes   │
│     break_start                     │
│     break_end                       │
│     working_days (JSON):            │
│       [0,1,2,3,4] = Mon-Fri         │
│     is_default                      │
│     is_active                       │
│     created_at, updated_at          │
├─────────────────────────────────────┤
│ Properties:                         │
│  - total_work_hours                 │
│  - break_duration                   │
│  - working_days_display             │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│            Holiday                  │
├─────────────────────────────────────┤
│ PK  id                              │
│     name                            │
│     date                            │
│     holiday_type:                   │
│       - national                    │
│       - religious                   │
│       - organizational              │
│     description                     │
│     is_recurring (annual)           │
│     created_at, updated_at          │
└─────────────────────────────────────┘
```

### 4. HIKVISION MODULE

```
┌─────────────────────────────────────┐
│        HikvisionDevice              │
├─────────────────────────────────────┤
│ PK  id                              │
│ FK  branch_id                       │
│ UK  serial_number                   │
│     name                            │
│     ip_address                      │
│     port (default: 80)              │
│     username, password              │
│     device_type (CHOICES):          │
│       - access_control              │
│       - time_attendance             │
│       - face_recognition            │
│     model                           │
│     firmware_version                │
│     location                        │
│     description                     │
│     is_active                       │
│     last_sync_time                  │
│     sync_status                     │
│     created_at, updated_at          │
├─────────────────────────────────────┤
│ Properties:                         │
│  - organization (via branch)        │
│  - is_online                        │
│  - full_location                    │
├─────────────────────────────────────┤
│ Methods:                            │
│  - test_connection()                │
│  - sync_attendance()                │
│  - get_device_info()                │
└─────────────────┬───────────────────┘
                  │ 1
                  │
                  │ N
┌─────────────────▼───────────────────┐
│         DeviceCommand               │
├─────────────────────────────────────┤
│ PK  id                              │
│ FK  device_id                       │
│ FK  executed_by_id                  │
│     command_type (CHOICES):         │
│       - sync_attendance             │
│       - sync_employees              │
│       - reboot_device               │
│       - clear_logs                  │
│       - get_status                  │
│     status (pending/success/failed) │
│     response (JSON)                 │
│     error_message                   │
│     executed_at                     │
│     completed_at                    │
│     created_at                      │
└─────────────────────────────────────┘
```

### 5. ACCOUNTS MODULE (Access Control)

```
┌─────────────────────────────────────┐
│              User                   │
│         (AbstractUser)              │
├─────────────────────────────────────┤
│ PK  id                              │
│ UK  username                        │
│ UK  email                           │
│     password (hashed)               │
│     first_name, last_name           │
│     role (CHOICES):                 │
│       - admin (full access)         │
│       - hr (manage employees)       │
│       - viewer (read-only)          │
│     phone                           │
│     avatar (image)                  │
│     is_verified                     │
│     last_activity                   │
│ FK  employee_id (1:1, optional)     │
│     is_active, is_staff             │
│     date_joined                     │
├─────────────────────────────────────┤
│ Properties:                         │
│  - is_admin                         │
│  - is_hr                            │
│  - full_name                        │
├─────────────────────────────────────┤
│ Access Control Methods:             │
│  - get_accessible_organizations()   │
│  - get_accessible_branches()        │
│  - get_accessible_departments()     │
│  - get_accessible_employees()       │
│  - has_access_to_employee(emp)      │
│  - has_access_to_branch(branch)     │
│  - has_access_to_department(dept)   │
│  - has_permission(perm)             │
└─────────────────┬───────────────────┘
                  │ 1
                  │
                  │ N
┌─────────────────▼───────────────────┐
│          UserAccess                 │
│      (Access Control Rules)         │
├─────────────────────────────────────┤
│ PK  id                              │
│ FK  user_id                         │
│     access_type (CHOICES):          │
│       - organization (all branches) │
│       - branch (all departments)    │
│       - department (only that dept) │
│ FK  organization_id (nullable)      │
│ FK  branch_id (nullable)            │
│ FK  department_id (nullable)        │
│     can_view (default: true)        │
│     can_edit (default: false)       │
│     can_delete (default: false)     │
│ FK  granted_by_id (User)            │
│     granted_at                      │
│     expires_at (nullable)           │
│     is_active                       │
│     notes                           │
├─────────────────────────────────────┤
│ Constraints:                        │
│  - UK(user, organization) if org    │
│  - UK(user, branch) if branch       │
│  - UK(user, department) if dept     │
├─────────────────────────────────────┤
│ Validation:                         │
│  - Only ONE of (org/branch/dept)    │
│  - access_type must match FK        │
│  - Exactly one FK must be filled    │
├─────────────────────────────────────┤
│ Properties:                         │
│  - is_expired                       │
│  - permissions_summary              │
├─────────────────────────────────────┤
│ Methods:                            │
│  - get_target_display()             │
└─────────────────────────────────────┘
```

## Access Control Logic Flow

```
┌─────────────────────────────────────────────────────────┐
│           user.get_accessible_employees()               │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  Is Admin?     │
         └────┬───────┬───┘
              │ YES   │ NO
              ▼       ▼
    ┌─────────────┐  ┌──────────────────────────────┐
    │ Return ALL  │  │  Build employee_ids set      │
    │ Employees   │  └──────────┬───────────────────┘
    └─────────────┘             │
                                ▼
                  ┌─────────────────────────────┐
                  │ Has user.employee?          │
                  └────┬───────────────┬────────┘
                       │ YES           │ NO
                       ▼               ▼
         ┌──────────────────────┐     │
         │ Add self to set      │     │
         │ Get all subordinates │     │
         │ (RECURSIVE)          │     │
         └──────────┬───────────┘     │
                    │                 │
                    └────────┬────────┘
                             ▼
              ┌──────────────────────────────┐
              │ Get UserAccess permissions   │
              └──────────┬───────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│Organization  │ │   Branch     │ │  Department  │
│  Access?     │ │   Access?    │ │   Access?    │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       ▼                ▼                ▼
  All branches    All employees    Dept employees
  → employees     in branch(es)    only
       │                │                │
       └────────────────┼────────────────┘
                        ▼
              ┌──────────────────┐
              │ Combine all sets │
              │ Return QuerySet  │
              └──────────────────┘
```

## Ierarxiya Misoli

```
Organization: "Mega Holding"
│
├── Branch: "Toshkent Bosh Ofis" (HQ)
│   ├── Department: "IT"
│   │   ├── Position: "CTO" (level 10)
│   │   │   └── Employee: "Ali Valiyev" (manager)
│   │   ├── Position: "Senior Developer" (level 5)
│   │   │   ├── Employee: "Vali Aliyev"
│   │   │   └── Employee: "Olim Karimov"
│   │   └── Position: "Junior Developer" (level 3)
│   │       └── Employee: "Aziz Rahimov"
│   │
│   └── Department: "HR"
│       ├── Position: "HR Director" (level 8)
│       │   └── Employee: "Malika Yusupova" (manager)
│       └── Position: "HR Specialist" (level 4)
│           └── Employee: "Dilnoza Karimova"
│
└── Branch: "Samarqand Filial"
    └── Department: "Sales"
        ├── Position: "Sales Manager" (level 7)
        │   └── Employee: "Bobur Saidov" (manager)
        └── Position: "Sales Agent" (level 3)
            ├── Employee: "Nodira Azimova"
            └── Employee: "Shohruh Tursunov"
```

## Access Control Misollari

### Misol 1: Filial Rahbari
```
User: ali_manager (role: hr)
Employee: Ali Valiyev (IT Department Head)
UserAccess:
  - type: branch
  - branch: Toshkent Bosh Ofis
  - can_view: true
  - can_edit: true

Ko'radi:
  ✅ O'zini (Ali Valiyev)
  ✅ Qo'l ostidagilar: Vali, Olim, Aziz (IT dept)
  ✅ Butun Toshkent filialdagi barcha hodimlar (UserAccess orqali)
  ❌ Samarqand filiali hodimlarini ko'rmaydi
```

### Misol 2: Bo'lim Ko'ruvchisi
```
User: viewer1 (role: viewer)
UserAccess:
  - type: department
  - department: HR
  - can_view: true
  - can_edit: false

Ko'radi:
  ✅ Malika Yusupova
  ✅ Dilnoza Karimova
  ❌ IT departament hodimlarini ko'rmaydi
  ❌ Boshqa filiallarni ko'rmaydi
```

### Misol 3: Super HR
```
User: super_hr (role: hr)
UserAccess:
  - type: organization
  - organization: Mega Holding
  - can_view: true
  - can_edit: true
  - can_delete: false

Ko'radi:
  ✅ Barcha filiallar
  ✅ Barcha bo'limlar
  ✅ Barcha hodimlar
  ✅ Tahrirlash mumkin
  ❌ O'chira olmaydi
```

## Database Indexlar va Performance

### Asosiy Indexlar:

1. **Organization**: code, is_active
2. **Branch**: (organization, code), is_active, branch_type, city
3. **Department**: (branch, code), is_active
4. **Employee**: personnel_number, email, (branch, status), (department, status)
5. **AttendanceRecord**: (employee, timestamp), device_id, event_type
6. **DailyAttendance**: (employee, date) UNIQUE
7. **User**: role, is_active
8. **UserAccess**: (user, access_type), is_active, expires_at

### Unique Constraints:

1. Organization.code
2. Organization.inn
3. (Branch.organization, Branch.code)
4. (Department.branch, Department.code)
5. Employee.personnel_number
6. Employee.email
7. (DailyAttendance.employee, DailyAttendance.date)
8. HikvisionDevice.serial_number
9. User.username
10. User.email
11. (UserAccess.user, UserAccess.organization) WHERE organization IS NOT NULL
12. (UserAccess.user, UserAccess.branch) WHERE branch IS NOT NULL
13. (UserAccess.user, UserAccess.department) WHERE department IS NOT NULL
