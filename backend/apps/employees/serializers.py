"""Serializers for employees app."""

from rest_framework import serializers
from django.utils import timezone
from django.db.models import Sum
from .models import Department, Position, Employee


class DepartmentSerializer(serializers.ModelSerializer):
    """Department serializer."""

    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'employee_count', 'created_at']

    def get_employee_count(self, obj):
        return obj.employees.filter(status='active').count()


class PositionSerializer(serializers.ModelSerializer):
    """Position serializer."""

    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Position
        fields = ['id', 'name', 'department', 'department_name']


class EmployeeListSerializer(serializers.ModelSerializer):
    """Employee list serializer (qisqacha)."""

    department_name = serializers.CharField(source='department.name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    full_name = serializers.CharField(read_only=True)
    today_check_in = serializers.SerializerMethodField()
    today_check_out = serializers.SerializerMethodField()
    today_status = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'full_name', 'first_name', 'last_name',
            'department', 'department_name', 'position', 'position_name',
            'status', 'phone', 'photo', 'work_start_time', 'work_end_time',
            'today_check_in', 'today_check_out', 'today_status'
        ]

    def get_today_check_in(self, obj):
        from apps.attendance.models import DailyAttendance
        today = timezone.now().date()
        daily = DailyAttendance.objects.filter(employee=obj, date=today).first()
        if daily and daily.first_check_in:
            return daily.first_check_in.strftime('%H:%M')
        return None

    def get_today_check_out(self, obj):
        from apps.attendance.models import DailyAttendance
        today = timezone.now().date()
        daily = DailyAttendance.objects.filter(employee=obj, date=today).first()
        if daily and daily.last_check_out:
            return daily.last_check_out.strftime('%H:%M')
        return None

    def get_today_status(self, obj):
        from apps.attendance.models import DailyAttendance
        today = timezone.now().date()
        daily = DailyAttendance.objects.filter(employee=obj, date=today).first()
        if daily:
            return daily.status
        return 'absent'


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Employee detail serializer (to'liq)."""

    department_name = serializers.CharField(source='department.name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'full_name', 'first_name', 'last_name', 'middle_name',
            'department', 'department_name', 'position', 'position_name',
            'phone', 'email', 'work_start_time', 'work_end_time',
            'status', 'hire_date', 'photo', 'created_at', 'updated_at'
        ]


class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    """Employee create/update serializer."""

    class Meta:
        model = Employee
        fields = [
            'employee_id', 'first_name', 'last_name', 'middle_name',
            'department', 'position', 'phone', 'email',
            'work_start_time', 'work_end_time', 'status', 'hire_date', 'photo'
        ]
