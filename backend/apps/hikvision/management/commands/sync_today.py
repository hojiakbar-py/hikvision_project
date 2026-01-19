"""
Bugungi kunning davomat ma'lumotlarini sinxronlashtirish.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from apps.hikvision.services import get_hikvision_service
from apps.hikvision.tasks import process_attendance_event
from apps.employees.models import Employee
from apps.attendance.models import AttendanceRecord, DailyAttendance


class Command(BaseCommand):
    help = 'Bugungi barcha davomat ma\'lumotlarini qurilmadan import qilish'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Necha soat oldingi ma\'lumotlarni olish (default: 24)',
        )
        parser.add_argument(
            '--date',
            type=str,
            help='Ma\'lum bir sana uchun (format: YYYY-MM-DD)',
        )

    def handle(self, *args, **options):
        hours_back = options['hours']
        target_date = options.get('date')

        self.stdout.write(self.style.HTTP_INFO('\n' + '='*70))
        self.stdout.write(self.style.HTTP_INFO('   HIKVISION DAVOMAT IMPORT'))
        self.stdout.write(self.style.HTTP_INFO('='*70 + '\n'))

        # Vaqt oralig'ini aniqlash
        if target_date:
            try:
                parsed_date = datetime.strptime(target_date, '%Y-%m-%d')
                start_time = parsed_date.replace(hour=0, minute=0, second=0)
                end_time = parsed_date.replace(hour=23, minute=59, second=59)
                self.stdout.write(f"📅 Sana: {target_date}")
            except ValueError:
                self.stdout.write(self.style.ERROR('❌ Noto\'g\'ri sana formati. YYYY-MM-DD formatini ishlating.'))
                return
        else:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)
            self.stdout.write(f"📅 Vaqt oralig'i: {hours_back} soat orqaga")

        self.stdout.write(f"⏰ Boshlanish: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write(f"⏰ Tugash: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Hikvision service
        try:
            service = get_hikvision_service()
            self.stdout.write(self.style.SUCCESS('✅ Hikvision qurilmaga ulandi'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Qurilmaga ulanib bo\'lmadi: {e}'))
            return

        # Eventlarni olish
        self.stdout.write('\n🔄 Ma\'lumotlar yuklanmoqda...\n')
        try:
            events = service.sync_attendance_events(
                start_time=start_time,
                end_time=end_time
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Jami {len(events)} ta event topildi\n'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Eventlarni olishda xatolik: {e}'))
            return

        if not events:
            self.stdout.write(self.style.WARNING('⚠️  Hech qanday event topilmadi'))
            return

        # Eventlarni qayta ishlash
        self.stdout.write('📊 Eventlarni qayta ishlash:\n')
        self.stdout.write('-' * 70)

        processed_count = 0
        skipped_count = 0
        error_count = 0

        for idx, event in enumerate(events, 1):
            employee_no = event.get('employeeNoString') or event.get('employeeNo')
            time_str = event.get('time', 'N/A')
            name = event.get('name', 'N/A')

            try:
                # Hodimni topish
                try:
                    employee = Employee.objects.get(employee_id=employee_no)
                except Employee.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'{idx}. ⚠️  Hodim topilmadi: {employee_no} ({name})')
                    )
                    skipped_count += 1
                    continue

                # Qayta ishlash
                result = process_attendance_event(event, device=None)

                if result:
                    processed_count += 1
                    status_icon = '✅'
                else:
                    skipped_count += 1
                    status_icon = '⏭️ '

                # Progress ko'rsatish
                if idx % 10 == 0 or idx == len(events):
                    self.stdout.write(
                        f'{idx}/{len(events)} - {status_icon} {employee.full_name} | {time_str}'
                    )

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'{idx}. ❌ Xatolik: {employee_no} - {e}')
                )

        # Natijalar
        self.stdout.write('\n' + '-' * 70)
        self.stdout.write('\n📈 NATIJALAR:\n')
        self.stdout.write(f'   ✅ Muvaffaqiyatli: {processed_count}')
        self.stdout.write(f'   ⏭️  O\'tkazildi: {skipped_count}')
        self.stdout.write(f'   ❌ Xatolik: {error_count}')
        self.stdout.write(f'   📊 Jami: {len(events)}\n')

        # DailyAttendance statistikasi
        if target_date:
            check_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        else:
            check_date = timezone.now().date()

        daily_stats = DailyAttendance.objects.filter(date=check_date)

        self.stdout.write('📋 KUNLIK DAVOMAT HOLATI:\n')
        self.stdout.write(f'   📅 Sana: {check_date}')
        self.stdout.write(f'   👥 Jami yozuvlar: {daily_stats.count()}')
        self.stdout.write(f'   ✅ Kelgan: {daily_stats.filter(status__in=["present", "late", "early_leave", "late_and_early"]).count()}')
        self.stdout.write(f'   ⏰ Kechikkan: {daily_stats.filter(status__in=["late", "late_and_early"]).count()}')
        self.stdout.write(f'   ❌ Kelmagan: {daily_stats.filter(status="absent").count()}')

        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('✨ Import yakunlandi!'))
        self.stdout.write('='*70 + '\n')
