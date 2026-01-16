"""Views for attendance app."""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import status
from .models import AttendanceRecord, DailyAttendance, WorkSchedule
from .serializers import (
    AttendanceRecordSerializer,
    DailyAttendanceSerializer,
    DailyAttendanceDetailSerializer,
    WorkScheduleSerializer,
    AttendanceStatisticsSerializer,
    EmployeeAttendanceSummarySerializer,
)
from apps.employees.models import Employee


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    """Davomat yozuvlari CRUD."""

    queryset = AttendanceRecord.objects.select_related('employee').all()
    serializer_class = AttendanceRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'event_type']
    ordering_fields = ['timestamp']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Sana bo'yicha filter
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(timestamp__date=date)

        # Sana oralig'i
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)

        return queryset


class DailyAttendanceViewSet(viewsets.ModelViewSet):
    """Kunlik davomat CRUD."""

    queryset = DailyAttendance.objects.select_related(
        'employee', 'employee__department', 'employee__position'
    ).all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'status', 'date']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['date', 'late_minutes', 'early_leave_minutes']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DailyAttendanceDetailSerializer
        return DailyAttendanceSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Bo'lim bo'yicha filter
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(employee__department_id=department)

        # Sana oralig'i
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(date__gte=start_date, date__lte=end_date)

        return queryset

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Bugungi davomat."""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(date=today)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def late_today(self, request):
        """Bugun kechikkanlar."""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            date=today,
            status__in=['late', 'late_and_early']
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class WorkScheduleViewSet(viewsets.ModelViewSet):
    """Ish jadvali CRUD."""

    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer


class DashboardStatisticsView(APIView):
    """Dashboard uchun statistikalar."""

    def get(self, request):
        today = timezone.now().date()

        # Bugungi statistika
        total_employees = Employee.objects.filter(status='active').count()

        today_attendance = DailyAttendance.objects.filter(date=today)
        present = today_attendance.exclude(status='absent').count()
        absent = total_employees - present
        late = today_attendance.filter(status__in=['late', 'late_and_early']).count()
        early_leave = today_attendance.filter(status__in=['early_leave', 'late_and_early']).count()
        on_time = today_attendance.filter(status='present').count()

        # Haftalik trend
        week_ago = today - timedelta(days=7)
        weekly_data = []
        for i in range(7):
            day = week_ago + timedelta(days=i+1)
            day_attendance = DailyAttendance.objects.filter(date=day)
            weekly_data.append({
                'date': day.isoformat(),
                'present': day_attendance.exclude(status='absent').count(),
                'late': day_attendance.filter(status__in=['late', 'late_and_early']).count(),
                'absent': total_employees - day_attendance.exclude(status='absent').count(),
            })

        # Eng ko'p kechikkanlar (shu oy)
        month_start = today.replace(day=1)
        top_late = DailyAttendance.objects.filter(
            date__gte=month_start,
            late_minutes__gt=0
        ).values(
            'employee__employee_id',
            'employee__first_name',
            'employee__last_name',
        ).annotate(
            total_late_minutes=Sum('late_minutes'),
            late_count=Count('id')
        ).order_by('-total_late_minutes')[:10]

        return Response({
            'today': {
                'date': today.isoformat(),
                'total_employees': total_employees,
                'present': present,
                'absent': absent,
                'late': late,
                'early_leave': early_leave,
                'on_time': on_time,
                'attendance_rate': round((present / total_employees * 100), 1) if total_employees > 0 else 0,
            },
            'weekly_trend': weekly_data,
            'top_late_employees': list(top_late),
        })


class EmployeeAttendanceReportView(APIView):
    """Hodim davomat hisoboti."""

    def get(self, request, employee_id):
        try:
            employee = Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            return Response({'error': 'Hodim topilmadi'}, status=status.HTTP_404_NOT_FOUND)

        # Sana oralig'i
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            # Default: shu oy
            today = timezone.now().date()
            start_date = today.replace(day=1)
            end_date = today
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        attendance = DailyAttendance.objects.filter(
            employee=employee,
            date__gte=start_date,
            date__lte=end_date
        )

        total_days = (end_date - start_date).days + 1
        present_days = attendance.exclude(status='absent').count()
        absent_days = attendance.filter(status='absent').count()
        late_days = attendance.filter(status__in=['late', 'late_and_early']).count()
        early_leave_days = attendance.filter(status__in=['early_leave', 'late_and_early']).count()

        aggregates = attendance.aggregate(
            total_late=Sum('late_minutes'),
            total_early_leave=Sum('early_leave_minutes'),
            total_overtime=Sum('overtime_minutes'),
            total_work=Sum('total_work_minutes'),
        )

        return Response({
            'employee': {
                'id': employee.id,
                'employee_id': employee.employee_id,
                'name': employee.full_name,
                'department': employee.department.name if employee.department else None,
                'position': employee.position.name if employee.position else None,
            },
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
            },
            'summary': {
                'total_days': total_days,
                'present_days': present_days,
                'absent_days': absent_days,
                'late_days': late_days,
                'early_leave_days': early_leave_days,
                'on_time_days': present_days - late_days,
                'total_late_minutes': aggregates['total_late'] or 0,
                'total_early_leave_minutes': aggregates['total_early_leave'] or 0,
                'total_overtime_minutes': aggregates['total_overtime'] or 0,
                'total_work_minutes': aggregates['total_work'] or 0,
                'attendance_rate': round((present_days / total_days * 100), 1) if total_days > 0 else 0,
            },
            'daily_records': DailyAttendanceSerializer(attendance.order_by('date'), many=True).data,
        })


class MonthlyReportView(APIView):
    """Oylik hisobot."""

    def get(self, request):
        # Oy va yil parametrlari
        year = int(request.query_params.get('year', timezone.now().year))
        month = int(request.query_params.get('month', timezone.now().month))
        department_id = request.query_params.get('department')

        # Oyning boshi va oxiri
        from calendar import monthrange
        start_date = datetime(year, month, 1).date()
        _, last_day = monthrange(year, month)
        end_date = datetime(year, month, last_day).date()

        # Hodimlar queryset
        employees = Employee.objects.filter(status='active')
        if department_id:
            employees = employees.filter(department_id=department_id)

        report_data = []
        for employee in employees:
            attendance = DailyAttendance.objects.filter(
                employee=employee,
                date__gte=start_date,
                date__lte=end_date
            )

            aggregates = attendance.aggregate(
                total_late=Sum('late_minutes'),
                total_early_leave=Sum('early_leave_minutes'),
                total_overtime=Sum('overtime_minutes'),
                total_work=Sum('total_work_minutes'),
            )

            present_days = attendance.exclude(status='absent').count()
            total_days = attendance.count()

            report_data.append({
                'employee_id': employee.employee_id,
                'employee_name': employee.full_name,
                'department': employee.department.name if employee.department else None,
                'position': employee.position.name if employee.position else None,
                'total_days': total_days,
                'present_days': present_days,
                'absent_days': attendance.filter(status='absent').count(),
                'late_days': attendance.filter(status__in=['late', 'late_and_early']).count(),
                'early_leave_days': attendance.filter(status__in=['early_leave', 'late_and_early']).count(),
                'total_late_minutes': aggregates['total_late'] or 0,
                'total_early_leave_minutes': aggregates['total_early_leave'] or 0,
                'total_overtime_minutes': aggregates['total_overtime'] or 0,
                'total_work_hours': round((aggregates['total_work'] or 0) / 60, 1),
                'attendance_rate': round((present_days / total_days * 100), 1) if total_days > 0 else 0,
            })

        return Response({
            'period': {
                'year': year,
                'month': month,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
            },
            'total_employees': len(report_data),
            'employees': report_data,
        })
