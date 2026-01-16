"""Admin configuration for employees app."""

from django.contrib import admin
from .models import Department, Position, Employee


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'department']
    list_filter = ['department']
    search_fields = ['name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'department', 'position', 'status', 'hire_date']
    list_filter = ['department', 'position', 'status']
    search_fields = ['first_name', 'last_name', 'employee_id', 'phone']
    date_hierarchy = 'hire_date'
