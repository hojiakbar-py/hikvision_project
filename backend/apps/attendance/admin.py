"""Admin configuration for attendance app."""

from django.contrib import admin
from .models import AttendanceRecord, DailyAttendance, WorkSchedule


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['employee', 'event_type', 'timestamp', 'device_id']
    list_filter = ['event_type', 'timestamp']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    date_hierarchy = 'timestamp'


@admin.register(DailyAttendance)
class DailyAttendanceAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'date', 'first_check_in', 'last_check_out',
        'late_minutes', 'early_leave_minutes', 'status'
    ]
    list_filter = ['status', 'date']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    date_hierarchy = 'date'


@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'is_default']
    list_filter = ['is_default']
