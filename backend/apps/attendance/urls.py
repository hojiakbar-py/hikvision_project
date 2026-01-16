"""URL configuration for attendance app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AttendanceRecordViewSet,
    DailyAttendanceViewSet,
    WorkScheduleViewSet,
    DashboardStatisticsView,
    EmployeeAttendanceReportView,
    MonthlyReportView,
)

router = DefaultRouter()
router.register('records', AttendanceRecordViewSet)
router.register('daily', DailyAttendanceViewSet)
router.register('schedules', WorkScheduleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardStatisticsView.as_view(), name='dashboard'),
    path('report/employee/<int:employee_id>/', EmployeeAttendanceReportView.as_view(), name='employee_report'),
    path('report/monthly/', MonthlyReportView.as_view(), name='monthly_report'),
]
