"""
Attendance Application Models.

Bu modul davomat nazorati tizimining asosiy modellarini o'z ichiga oladi.
Hodimlarning kunlik kirish/chiqish vaqtlari, kechikish, erta ketish va
ish jadvallarini boshqarish uchun ishlatiladi.

Models:
    - AttendanceRecord: Kirish/chiqish yozuvlari (raw data)
    - DailyAttendance: Kunlik davomat xulosasi
    - WorkSchedule: Ish jadvali sozlamalari
    - Holiday: Bayram va dam olish kunlari
    - LeaveRequest: Ta'til so'rovlari

Example:
    >>> from apps.attendance.models import DailyAttendance
    >>> attendance = DailyAttendance.objects.get(
    ...     employee__employee_id="EMP001",
    ...     date="2024-01-15"
    ... )
    >>> attendance.status
    'late'
    >>> attendance.late_minutes
    15
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, time, date
from typing import Optional, Tuple
from decimal import Decimal


class AttendanceRecord(models.Model):
    """
    Davomat yozuvi - Hikvision qurilmasidan kelgan raw ma'lumotlar.

    Har bir kirish yoki chiqish hodisasi alohida yozuv sifatida saqlanadi.
    Bu ma'lumotlar keyinchalik DailyAttendance modelida jamlanadi.

    Attributes:
        employee (Employee): Hodim
        event_type (str): Hodisa turi (kirish/chiqish)
        timestamp (datetime): Hodisa vaqti
        device_id (str): Qurilma identifikatori
        card_no (str): RFID karta raqami
        verify_mode (str): Tekshirish usuli (yuz, barmoq, karta)
        temperature (float): Tana harorati
        mask_status (str): Niqob holati
        confidence (float): Tanib olish ishonchliligi
        raw_data (JSON): Qurilmadan kelgan to'liq ma'lumot

    Example:
        >>> record = AttendanceRecord.objects.create(
        ...     employee=emp,
        ...     event_type='check_in',
        ...     timestamp=timezone.now(),
        ...     device_id='DEV001'
        ... )
    """

    class EventType(models.TextChoices):
        """
        Hodisa turlari.

        Attributes:
            CHECK_IN: Ishga kirish
            CHECK_OUT: Ishdan chiqish
        """
        CHECK_IN = 'check_in', _('Kirish')
        CHECK_OUT = 'check_out', _('Chiqish')

    class VerifyMode(models.TextChoices):
        """
        Tekshirish usullari.

        Attributes:
            FACE: Yuz tanish
            FINGERPRINT: Barmoq izi
            CARD: RFID karta
            PASSWORD: Parol
            MIXED: Aralash
        """
        FACE = 'face', _('Yuz tanish')
        FINGERPRINT = 'fingerprint', _('Barmoq izi')
        CARD = 'card', _('RFID karta')
        PASSWORD = 'password', _('Parol')
        MIXED = 'mixed', _('Aralash')

    class MaskStatus(models.TextChoices):
        """
        Niqob holatlari.
        """
        WEARING = 'wearing', _('Niqobli')
        NOT_WEARING = 'not_wearing', _('Niqobsiz')
        UNKNOWN = 'unknown', _("Noma'lum")

    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='attendance_records',
        verbose_name=_("Hodim"),
        help_text=_("Davomat yozuvi tegishli hodim")
    )
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        verbose_name=_("Hodisa turi"),
        help_text=_("Kirish yoki chiqish")
    )
    timestamp = models.DateTimeField(
        verbose_name=_("Vaqt"),
        help_text=_("Hodisa sodir bo'lgan vaqt"),
        db_index=True
    )
    device_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Qurilma ID"),
        help_text=_("Hikvision qurilma identifikatori")
    )

    # Hikvision'dan kelgan qo'shimcha ma'lumotlar
    card_no = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Karta raqami"),
        help_text=_("RFID karta raqami")
    )
    verify_mode = models.CharField(
        max_length=20,
        choices=VerifyMode.choices,
        blank=True,
        null=True,
        verbose_name=_("Tekshirish usuli"),
        help_text=_("Qanday usulda tekshirilgan")
    )
    temperature = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(Decimal('30.0')),
            MaxValueValidator(Decimal('45.0'))
        ],
        verbose_name=_("Harorat"),
        help_text=_("Tana harorati (°C)")
    )
    mask_status = models.CharField(
        max_length=20,
        choices=MaskStatus.choices,
        blank=True,
        null=True,
        verbose_name=_("Niqob holati"),
        help_text=_("Niqob taqilgan yoki yo'q")
    )
    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(Decimal('0')),
            MaxValueValidator(Decimal('100'))
        ],
        verbose_name=_("Ishonchlilik"),
        help_text=_("Tanib olish ishonchliligi (%)")
    )
    raw_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("Xom ma'lumot"),
        help_text=_("Qurilmadan kelgan to'liq JSON ma'lumot")
    )
    photo_snapshot = models.ImageField(
        upload_to='attendance/snapshots/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name=_("Rasm"),
        help_text=_("Kirish/chiqish vaqtidagi rasm")
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Yaratilgan vaqt")
    )

    class Meta:
        verbose_name = _("Davomat yozuvi")
        verbose_name_plural = _("Davomat yozuvlari")
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['employee', 'timestamp'], name='att_emp_time_idx'),
            models.Index(fields=['timestamp'], name='att_timestamp_idx'),
            models.Index(fields=['event_type'], name='att_event_idx'),
            models.Index(fields=['device_id'], name='att_device_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'timestamp', 'device_id'],
                name='unique_attendance_record'
            )
        ]

    def __str__(self) -> str:
        """
        Yozuvni string sifatida qaytarish.

        Returns:
            str: Hodim, hodisa turi va vaqt
        """
        return f"{self.employee} - {self.get_event_type_display()} - {self.timestamp}"

    def __repr__(self) -> str:
        """
        Debug uchun to'liq ma'lumot.

        Returns:
            str: Model va asosiy ma'lumotlar
        """
        return (
            f"<AttendanceRecord(id={self.pk}, emp='{self.employee.employee_id}', "
            f"type='{self.event_type}', time='{self.timestamp}')>"
        )

    @property
    def date(self) -> date:
        """
        Yozuv sanasini qaytarish.

        Returns:
            date: Faqat sana qismi
        """
        return self.timestamp.date()

    @property
    def time(self) -> time:
        """
        Yozuv vaqtini qaytarish.

        Returns:
            time: Faqat vaqt qismi
        """
        return self.timestamp.time()

    @property
    def is_check_in(self) -> bool:
        """
        Kirish hodisasi ekanligini tekshirish.

        Returns:
            bool: True agar kirish bo'lsa
        """
        return self.event_type == self.EventType.CHECK_IN

    @property
    def is_check_out(self) -> bool:
        """
        Chiqish hodisasi ekanligini tekshirish.

        Returns:
            bool: True agar chiqish bo'lsa
        """
        return self.event_type == self.EventType.CHECK_OUT

    def clean(self) -> None:
        """
        Model validatsiyasi.

        Raises:
            ValidationError: Noto'g'ri ma'lumotlar bo'lsa
        """
        if self.timestamp and self.timestamp > timezone.now():
            raise ValidationError({
                'timestamp': _("Vaqt kelajakda bo'lishi mumkin emas")
            })


class DailyAttendance(models.Model):
    """
    Kunlik davomat xulosasi.

    Har bir hodim uchun har kuni bitta yozuv yaratiladi.
    Kirish/chiqish vaqtlari, kechikish, erta ketish hisob-kitoblari.

    Attributes:
        employee (Employee): Hodim
        date (date): Sana
        first_check_in (datetime): Birinchi kirish vaqti
        last_check_out (datetime): Oxirgi chiqish vaqti
        scheduled_start (time): Rejalashtirilgan boshlanish
        scheduled_end (time): Rejalashtirilgan tugash
        late_minutes (int): Kechikish daqiqalari
        early_leave_minutes (int): Erta ketish daqiqalari
        overtime_minutes (int): Qo'shimcha ish daqiqalari
        total_work_minutes (int): Jami ish vaqti
        status (str): Davomat holati
        notes (str): Izohlar
        approved_by (User): Tasdiqlagan foydalanuvchi
        approved_at (datetime): Tasdiqlangan vaqt

    Properties:
        work_hours: Ish soatlari (soat:daqiqa formatida)
        is_late: Kechikkanmi
        is_early_leave: Erta ketganmi

    Example:
        >>> daily = DailyAttendance.objects.get(employee=emp, date=today)
        >>> daily.status
        'late'
        >>> daily.work_hours
        '7:45'
    """

    class Status(models.TextChoices):
        """
        Davomat holatlari.

        Attributes:
            PRESENT: Kelgan (vaqtida)
            ABSENT: Kelmagan
            LATE: Kechikkan
            EARLY_LEAVE: Erta ketgan
            LATE_AND_EARLY: Kechikkan va erta ketgan
            HALF_DAY: Yarim kun
            ON_LEAVE: Ta'tilda
            HOLIDAY: Dam olish kuni
            SICK_LEAVE: Kasallik ta'tili
            REMOTE: Masofadan ishlash
        """
        PRESENT = 'present', _('Kelgan')
        ABSENT = 'absent', _('Kelmagan')
        LATE = 'late', _('Kechikkan')
        EARLY_LEAVE = 'early_leave', _('Erta ketgan')
        LATE_AND_EARLY = 'late_and_early', _('Kechikkan va erta ketgan')
        HALF_DAY = 'half_day', _('Yarim kun')
        ON_LEAVE = 'on_leave', _("Ta'tilda")
        HOLIDAY = 'holiday', _('Dam olish kuni')
        SICK_LEAVE = 'sick_leave', _('Kasallik')
        REMOTE = 'remote', _('Masofadan')

    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='daily_attendances',
        verbose_name=_("Hodim"),
        help_text=_("Davomat tegishli hodim")
    )
    date = models.DateField(
        verbose_name=_("Sana"),
        help_text=_("Davomat sanasi"),
        db_index=True
    )

    # Kirish/Chiqish vaqtlari
    first_check_in = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Birinchi kirish"),
        help_text=_("Shu kundagi birinchi kirish vaqti")
    )
    last_check_out = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Oxirgi chiqish"),
        help_text=_("Shu kundagi oxirgi chiqish vaqti")
    )

    # Ish vaqti (shu kun uchun)
    scheduled_start = models.TimeField(
        verbose_name=_("Rejalashtirilgan boshlanish"),
        help_text=_("Ish boshlanishi kerak bo'lgan vaqt")
    )
    scheduled_end = models.TimeField(
        verbose_name=_("Rejalashtirilgan tugash"),
        help_text=_("Ish tugashi kerak bo'lgan vaqt")
    )

    # Hisoblangan qiymatlar
    late_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Kechikish (daqiqa)"),
        help_text=_("Necha daqiqa kechikkan")
    )
    early_leave_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Erta ketish (daqiqa)"),
        help_text=_("Necha daqiqa erta ketgan")
    )
    overtime_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Qo'shimcha ish (daqiqa)"),
        help_text=_("Qo'shimcha ishlangan daqiqalar")
    )
    total_work_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Jami ish vaqti (daqiqa)"),
        help_text=_("Umumiy ishlangan daqiqalar")
    )

    # Holat
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ABSENT,
        verbose_name=_("Holat"),
        help_text=_("Davomat holati")
    )

    # Qo'shimcha ma'lumotlar
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Izoh"),
        help_text=_("Qo'shimcha izohlar")
    )
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='approved_attendances',
        verbose_name=_("Tasdiqlagan"),
        help_text=_("Kim tasdiqlagan")
    )
    approved_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Tasdiqlangan vaqt")
    )

    # Vaqt belgilari
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Yaratilgan vaqt")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("O'zgartirilgan vaqt")
    )

    class Meta:
        verbose_name = _("Kunlik davomat")
        verbose_name_plural = _("Kunlik davomatlar")
        ordering = ['-date', 'employee']
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'date'],
                name='unique_daily_attendance'
            )
        ]
        indexes = [
            models.Index(fields=['date'], name='daily_date_idx'),
            models.Index(fields=['employee', 'date'], name='daily_emp_date_idx'),
            models.Index(fields=['status'], name='daily_status_idx'),
        ]

    def __str__(self) -> str:
        """
        Kunlik davomatni string sifatida qaytarish.

        Returns:
            str: Hodim, sana va holat
        """
        return f"{self.employee} - {self.date} - {self.get_status_display()}"

    def __repr__(self) -> str:
        """
        Debug uchun to'liq ma'lumot.

        Returns:
            str: Model va asosiy ma'lumotlar
        """
        return (
            f"<DailyAttendance(id={self.pk}, emp='{self.employee.employee_id}', "
            f"date='{self.date}', status='{self.status}')>"
        )

    @property
    def work_hours(self) -> str:
        """
        Ish soatlarini soat:daqiqa formatida qaytarish.

        Returns:
            str: "7:45" formatida

        Example:
            >>> daily.work_hours
            '8:30'
        """
        hours = self.total_work_minutes // 60
        minutes = self.total_work_minutes % 60
        return f"{hours}:{minutes:02d}"

    @property
    def is_late(self) -> bool:
        """
        Hodim kechikkanligini tekshirish.

        Returns:
            bool: True agar kechikkan bo'lsa
        """
        return self.late_minutes > 0

    @property
    def is_early_leave(self) -> bool:
        """
        Hodim erta ketganligini tekshirish.

        Returns:
            bool: True agar erta ketgan bo'lsa
        """
        return self.early_leave_minutes > 0

    @property
    def has_overtime(self) -> bool:
        """
        Qo'shimcha ish borligini tekshirish.

        Returns:
            bool: True agar overtime mavjud bo'lsa
        """
        return self.overtime_minutes > 0

    @property
    def is_approved(self) -> bool:
        """
        Davomat tasdiqlangan yoki yo'qligini tekshirish.

        Returns:
            bool: True agar tasdiqlangan bo'lsa
        """
        return self.approved_by is not None

    def calculate_late_minutes(self) -> int:
        """
        Kechikish daqiqalarini hisoblash.

        Returns:
            int: Kechikish daqiqalari (0 dan kam bo'lmaydi)

        Note:
            Agar hodim kirish vaqtidan keyin kelgan bo'lsa,
            kechikish daqiqalari hisoblanadi.
        """
        if not self.first_check_in:
            return 0

        scheduled_start_dt = timezone.make_aware(
            datetime.combine(self.date, self.scheduled_start)
        )

        if self.first_check_in > scheduled_start_dt:
            diff = self.first_check_in - scheduled_start_dt
            return int(diff.total_seconds() / 60)
        return 0

    def calculate_early_leave_minutes(self) -> int:
        """
        Erta ketish daqiqalarini hisoblash.

        Returns:
            int: Erta ketish daqiqalari (0 dan kam bo'lmaydi)

        Note:
            Agar hodim chiqish vaqtidan oldin ketgan bo'lsa,
            erta ketish daqiqalari hisoblanadi.
        """
        if not self.last_check_out:
            return 0

        scheduled_end_dt = timezone.make_aware(
            datetime.combine(self.date, self.scheduled_end)
        )

        if self.last_check_out < scheduled_end_dt:
            diff = scheduled_end_dt - self.last_check_out
            return int(diff.total_seconds() / 60)
        return 0

    def calculate_overtime_minutes(self) -> int:
        """
        Qo'shimcha ish vaqtini hisoblash.

        Returns:
            int: Overtime daqiqalari (0 dan kam bo'lmaydi)

        Note:
            Agar hodim chiqish vaqtidan keyin ishlagan bo'lsa,
            qo'shimcha ish daqiqalari hisoblanadi.
        """
        if not self.last_check_out:
            return 0

        scheduled_end_dt = timezone.make_aware(
            datetime.combine(self.date, self.scheduled_end)
        )

        if self.last_check_out > scheduled_end_dt:
            diff = self.last_check_out - scheduled_end_dt
            return int(diff.total_seconds() / 60)
        return 0

    def calculate_total_work_minutes(self) -> int:
        """
        Jami ish vaqtini hisoblash.

        Returns:
            int: Umumiy ishlangan daqiqalar

        Note:
            Birinchi kirish va oxirgi chiqish orasidagi vaqt.
        """
        if not self.first_check_in or not self.last_check_out:
            return 0

        diff = self.last_check_out - self.first_check_in
        return max(0, int(diff.total_seconds() / 60))

    def calculate_status(self) -> str:
        """
        Davomat holatini hisoblash.

        Returns:
            str: Status qiymati

        Note:
            Kechikish va erta ketish asosida holat aniqlanadi.
        """
        if not self.first_check_in:
            return self.Status.ABSENT

        is_late = self.late_minutes > 0
        is_early = self.early_leave_minutes > 0

        if is_late and is_early:
            return self.Status.LATE_AND_EARLY
        elif is_late:
            return self.Status.LATE
        elif is_early:
            return self.Status.EARLY_LEAVE
        else:
            return self.Status.PRESENT

    def recalculate(self, save: bool = True) -> None:
        """
        Barcha qiymatlarni qayta hisoblash.

        Args:
            save: True bo'lsa, o'zgarishlarni saqlaydi

        Side Effects:
            late_minutes, early_leave_minutes, overtime_minutes,
            total_work_minutes va status maydonlari yangilanadi.
        """
        self.late_minutes = self.calculate_late_minutes()
        self.early_leave_minutes = self.calculate_early_leave_minutes()
        self.overtime_minutes = self.calculate_overtime_minutes()
        self.total_work_minutes = self.calculate_total_work_minutes()
        self.status = self.calculate_status()

        if save:
            self.save()

    def approve(self, user, notes: str = None) -> None:
        """
        Davomatni tasdiqlash.

        Args:
            user: Tasdiqlovchi foydalanuvchi
            notes: Qo'shimcha izoh

        Side Effects:
            approved_by va approved_at maydonlari o'zgaradi
        """
        self.approved_by = user
        self.approved_at = timezone.now()
        if notes:
            self.notes = f"{self.notes or ''}\n\nTasdiqlash izohi: {notes}".strip()
        self.save()

    def get_attendance_records(self) -> models.QuerySet:
        """
        Shu kun uchun barcha kirish/chiqish yozuvlarini olish.

        Returns:
            QuerySet: AttendanceRecord yozuvlari
        """
        return AttendanceRecord.objects.filter(
            employee=self.employee,
            timestamp__date=self.date
        ).order_by('timestamp')


class WorkSchedule(models.Model):
    """
    Ish jadvali sozlamalari.

    Turli xil ish jadvallarini belgilash uchun ishlatiladi.
    Har bir hodim yoki bo'limga alohida jadval tayinlanishi mumkin.

    Attributes:
        name (str): Jadval nomi
        code (str): Jadval kodi
        start_time (time): Ish boshlanish vaqti
        end_time (time): Ish tugash vaqti
        late_threshold_minutes (int): Kechikish chegarasi
        early_leave_threshold_minutes (int): Erta ketish chegarasi
        break_start (time): Tushlik boshlanishi
        break_end (time): Tushlik tugashi
        working_days (list): Ish kunlari
        is_default (bool): Standart jadval
        is_active (bool): Jadval faol yoki yo'q

    Properties:
        total_work_hours: Kunlik ish soatlari
        break_duration: Tushlik davomiyligi

    Example:
        >>> schedule = WorkSchedule.objects.get(is_default=True)
        >>> schedule.total_work_hours
        8.0
    """

    class WeekDay(models.IntegerChoices):
        """
        Hafta kunlari.
        """
        MONDAY = 0, _('Dushanba')
        TUESDAY = 1, _('Seshanba')
        WEDNESDAY = 2, _('Chorshanba')
        THURSDAY = 3, _('Payshanba')
        FRIDAY = 4, _('Juma')
        SATURDAY = 5, _('Shanba')
        SUNDAY = 6, _('Yakshanba')

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Jadval nomi"),
        help_text=_("Ish jadvalining nomi")
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Jadval kodi"),
        help_text=_("Qisqa identifikator")
    )
    start_time = models.TimeField(
        verbose_name=_("Boshlanish vaqti"),
        help_text=_("Ish kunining boshlanish vaqti")
    )
    end_time = models.TimeField(
        verbose_name=_("Tugash vaqti"),
        help_text=_("Ish kunining tugash vaqti")
    )
    late_threshold_minutes = models.PositiveIntegerField(
        default=5,
        validators=[MaxValueValidator(60)],
        verbose_name=_("Kechikish chegarasi (daqiqa)"),
        help_text=_("Necha daqiqadan keyin kechikish hisoblanadi")
    )
    early_leave_threshold_minutes = models.PositiveIntegerField(
        default=5,
        validators=[MaxValueValidator(60)],
        verbose_name=_("Erta ketish chegarasi (daqiqa)"),
        help_text=_("Necha daqiqadan keyin erta ketish hisoblanadi")
    )
    break_start = models.TimeField(
        blank=True,
        null=True,
        verbose_name=_("Tushlik boshlanishi"),
        help_text=_("Tushlik tanaffusi boshlanish vaqti")
    )
    break_end = models.TimeField(
        blank=True,
        null=True,
        verbose_name=_("Tushlik tugashi"),
        help_text=_("Tushlik tanaffusi tugash vaqti")
    )
    working_days = models.JSONField(
        default=list,
        verbose_name=_("Ish kunlari"),
        help_text=_("Ish kunlari ro'yxati (0-6: Dushanba-Yakshanba)")
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("Standart jadval"),
        help_text=_("Yangi hodimlar uchun standart jadval")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Faol"),
        help_text=_("Jadval faol yoki arxivlangan")
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Yaratilgan vaqt")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("O'zgartirilgan vaqt")
    )

    class Meta:
        verbose_name = _("Ish jadvali")
        verbose_name_plural = _("Ish jadvallari")
        ordering = ['name']

    def __str__(self) -> str:
        """
        Jadvalni string sifatida qaytarish.

        Returns:
            str: Jadval nomi va vaqtlari
        """
        return f"{self.name} ({self.start_time} - {self.end_time})"

    def __repr__(self) -> str:
        """
        Debug uchun to'liq ma'lumot.

        Returns:
            str: Model va asosiy ma'lumotlar
        """
        return (
            f"<WorkSchedule(id={self.pk}, name='{self.name}', "
            f"start='{self.start_time}', end='{self.end_time}')>"
        )

    @property
    def total_work_hours(self) -> float:
        """
        Kunlik ish soatlarini hisoblash.

        Returns:
            float: Ish soatlari (tushliksiz)

        Example:
            >>> schedule.total_work_hours
            8.0
        """
        start_dt = datetime.combine(date.today(), self.start_time)
        end_dt = datetime.combine(date.today(), self.end_time)
        total_minutes = (end_dt - start_dt).total_seconds() / 60

        # Tushlikni ayirish
        if self.break_start and self.break_end:
            total_minutes -= self.break_duration_minutes

        return round(total_minutes / 60, 2)

    @property
    def break_duration_minutes(self) -> int:
        """
        Tushlik davomiyligini daqiqalarda qaytarish.

        Returns:
            int: Tushlik davomiyligi (daqiqa)
        """
        if not self.break_start or not self.break_end:
            return 0

        break_start_dt = datetime.combine(date.today(), self.break_start)
        break_end_dt = datetime.combine(date.today(), self.break_end)
        return int((break_end_dt - break_start_dt).total_seconds() / 60)

    def is_working_day(self, check_date: date) -> bool:
        """
        Berilgan sana ish kuni ekanligini tekshirish.

        Args:
            check_date: Tekshiriladigan sana

        Returns:
            bool: True agar ish kuni bo'lsa
        """
        if not self.working_days:
            # Default: Dushanba-Juma
            return check_date.weekday() < 5
        return check_date.weekday() in self.working_days

    def save(self, *args, **kwargs) -> None:
        """
        Jadval saqlash.

        Note:
            Agar is_default=True bo'lsa, boshqa jadvallar
            default emas qilib belgilanadi.
        """
        if self.is_default:
            WorkSchedule.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def clean(self) -> None:
        """
        Model validatsiyasi.

        Raises:
            ValidationError: Noto'g'ri vaqtlar bo'lsa
        """
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError({
                    'end_time': _("Tugash vaqti boshlanish vaqtidan keyin bo'lishi kerak")
                })

        if self.break_start and self.break_end:
            if self.break_start >= self.break_end:
                raise ValidationError({
                    'break_end': _("Tushlik tugashi boshlanishidan keyin bo'lishi kerak")
                })


class Holiday(models.Model):
    """
    Bayram va dam olish kunlari.

    Rasmiy dam olish kunlari va kompaniya bayramlari.

    Attributes:
        name (str): Bayram nomi
        date (date): Sana
        holiday_type (str): Bayram turi
        is_recurring (bool): Har yili takrorlanadimi
        description (str): Tavsif

    Example:
        >>> holiday = Holiday.objects.create(
        ...     name="Yangi yil",
        ...     date=date(2024, 1, 1),
        ...     holiday_type='national'
        ... )
    """

    class HolidayType(models.TextChoices):
        """
        Bayram turlari.
        """
        NATIONAL = 'national', _('Milliy bayram')
        RELIGIOUS = 'religious', _('Diniy bayram')
        COMPANY = 'company', _('Kompaniya bayram')
        OTHER = 'other', _('Boshqa')

    name = models.CharField(
        max_length=100,
        verbose_name=_("Bayram nomi"),
        help_text=_("Dam olish kunining nomi")
    )
    date = models.DateField(
        verbose_name=_("Sana"),
        help_text=_("Dam olish kuni sanasi")
    )
    holiday_type = models.CharField(
        max_length=20,
        choices=HolidayType.choices,
        default=HolidayType.NATIONAL,
        verbose_name=_("Bayram turi")
    )
    is_recurring = models.BooleanField(
        default=False,
        verbose_name=_("Har yili takrorlanadi"),
        help_text=_("Bu bayram har yili bir xil sanada bo'ladimi")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Tavsif")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Yaratilgan vaqt")
    )

    class Meta:
        verbose_name = _("Dam olish kuni")
        verbose_name_plural = _("Dam olish kunlari")
        ordering = ['date']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'date'],
                name='unique_holiday'
            )
        ]

    def __str__(self) -> str:
        """
        Bayramni string sifatida qaytarish.

        Returns:
            str: Bayram nomi va sanasi
        """
        return f"{self.name} ({self.date})"

    @classmethod
    def is_holiday(cls, check_date: date) -> bool:
        """
        Berilgan sana dam olish kuni ekanligini tekshirish.

        Args:
            check_date: Tekshiriladigan sana

        Returns:
            bool: True agar dam olish kuni bo'lsa
        """
        return cls.objects.filter(date=check_date).exists()


class LeaveRequest(models.Model):
    """
    Ta'til so'rovlari modeli.

    Hodimlarning ta'til, kasallik va boshqa so'rovlarini boshqarish.

    Attributes:
        employee (Employee): Hodim
        leave_type (str): Ta'til turi
        start_date (date): Boshlanish sanasi
        end_date (date): Tugash sanasi
        reason (str): Sabab
        status (str): So'rov holati
        approved_by (User): Tasdiqlagan
        approved_at (datetime): Tasdiqlangan vaqt
        rejection_reason (str): Rad etish sababi

    Properties:
        total_days: Jami kunlar
        is_approved: Tasdiqlangan yoki yo'q
        is_pending: Kutilmoqda yoki yo'q

    Example:
        >>> leave = LeaveRequest.objects.create(
        ...     employee=emp,
        ...     leave_type='annual',
        ...     start_date=date(2024, 7, 1),
        ...     end_date=date(2024, 7, 14),
        ...     reason="Oilaviy dam olish"
        ... )
    """

    class LeaveType(models.TextChoices):
        """
        Ta'til turlari.
        """
        ANNUAL = 'annual', _("Yillik ta'til")
        SICK = 'sick', _('Kasallik')
        UNPAID = 'unpaid', _("Haq to'lanmaydigan")
        MATERNITY = 'maternity', _('Dekret')
        PATERNITY = 'paternity', _("Otalik ta'tili")
        BEREAVEMENT = 'bereavement', _('Motam')
        OTHER = 'other', _('Boshqa')

    class Status(models.TextChoices):
        """
        So'rov holatlari.
        """
        PENDING = 'pending', _('Kutilmoqda')
        APPROVED = 'approved', _('Tasdiqlangan')
        REJECTED = 'rejected', _('Rad etilgan')
        CANCELLED = 'cancelled', _('Bekor qilingan')

    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='leave_requests',
        verbose_name=_("Hodim")
    )
    leave_type = models.CharField(
        max_length=20,
        choices=LeaveType.choices,
        verbose_name=_("Ta'til turi")
    )
    start_date = models.DateField(
        verbose_name=_("Boshlanish sanasi")
    )
    end_date = models.DateField(
        verbose_name=_("Tugash sanasi")
    )
    reason = models.TextField(
        verbose_name=_("Sabab"),
        help_text=_("Ta'til olish sababi")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Holat")
    )
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='approved_leaves',
        verbose_name=_("Tasdiqlagan")
    )
    approved_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Tasdiqlangan vaqt")
    )
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Rad etish sababi")
    )
    attachment = models.FileField(
        upload_to='leave_requests/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_("Ilova"),
        help_text=_("Qo'shimcha hujjat (kasallik varaqasi va h.k.)")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Yaratilgan vaqt")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("O'zgartirilgan vaqt")
    )

    class Meta:
        verbose_name = _("Ta'til so'rovi")
        verbose_name_plural = _("Ta'til so'rovlari")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'status'], name='leave_emp_status_idx'),
            models.Index(fields=['start_date', 'end_date'], name='leave_dates_idx'),
        ]

    def __str__(self) -> str:
        """
        So'rovni string sifatida qaytarish.

        Returns:
            str: Hodim, tur va sanalar
        """
        return f"{self.employee.short_name} - {self.get_leave_type_display()} ({self.start_date} - {self.end_date})"

    @property
    def total_days(self) -> int:
        """
        Jami ta'til kunlarini hisoblash.

        Returns:
            int: Kunlar soni
        """
        return (self.end_date - self.start_date).days + 1

    @property
    def is_approved(self) -> bool:
        """
        So'rov tasdiqlangan yoki yo'qligini tekshirish.

        Returns:
            bool: True agar tasdiqlangan bo'lsa
        """
        return self.status == self.Status.APPROVED

    @property
    def is_pending(self) -> bool:
        """
        So'rov kutilmoqda yoki yo'qligini tekshirish.

        Returns:
            bool: True agar kutilmoqda bo'lsa
        """
        return self.status == self.Status.PENDING

    def approve(self, user, notes: str = None) -> None:
        """
        So'rovni tasdiqlash.

        Args:
            user: Tasdiqlovchi foydalanuvchi
            notes: Qo'shimcha izoh

        Raises:
            ValidationError: Allaqachon qaror qilingan bo'lsa
        """
        if self.status != self.Status.PENDING:
            raise ValidationError(_("Bu so'rovga allaqachon qaror qilingan"))

        self.status = self.Status.APPROVED
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()

        # DailyAttendance yozuvlarini yaratish
        self._create_attendance_records()

    def reject(self, user, reason: str) -> None:
        """
        So'rovni rad etish.

        Args:
            user: Rad etuvchi foydalanuvchi
            reason: Rad etish sababi

        Raises:
            ValidationError: Allaqachon qaror qilingan bo'lsa
        """
        if self.status != self.Status.PENDING:
            raise ValidationError(_("Bu so'rovga allaqachon qaror qilingan"))

        self.status = self.Status.REJECTED
        self.approved_by = user
        self.approved_at = timezone.now()
        self.rejection_reason = reason
        self.save()

    def cancel(self) -> None:
        """
        So'rovni bekor qilish.

        Raises:
            ValidationError: Allaqachon bajarilgan bo'lsa
        """
        if self.status == self.Status.APPROVED and self.start_date <= timezone.now().date():
            raise ValidationError(_("Boshlangan ta'tilni bekor qilib bo'lmaydi"))

        self.status = self.Status.CANCELLED
        self.save()

    def _create_attendance_records(self) -> None:
        """
        Ta'til kunlari uchun DailyAttendance yozuvlarini yaratish.

        Side Effects:
            DailyAttendance yozuvlari yaratiladi
        """
        current_date = self.start_date
        status_map = {
            self.LeaveType.SICK: DailyAttendance.Status.SICK_LEAVE,
            self.LeaveType.ANNUAL: DailyAttendance.Status.ON_LEAVE,
        }
        attendance_status = status_map.get(
            self.leave_type,
            DailyAttendance.Status.ON_LEAVE
        )

        while current_date <= self.end_date:
            DailyAttendance.objects.update_or_create(
                employee=self.employee,
                date=current_date,
                defaults={
                    'status': attendance_status,
                    'scheduled_start': self.employee.work_start_time,
                    'scheduled_end': self.employee.work_end_time,
                    'notes': f"Ta'til so'rovi #{self.pk}"
                }
            )
            current_date += timedelta(days=1)

    def clean(self) -> None:
        """
        Model validatsiyasi.

        Raises:
            ValidationError: Noto'g'ri sanalar bo'lsa
        """
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError({
                    'end_date': _("Tugash sanasi boshlanish sanasidan keyin bo'lishi kerak")
                })

            if self.start_date < timezone.now().date():
                raise ValidationError({
                    'start_date': _("O'tgan sanaga ta'til so'rovi yaratib bo'lmaydi")
                })
