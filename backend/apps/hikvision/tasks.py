"""
Celery tasks for Hikvision sync.
Avtomatik sinxronizatsiya uchun.
"""

from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .services import get_hikvision_service
from .models import HikvisionDevice, SyncLog
from apps.employees.models import Employee
from apps.attendance.models import AttendanceRecord, DailyAttendance

logger = logging.getLogger(__name__)


@shared_task
def sync_attendance_from_device(device_id: int = None, hours_back: int = 24):
    """
    Hikvision qurilmasidan davomat ma'lumotlarini sinxronlashtirish.

    Args:
        device_id: Qurilma ID si (None bo'lsa default qurilma ishlatiladi)
        hours_back: Necha soat oldingi ma'lumotlarni olish
    """
    now_local = timezone.localtime(timezone.now())
    start_time = now_local - timedelta(hours=hours_back)
    end_time = now_local

    if device_id:
        try:
            device = HikvisionDevice.objects.get(pk=device_id, is_active=True)
            service = get_hikvision_service(device)
        except HikvisionDevice.DoesNotExist:
            logger.error(f"Qurilma topilmadi: {device_id}")
            return {'error': 'Device not found'}
    else:
        service = get_hikvision_service()
        device = None

    # Sync log yaratish
    sync_log = None
    if device:
        sync_log = SyncLog.objects.create(
            device=device,
            status='partial',
            records_fetched=0,
            records_processed=0
        )

    try:
        # Eventlarni olish
        events = service.sync_attendance_events(
            start_time=start_time.replace(tzinfo=None),
            end_time=end_time.replace(tzinfo=None)
        )

        records_fetched = len(events)
        records_processed = 0

        for event in events:
            processed = process_attendance_event(event, device)
            if processed:
                records_processed += 1

        if sync_log:
            sync_log.status = 'success'
            sync_log.finished_at = timezone.now()
            sync_log.records_fetched = records_fetched
            sync_log.records_processed = records_processed
            sync_log.save()

        if device:
            device.status = 'online'
            device.last_sync = timezone.now()
            device.save()

        return {
            'success': True,
            'records_fetched': records_fetched,
            'records_processed': records_processed
        }

    except Exception as e:
        logger.error(f"Sinxronizatsiyada xatolik: {e}")

        if sync_log:
            sync_log.status = 'failed'
            sync_log.finished_at = timezone.now()
            sync_log.error_message = str(e)
            sync_log.save()

        if device:
            device.status = 'error'
            device.save()

        return {
            'success': False,
            'error': str(e)
        }


def process_attendance_event(event: dict, device=None) -> bool:
    """
    Bitta attendance eventni qayta ishlash va saqlash.

    Returns:
        True agar muvaffaqiyatli saqlangan bo'lsa
    """
    try:
        # Employee ID ni olish
        employee_no = event.get('employeeNoString') or event.get('employeeNo')
        if not employee_no:
            return False

        # Hodimni topish
        try:
            employee = Employee.objects.get(employee_id=employee_no)
        except Employee.DoesNotExist:
            logger.warning(f"Hodim topilmadi: {employee_no}")
            return False

        # Vaqtni parse qilish
        time_str = event.get('time')
        if not time_str:
            return False

        # Hikvision format: 2024-01-15T09:30:45+05:00 yoki 2024-01-15T09:30:45Z
        try:
            if 'Z' in time_str:
                timestamp = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')
            elif '+' in time_str:
                timestamp = datetime.fromisoformat(time_str)
            else:
                timestamp = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')

            timestamp = timezone.make_aware(timestamp) if timezone.is_naive(timestamp) else timestamp
        except Exception as e:
            logger.error(f"Vaqtni parse qilishda xatolik: {time_str} - {e}")
            return False

        # Duplicate tekshirish
        existing = AttendanceRecord.objects.filter(
            employee=employee,
            timestamp=timestamp
        ).exists()

        if existing:
            update_daily_attendance(employee, timestamp.date())
            return False

        # Event turini aniqlash (kirish yoki chiqish)
        event_type = determine_event_type(employee, timestamp)

        # AttendanceRecord yaratish
        AttendanceRecord.objects.create(
            employee=employee,
            event_type=event_type,
            timestamp=timestamp,
            device_id=device.serial_number if device else None,
            card_no=event.get('cardNo'),
            verify_mode=event.get('currentVerifyMode'),
        )

        # DailyAttendance yangilash
        update_daily_attendance(employee, timestamp.date())

        return True

    except Exception as e:
        logger.error(f"Event qayta ishlashda xatolik: {e}")
        return False


def determine_event_type(employee: Employee, timestamp: datetime) -> str:
    """
    Event turini aniqlash - kirish yoki chiqish.
    Mantiq: ish vaqti boshiga yaqin = kirish, ish vaqti oxiriga yaqin = chiqish
    """
    event_time = timestamp.time()
    work_start = employee.work_start_time
    work_end = employee.work_end_time

    # Tushlik vaqti (taxminan)
    lunch_start = datetime.strptime('12:00', '%H:%M').time()
    lunch_end = datetime.strptime('14:00', '%H:%M').time()

    # Kunning birinchi yarmida (ish boshiga yaqin) - kirish
    # Kunning ikkinchi yarmida (ish oxiriga yaqin) - chiqish
    # Tushlikka ham e'tibor berish mumkin

    # Sodda mantiq: 13:00 gacha - kirish, keyin - chiqish
    mid_day = datetime.strptime('13:00', '%H:%M').time()

    if event_time < mid_day:
        return 'check_in'
    else:
        return 'check_out'


def update_daily_attendance(employee: Employee, date):
    """
    Kunlik davomat yozuvini yangilash yoki yaratish.
    """
    # Shu kungi barcha yozuvlarni olish
    records = AttendanceRecord.objects.filter(
        employee=employee,
        timestamp__date=date
    ).order_by('timestamp')

    if not records.exists():
        return

    # Qurilma event turlari doim aniq bo'lmasligi mumkin.
    # Shu sababli kirish/chiqishni vaqt bo'yicha aniqlaymiz.
    # Kirish: 09:00 gacha bo'lgan eng erta event.
    # Chiqish: 18:00 +/- 4 daqiqa oralig'idagi eng kech event.
    check_in_cutoff = datetime.strptime('09:00', '%H:%M').time()
    checkout_start = datetime.strptime('17:56', '%H:%M').time()
    checkout_end = datetime.strptime('18:04', '%H:%M').time()

    first_check_in = None
    for record in records:
        if record.timestamp.time() <= check_in_cutoff:
            first_check_in = record.timestamp
            break
    if not first_check_in:
        first_check_in = records.first().timestamp

    last_check_out = None
    checkout_candidates = [
        record.timestamp for record in records
        if checkout_start <= record.timestamp.time() <= checkout_end
    ]
    if checkout_candidates:
        last_check_out = checkout_candidates[-1]

    # DailyAttendance yaratish yoki yangilash
    daily, created = DailyAttendance.objects.get_or_create(
        employee=employee,
        date=date,
        defaults={
            'scheduled_start': employee.work_start_time,
            'scheduled_end': employee.work_end_time,
            'first_check_in': first_check_in,
            'last_check_out': last_check_out,
        }
    )

    # Yangilanishlar
    daily.first_check_in = first_check_in
    daily.last_check_out = last_check_out
    daily.scheduled_start = employee.work_start_time
    daily.scheduled_end = employee.work_end_time

    # Hozircha ish jadvaliga qattiq bog'lanmasdan faqat kirish/chiqishni ko'rsatamiz
    if first_check_in:
        daily.status = DailyAttendance.Status.PRESENT
    else:
        daily.status = DailyAttendance.Status.ABSENT
    daily.late_minutes = 0
    daily.early_leave_minutes = 0
    daily.overtime_minutes = 0
    daily.total_work_minutes = daily.calculate_total_work_minutes()

    daily.save()


@shared_task
def sync_all_devices():
    """Barcha faol qurilmalardan sinxronlashtirish."""
    devices = HikvisionDevice.objects.filter(is_active=True)

    results = []
    for device in devices:
        result = sync_attendance_from_device.delay(device.id)
        results.append({
            'device_id': device.id,
            'device_name': device.name,
            'task_id': result.id
        })

    return results


@shared_task
def daily_attendance_report():
    """Har kuni ertalab kunlik davomat holatini tekshirish."""
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    # Kechagi kun uchun davomati yo'q hodimlarni topish
    active_employees = Employee.objects.filter(status='active')

    for employee in active_employees:
        daily, created = DailyAttendance.objects.get_or_create(
            employee=employee,
            date=yesterday,
            defaults={
                'scheduled_start': employee.work_start_time,
                'scheduled_end': employee.work_end_time,
                'status': 'absent'
            }
        )

        if created:
            # Yangi yaratilgan bo'lsa, demak hodim kelmagan
            daily.status = 'absent'
            daily.save()

    return {'date': yesterday.isoformat(), 'processed': active_employees.count()}
