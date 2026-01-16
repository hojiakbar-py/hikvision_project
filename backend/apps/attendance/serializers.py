"""Serializers for attendance app."""

from rest_framework import serializers
from .models import AttendanceRecord, DailyAttendance, WorkSchedule
from apps.employees.serializers import EmployeeListSerializer


class AttendanceRecordSerializer(serializers.ModelSerializer):
    """Davomat yozuvi serializer."""

    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'employee', 'employee_name', 'event_type', 'event_type_display',
            'timestamp', 'device_id', 'card_no', 'verify_mode', 'temperature', 'created_at'
        ]


class DailyAttendanceSerializer(serializers.ModelSerializer):
    """Kunlik davomat serializer."""

    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    department_name = serializers.CharField(source='employee.department.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Formatlangan vaqtlar
    check_in_time = serializers.SerializerMethodField()
    check_out_time = serializers.SerializerMethodField()
    work_hours = serializers.SerializerMethodField()

    class Meta:
        model = DailyAttendance
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'department_name',
            'date', 'first_check_in', 'last_check_out', 'check_in_time', 'check_out_time',
            'scheduled_start', 'scheduled_end', 'late_minutes', 'early_leave_minutes',
            'overtime_minutes', 'total_work_minutes', 'work_hours', 'status', 'status_display', 'notes'
        ]

    def get_check_in_time(self, obj):
        if obj.first_check_in:
            return obj.first_check_in.strftime('%H:%M')
        return None

    def get_check_out_time(self, obj):
        if obj.last_check_out:
            return obj.last_check_out.strftime('%H:%M')
        return None

    def get_work_hours(self, obj):
        if obj.total_work_minutes:
            hours = obj.total_work_minutes // 60
            minutes = obj.total_work_minutes % 60
            return f"{hours}s {minutes}d"
        return None


class DailyAttendanceDetailSerializer(DailyAttendanceSerializer):
    """Kunlik davomat batafsil serializer."""

    employee = EmployeeListSerializer(read_only=True)
    records = serializers.SerializerMethodField()

    class Meta(DailyAttendanceSerializer.Meta):
        fields = DailyAttendanceSerializer.Meta.fields + ['records']

    def get_records(self, obj):
        records = AttendanceRecord.objects.filter(
            employee=obj.employee,
            timestamp__date=obj.date
        ).order_by('timestamp')
        return AttendanceRecordSerializer(records, many=True).data


class WorkScheduleSerializer(serializers.ModelSerializer):
    """Ish jadvali serializer."""

    class Meta:
        model = WorkSchedule
        fields = '__all__'


class AttendanceStatisticsSerializer(serializers.Serializer):
    """Davomat statistikasi."""

    date = serializers.DateField()
    total_employees = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    late = serializers.IntegerField()
    early_leave = serializers.IntegerField()
    on_time = serializers.IntegerField()


class EmployeeAttendanceSummarySerializer(serializers.Serializer):
    """Hodim davomat xulosasi."""

    employee_id = serializers.CharField()
    employee_name = serializers.CharField()
    department = serializers.CharField()
    total_days = serializers.IntegerField()
    present_days = serializers.IntegerField()
    absent_days = serializers.IntegerField()
    late_days = serializers.IntegerField()
    early_leave_days = serializers.IntegerField()
    total_late_minutes = serializers.IntegerField()
    total_early_leave_minutes = serializers.IntegerField()
    total_overtime_minutes = serializers.IntegerField()
    attendance_rate = serializers.FloatField()
