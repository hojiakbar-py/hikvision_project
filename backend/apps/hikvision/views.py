"""Views for hikvision app."""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta, date
import logging
from rest_framework import status
from .models import HikvisionDevice, SyncLog
from .serializers import (
    HikvisionDeviceSerializer,
    HikvisionDeviceListSerializer,
    SyncLogSerializer,
    SyncRequestSerializer,
)
from .services import get_hikvision_service
from .tasks import sync_attendance_from_device
from apps.employees.models import Employee, Department

logger = logging.getLogger(__name__)


class HikvisionDeviceViewSet(viewsets.ModelViewSet):
    """Hikvision device CRUD."""

    queryset = HikvisionDevice.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return HikvisionDeviceListSerializer
        return HikvisionDeviceSerializer

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Qurilma bilan aloqani tekshirish."""
        device = self.get_object()

        # Debug: qurilma ma'lumotlarini log qilish
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Testing device: {device.ip_address}:{device.port} user={device.username}")

        service = get_hikvision_service(device)
        result = service.check_connection()

        # Qurilma ma'lumotlarini yangilash
        if result['status'] == 'online':
            device.status = 'online'
            if result.get('serial_number'):
                device.serial_number = result['serial_number']
            if result.get('model'):
                device.model = result['model']
            device.save()
        else:
            device.status = 'offline'
            device.save()

        return Response(result)

    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Qurilmadan ma'lumotlarni sinxronlashtirish."""
        device = self.get_object()
        hours_back = request.data.get('hours_back', 24)

        # Sinxron rejimda ishlatish (Celery'siz)
        try:
            result = sync_attendance_from_device(device.id, hours_back)
            if result.get('success'):
                return Response({
                    'message': 'Sinxronizatsiya muvaffaqiyatli',
                    'records_fetched': result.get('records_fetched', 0),
                    'records_processed': result.get('records_processed', 0)
                })
            else:
                return Response({
                    'message': 'Sinxronizatsiyada xatolik',
                    'error': result.get('error', 'Unknown error')
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'message': 'Sinxronizatsiyada xatolik',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Qurilmadagi foydalanuvchilar ro'yxati."""
        device = self.get_object()
        service = get_hikvision_service(device)
        result = service.get_user_list()

        return Response(result)

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Qurilma sync loglari."""
        device = self.get_object()
        logs = SyncLog.objects.filter(device=device)[:50]
        serializer = SyncLogSerializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def import_users(self, request, pk=None):
        """Qurilmadagi foydalanuvchilarni hodimlar sifatida import qilish."""
        device = self.get_object()
        service = get_hikvision_service(device)

        try:
            result = service.get_user_list()

            if not result.get('success'):
                return Response({
                    'message': 'Foydalanuvchilarni olishda xatolik',
                    'error': result.get('error', 'Unknown error')
                }, status=status.HTTP_400_BAD_REQUEST)

            data = result.get('data', {})
            users = []

            # JSON strukturaga qarab parse qilish
            if 'UserInfoSearch' in data:
                users = data['UserInfoSearch'].get('UserInfo', [])
            elif 'UserInfo' in data:
                users = data['UserInfo']

            if isinstance(users, dict):
                users = [users]

            # Default bo'lim yaratish yoki olish
            default_dept, _ = Department.objects.get_or_create(
                name="Umumiy",
                defaults={'description': "Avtomatik yaratilgan bo'lim"}
            )

            imported_count = 0
            skipped_count = 0

            for user in users:
                employee_no = user.get('employeeNo')
                name = user.get('name', '')

                if not employee_no:
                    skipped_count += 1
                    continue

                # Mavjud hodimni tekshirish
                if Employee.objects.filter(employee_id=employee_no).exists():
                    skipped_count += 1
                    continue

                # Ism va familiyani ajratish
                name_parts = name.split() if name else ['Noma\'lum']
                first_name = name_parts[0] if name_parts else 'Noma\'lum'
                last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

                # Yangi hodim yaratish
                Employee.objects.create(
                    employee_id=employee_no,
                    first_name=first_name,
                    last_name=last_name,
                    department=default_dept,
                    status='active',
                    work_start_time='09:00',
                    work_end_time='18:00',
                    hire_date=date.today(),
                )
                imported_count += 1

            return Response({
                'message': f'{imported_count} ta hodim import qilindi',
                'imported': imported_count,
                'skipped': skipped_count,
                'total_in_device': len(users)
            })

        except Exception as e:
            logger.error(f"Import xatoligi: {e}")
            return Response({
                'message': 'Import qilishda xatolik',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Sync log read-only viewset."""

    queryset = SyncLog.objects.select_related('device').all()
    serializer_class = SyncLogSerializer


class ManualSyncView(APIView):
    """Manual sync trigger."""

    def post(self, request):
        serializer = SyncRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        device_id = serializer.validated_data.get('device_id')
        hours_back = serializer.validated_data.get('hours_back', 24)

        # Sinxron rejimda ishlatish (Celery'siz)
        try:
            result = sync_attendance_from_device(device_id, hours_back)
            if result.get('success'):
                return Response({
                    'message': 'Sinxronizatsiya muvaffaqiyatli',
                    'records_fetched': result.get('records_fetched', 0),
                    'records_processed': result.get('records_processed', 0)
                })
            else:
                return Response({
                    'message': 'Sinxronizatsiyada xatolik',
                    'error': result.get('error', 'Unknown error')
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'message': 'Sinxronizatsiyada xatolik',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceStatusView(APIView):
    """Barcha qurilmalar holati."""

    def get(self, request):
        devices = HikvisionDevice.objects.filter(is_active=True)

        result = []
        for device in devices:
            last_sync = SyncLog.objects.filter(device=device).first()
            result.append({
                'id': device.id,
                'name': device.name,
                'ip_address': device.ip_address,
                'status': device.status,
                'last_sync': device.last_sync,
                'last_sync_status': last_sync.status if last_sync else None,
                'last_sync_records': last_sync.records_processed if last_sync else 0,
            })

        return Response(result)
