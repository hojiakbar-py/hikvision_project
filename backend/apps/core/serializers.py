"""
Core Application Serializers.

Bu modul Organization va Branch modellarini API orqali
boshqarish uchun serializer larni o'z ichiga oladi.
"""

from rest_framework import serializers
from .models import Organization, Branch, OrganizationSettings


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Organization modeli uchun serializer.

    Tashkilot asosiy ma'lumotlarini API orqali qaytarish.
    """

    total_branches = serializers.IntegerField(read_only=True)
    active_branches = serializers.IntegerField(read_only=True)
    total_employees = serializers.IntegerField(read_only=True)

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'legal_name', 'code', 'inn',
            'logo', 'description', 'address', 'phone', 'email', 'website',
            'founded_date', 'industry', 'employee_count',
            'is_active', 'timezone', 'currency', 'language',
            'total_branches', 'active_branches', 'total_employees',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class BranchSerializer(serializers.ModelSerializer):
    """
    Branch modeli uchun serializer.

    Filial asosiy ma'lumotlarini API orqali qaytarish.
    """

    organization_name = serializers.CharField(source='organization.name', read_only=True)
    full_address = serializers.CharField(read_only=True)
    employee_count = serializers.IntegerField(read_only=True)
    department_count = serializers.IntegerField(read_only=True)
    device_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Branch
        fields = [
            'id', 'organization', 'organization_name', 'parent', 'name', 'code',
            'branch_type', 'address', 'city', 'region', 'country',
            'latitude', 'longitude', 'phone', 'email',
            'work_start_time', 'work_end_time', 'timezone',
            'is_active', 'is_head_office', 'description', 'established_date',
            'full_address', 'employee_count', 'department_count', 'device_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class BranchAttendanceStatsSerializer(serializers.Serializer):
    """
    Filial davomat statistikasi serializer.

    Kunlik davomat statistikasini formatlash.
    """

    date = serializers.DateField()
    total_employees = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    late = serializers.IntegerField()
    half_day = serializers.IntegerField()
    on_leave = serializers.IntegerField()
    present_percentage = serializers.FloatField()
    late_percentage = serializers.FloatField()


class BranchAttendanceSummarySerializer(serializers.Serializer):
    """
    Filial davomat xulosasi serializer.

    Ma'lum davrdagi davomat xulosasini formatlash.
    """

    period = serializers.DictField()
    total_employees = serializers.IntegerField()
    total_records = serializers.IntegerField()
    total_late_minutes = serializers.IntegerField()
    total_overtime_minutes = serializers.IntegerField()
    average_work_hours = serializers.FloatField()
    present_count = serializers.IntegerField()
    late_count = serializers.IntegerField()
    absent_count = serializers.IntegerField()
    average_present_per_day = serializers.FloatField(required=False)
    average_late_per_day = serializers.FloatField(required=False)
    average_absent_per_day = serializers.FloatField(required=False)


class DepartmentAttendanceBreakdownSerializer(serializers.Serializer):
    """
    Bo'limlar bo'yicha davomat taqsimoti serializer.
    """

    department_id = serializers.IntegerField()
    department_name = serializers.CharField()
    department_code = serializers.CharField()
    total_employees = serializers.IntegerField()
    present = serializers.IntegerField()
    late = serializers.IntegerField()
    absent = serializers.IntegerField()
    half_day = serializers.IntegerField()
    on_leave = serializers.IntegerField()
    present_percentage = serializers.FloatField()


class TopLatecomersSerializer(serializers.Serializer):
    """
    Eng ko'p kechikkanlar serializer.
    """

    employee_id = serializers.IntegerField()
    personnel_number = serializers.CharField()
    employee_name = serializers.CharField()
    department = serializers.CharField(allow_null=True)
    late_count = serializers.IntegerField()
    total_late_minutes = serializers.IntegerField()
    average_late_minutes = serializers.FloatField()


class OrganizationSettingsSerializer(serializers.ModelSerializer):
    """
    OrganizationSettings modeli uchun serializer.
    """

    organization_name = serializers.CharField(source='organization.name', read_only=True)
    working_days_display = serializers.CharField(read_only=True)

    class Meta:
        model = OrganizationSettings
        fields = [
            'id', 'organization', 'organization_name',
            'late_threshold_minutes', 'early_leave_threshold_minutes',
            'overtime_calculation_enabled', 'half_day_threshold_hours',
            'working_days', 'working_days_display',
            'auto_sync_interval_minutes', 'sync_history_days',
            'notification_email', 'send_daily_report', 'send_late_notifications',
            'allow_remote_work', 'require_photo_on_check', 'allow_manual_attendance',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
