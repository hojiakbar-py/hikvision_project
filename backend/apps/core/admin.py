"""Core app admin configuration."""

from django.contrib import admin
from .models import Organization, Branch, OrganizationSettings


class BranchInline(admin.TabularInline):
    """Branch inline for Organization admin."""

    model = Branch
    extra = 0
    fields = ['name', 'code', 'branch_type', 'city', 'is_active']
    readonly_fields = ['code']
    show_change_link = True


class OrganizationSettingsInline(admin.StackedInline):
    """Settings inline for Organization admin."""

    model = OrganizationSettings
    can_delete = False


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Organization admin configuration."""

    list_display = [
        'name', 'code', 'industry', 'total_branches',
        'total_employees', 'is_active'
    ]
    list_filter = ['is_active', 'industry', 'currency']
    search_fields = ['name', 'code', 'legal_name', 'inn']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrganizationSettingsInline, BranchInline]

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'legal_name', 'code', 'inn', 'logo')
        }),
        ('Aloqa', {
            'fields': ('address', 'phone', 'email', 'website')
        }),
        ('Biznes ma\'lumotlari', {
            'fields': ('industry', 'founded_date', 'employee_count')
        }),
        ('Sozlamalar', {
            'fields': ('timezone', 'currency', 'language', 'is_active')
        }),
        ('Tizim', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    """Branch admin configuration."""

    list_display = [
        'name', 'code', 'organization', 'branch_type',
        'city', 'employee_count', 'is_active'
    ]
    list_filter = ['organization', 'branch_type', 'is_active', 'city']
    search_fields = ['name', 'code', 'city', 'address']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['organization', 'parent']

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('organization', 'parent', 'name', 'code', 'branch_type')
        }),
        ('Manzil', {
            'fields': ('country', 'region', 'city', 'address', 'latitude', 'longitude')
        }),
        ('Aloqa', {
            'fields': ('phone', 'email')
        }),
        ('Ish vaqti', {
            'fields': ('work_start_time', 'work_end_time', 'timezone')
        }),
        ('Holat', {
            'fields': ('is_active', 'is_head_office', 'established_date', 'description')
        }),
        ('Tizim', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrganizationSettings)
class OrganizationSettingsAdmin(admin.ModelAdmin):
    """Organization settings admin configuration."""

    list_display = [
        'organization', 'late_threshold_minutes',
        'auto_sync_interval_minutes', 'send_daily_report'
    ]
    list_filter = ['send_daily_report', 'allow_remote_work']
    search_fields = ['organization__name']
