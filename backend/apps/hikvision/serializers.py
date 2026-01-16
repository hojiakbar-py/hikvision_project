"""Serializers for hikvision app."""

from rest_framework import serializers
from .models import HikvisionDevice, SyncLog


class HikvisionDeviceSerializer(serializers.ModelSerializer):
    """Hikvision device serializer."""

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    password = serializers.CharField(write_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = HikvisionDevice
        fields = [
            'id', 'name', 'ip_address', 'port', 'username', 'password',
            'serial_number', 'model', 'location', 'branch', 'branch_name',
            'status', 'status_display', 'last_sync', 'is_active', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['serial_number', 'model', 'status', 'last_sync', 'branch_name']


class HikvisionDeviceListSerializer(serializers.ModelSerializer):
    """Hikvision device list serializer (parolsiz)."""

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = HikvisionDevice
        fields = [
            'id', 'name', 'ip_address', 'port', 'serial_number', 'model',
            'location', 'branch', 'branch_name', 'status', 'status_display', 
            'last_sync', 'is_active'
        ]


class SyncLogSerializer(serializers.ModelSerializer):
    """Sync log serializer."""

    device_name = serializers.CharField(source='device.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        model = SyncLog
        fields = [
            'id', 'device', 'device_name', 'started_at', 'finished_at',
            'duration', 'status', 'status_display', 'records_fetched',
            'records_processed', 'error_message'
        ]

    def get_duration(self, obj):
        if obj.finished_at and obj.started_at:
            diff = obj.finished_at - obj.started_at
            return int(diff.total_seconds())
        return None


class SyncRequestSerializer(serializers.Serializer):
    """Manual sync request serializer."""

    device_id = serializers.IntegerField(required=False)
    hours_back = serializers.IntegerField(default=24, min_value=1, max_value=720)
