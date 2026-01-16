"""Admin configuration for hikvision app."""

from django.contrib import admin
from .models import HikvisionDevice, SyncLog


@admin.register(HikvisionDevice)
class HikvisionDeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip_address', 'port', 'status', 'last_sync', 'is_active']
    list_filter = ['status', 'is_active']
    search_fields = ['name', 'ip_address', 'serial_number']


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ['device', 'started_at', 'finished_at', 'status', 'records_fetched', 'records_processed']
    list_filter = ['status', 'device']
    date_hierarchy = 'started_at'
