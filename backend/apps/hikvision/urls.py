"""URL configuration for hikvision app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HikvisionDeviceViewSet,
    SyncLogViewSet,
    ManualSyncView,
    DeviceStatusView,
)

router = DefaultRouter()
router.register('devices', HikvisionDeviceViewSet)
router.register('logs', SyncLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('sync/', ManualSyncView.as_view(), name='manual_sync'),
    path('status/', DeviceStatusView.as_view(), name='device_status'),
]
