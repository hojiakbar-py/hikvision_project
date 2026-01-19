"""Views for employees app."""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta

from .models import Department, Position, Employee
from .serializers import (
    DepartmentSerializer,
    PositionSerializer,
    EmployeeListSerializer,
    EmployeeDetailSerializer,
    EmployeeCreateUpdateSerializer,
)
from apps.attendance.models import DailyAttendance, AttendanceRecord


class DepartmentViewSet(viewsets.ModelViewSet):
    """Department CRUD operations."""

    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']


class PositionViewSet(viewsets.ModelViewSet):
    """Position CRUD operations."""

    queryset = Position.objects.select_related('department').all()
    serializer_class = PositionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['department']
    search_fields = ['name']


class EmployeeViewSet(viewsets.ModelViewSet):
    """Employee CRUD operations."""

    queryset = Employee.objects.select_related('department', 'position').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'position', 'status']
    search_fields = ['first_name', 'last_name', 'employee_id', 'phone']
    ordering_fields = ['last_name', 'first_name', 'hire_date', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EmployeeCreateUpdateSerializer
        return EmployeeDetailSerializer

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Hodimlar statistikasi."""
        total = Employee.objects.count()
        active = Employee.objects.filter(status='active').count()
        inactive = Employee.objects.filter(status='inactive').count()
        on_leave = Employee.objects.filter(status='on_leave').count()

        by_department = Department.objects.annotate(
            employee_count=Count('employees', filter=models.Q(employees__status='active'))
        ).values('name', 'employee_count')

        return Response({
            'total': total,
            'active': active,
            'inactive': inactive,
            'on_leave': on_leave,
            'by_department': list(by_department),
        })

    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """Hodim profili - to'liq statistika bilan."""
        employee = self.get_object()

        # Joriy oy boshlanishi
        today = timezone.now().date()
        month_start = today.replace(day=1)

        # Oylik davomat ma'lumotlari
        monthly_attendance = DailyAttendance.objects.filter(
            employee=employee,
            date__gte=month_start,
            date__lte=today
        )

        # Statistikalar
        total_days = monthly_attendance.count()
        present_days = monthly_attendance.filter(status='present').count()
        late_days = monthly_attendance.filter(status__in=['late', 'late_and_early']).count()
        absent_days = monthly_attendance.filter(status='absent').count()
        early_leave_days = monthly_attendance.filter(status__in=['early_leave', 'late_and_early']).count()

        # Jami kechikish daqiqalari
        total_late_minutes = monthly_attendance.aggregate(
            total=Sum('late_minutes')
        )['total'] or 0

        # Jami erta ketish daqiqalari
        total_early_leave_minutes = monthly_attendance.aggregate(
            total=Sum('early_leave_minutes')
        )['total'] or 0

        # Jami ish vaqti (daqiqa)
        total_work_minutes = monthly_attendance.aggregate(
            total=Sum('total_work_minutes')
        )['total'] or 0

        # Oxirgi 30 kunlik davomat tarixi
        last_30_days = DailyAttendance.objects.filter(
            employee=employee,
            date__gte=today - timedelta(days=30)
        ).order_by('-date').values(
            'date', 'status', 'first_check_in', 'last_check_out',
            'late_minutes', 'early_leave_minutes', 'total_work_minutes'
        )

        # Bugungi holatni olish
        today_attendance = DailyAttendance.objects.filter(
            employee=employee,
            date=today
        ).first()

        # Serializer bilan asosiy ma'lumotlar
        serializer = EmployeeDetailSerializer(employee)

        return Response({
            'employee': serializer.data,
            'today': {
                'status': today_attendance.status if today_attendance else 'absent',
                'check_in': timezone.localtime(today_attendance.first_check_in).strftime('%H:%M') if today_attendance and today_attendance.first_check_in else None,
                'check_out': timezone.localtime(today_attendance.last_check_out).strftime('%H:%M') if today_attendance and today_attendance.last_check_out else None,
                'late_minutes': today_attendance.late_minutes if today_attendance else 0,
                'early_leave_minutes': today_attendance.early_leave_minutes if today_attendance else 0,
                'work_minutes': today_attendance.total_work_minutes if today_attendance else 0,
            },
            'monthly_stats': {
                'month': today.strftime('%Y-%m'),
                'total_days': total_days,
                'present_days': present_days,
                'late_days': late_days,
                'absent_days': absent_days,
                'early_leave_days': early_leave_days,
                'total_late_minutes': total_late_minutes,
                'total_early_leave_minutes': total_early_leave_minutes,
                'total_work_minutes': total_work_minutes,
                'total_work_hours': round(total_work_minutes / 60, 1),
                'avg_late_minutes': round(total_late_minutes / late_days, 1) if late_days > 0 else 0,
            },
            'attendance_history': list(last_30_days),
        })

    # Qo'shimcha viewsetlar yoki funksiyalar kerak bo'lsa, shu yerda qo'shish mumkin.@action(detail=False, methods=['post'])
    def import_from_device(self, request):
        """Hikvision qurilmasidan hodimlarni import qilish."""
        from apps.hikvision.services import get_hikvision_service
        from apps.hikvision.models import HikvisionDevice
        from rest_framework import status
        
        device_id = request.data.get('device_id')
        
        if not device_id:
            return Response(
                {'error': 'Device ID talab etiladi'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            device = HikvisionDevice.objects.get(id=device_id)
            service = get_hikvision_service(device)
            
            # Userlarni olish
            result = service.get_user_list()
            
            if not result['success']:
                return Response(
                    {'error': result.get('error', 'Userlarni olishda xatolik')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            users = result['data'].get('UserInfoSearch', {}).get('UserInfo', [])
            
            # Import qilish
            imported = 0
            skipped = 0
            errors = []
            
            for user in users:
                try:
                    employee_id = user.get('employeeNo')
                    name = user.get('name', '')
                    
                    if not employee_id or not name:
                        skipped += 1
                        continue
                    
                    # Allaqachon mavjudmi tekshirish
                    employee, created = Employee.objects.get_or_create(
                        employee_id=employee_id,
                        defaults={
                            'first_name': name.split()[0] if name else 'Unknown',
                            'last_name': ' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
                            'status': 'active'
                        }
                    )
                    
                    if created:
                        imported += 1
                    else:
                        skipped += 1
                        
                except Exception as e:
                    errors.append(f"{user.get('name', 'Unknown')}: {str(e)}")
            
            return Response({
                'message': f'{imported} ta hodim import qilindi',
                'imported': imported,
                'skipped': skipped,
                'errors': errors
            })
            
        except HikvisionDevice.DoesNotExist:
            return Response(
                {'error': 'Qurilma topilmadi'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
