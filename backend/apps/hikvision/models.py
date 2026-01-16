"""
Hikvision Application Models.

Bu modul Hikvision qurilmalarini boshqarish va sinxronizatsiya
jarayonlarini kuzatish uchun modellarni o'z ichiga oladi.

Models:
    - HikvisionDevice: Qurilma ma'lumotlari va sozlamalari
    - SyncLog: Sinxronizatsiya loglari
    - DeviceCommand: Qurilmaga yuborilgan buyruqlar

Example:
    >>> from apps.hikvision.models import HikvisionDevice
    >>> device = HikvisionDevice.objects.create(
    ...     name="Asosiy kirish",
    ...     ip_address="192.168.1.100",
    ...     username="admin",
    ...     password="password123"
    ... )
    >>> device.test_connection()
    True
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import timedelta
from typing import Optional


class HikvisionDevice(models.Model):
    """
    Hikvision qurilma modeli.

    Hikvision DS-K1T343EFWX va boshqa turli modellarni qo'llab-quvvatlaydi.
    Qurilma bilan bog'lanish uchun barcha zarur sozlamalar saqlanadi.

    Attributes:
        name (str): Qurilma nomi
        ip_address (str): IP manzili
        port (int): Port raqami
        username (str): Login
        password (str): Parol
        serial_number (str): Seriya raqami
        model (str): Qurilma modeli
        firmware_version (str): Firmware versiyasi
        location (str): Joylashuv
        description (str): Tavsif
        device_type (str): Qurilma turi
        status (str): Joriy holat
        last_sync (datetime): Oxirgi sinxronizatsiya
        last_heartbeat (datetime): Oxirgi bog'lanish
        sync_interval_minutes (int): Sinxronizatsiya oralig'i
        is_active (bool): Faol yoki yo'q
        auto_sync_enabled (bool): Avtomatik sinxronizatsiya

    Properties:
        base_url: Qurilma API URL
        is_online: Online yoki yo'q
        sync_overdue: Sinxronizatsiya kechikkanmi

    Example:
        >>> device = HikvisionDevice.objects.get(name="Asosiy kirish")
        >>> device.is_online
        True
        >>> device.base_url
        'http://192.168.1.100:80'
    """

    class Status(models.TextChoices):
        """
        Qurilma holatlari.

        Attributes:
            ONLINE: Qurilma ishlayapti va bog'lanish mavjud
            OFFLINE: Qurilma bilan bog'lanish yo'q
            ERROR: Xatolik yuz berdi
            MAINTENANCE: Texnik xizmat ko'rsatish
            SYNCING: Sinxronizatsiya jarayonida
        """
        ONLINE = 'online', _('Online')
        OFFLINE = 'offline', _('Offline')
        ERROR = 'error', _('Xatolik')
        MAINTENANCE = 'maintenance', _('Texnik xizmat')
        SYNCING = 'syncing', _('Sinxronizatsiya')

    class DeviceType(models.TextChoices):
        """
        Qurilma turlari.

        Attributes:
            FACE_TERMINAL: Yuz tanish terminali
            FINGERPRINT: Barmoq izi skaneri
            CARD_READER: Karta o'quvchi
            MIXED: Aralash qurilma
        """
        FACE_TERMINAL = 'face_terminal', _('Yuz tanish terminali')
        FINGERPRINT = 'fingerprint', _('Barmoq izi skaneri')
        CARD_READER = 'card_reader', _('Karta o\'quvchi')
        MIXED = 'mixed', _('Aralash')

    # Tashkilot bog'lanishi
    branch = models.ForeignKey(
        'core.Branch',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='devices',
        verbose_name=_("Filial"),
        help_text=_("Qurilma o'rnatilgan filial")
    )

    # Asosiy ma'lumotlar
    name = models.CharField(
        max_length=100,
        verbose_name=_("Qurilma nomi"),
        help_text=_("Qurilmaning identifikatsiya uchun nomi")
    )
    ip_address = models.GenericIPAddressField(
        verbose_name=_("IP manzil"),
        help_text=_("Qurilmaning tarmoqdagi IP manzili")
    )
    port = models.PositiveIntegerField(
        default=80,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(65535)
        ],
        verbose_name=_("Port"),
        help_text=_("HTTP port raqami (standart: 80)")
    )

    # Autentifikatsiya
    username = models.CharField(
        max_length=50,
        verbose_name=_("Login"),
        help_text=_("Qurilmaga kirish uchun foydalanuvchi nomi")
    )
    password = models.CharField(
        max_length=100,
        verbose_name=_("Parol"),
        help_text=_("Qurilmaga kirish paroli")
    )

    # Qurilma ma'lumotlari
    serial_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_("Seriya raqami"),
        help_text=_("Qurilmaning zavod seriya raqami")
    )
    model = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Model"),
        help_text=_("Qurilma modeli (masalan: DS-K1T343EFWX)")
    )
    firmware_version = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Firmware versiyasi"),
        help_text=_("Qurilma dasturiy ta'minot versiyasi")
    )
    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.FACE_TERMINAL,
        verbose_name=_("Qurilma turi"),
        help_text=_("Qurilma texnologiyasi")
    )

    # Joylashuv va tavsif
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Joylashuv"),
        help_text=_("Qurilma o'rnatilgan joy")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Tavsif"),
        help_text=_("Qo'shimcha ma'lumotlar")
    )

    # Holat va sinxronizatsiya
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OFFLINE,
        verbose_name=_("Holat"),
        help_text=_("Qurilmaning joriy holati")
    )
    last_sync = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Oxirgi sinxronizatsiya"),
        help_text=_("Ma'lumotlar oxirgi marta sinxronlangan vaqt")
    )
    last_heartbeat = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Oxirgi bog'lanish"),
        help_text=_("Qurilma bilan oxirgi muvaffaqiyatli bog'lanish")
    )
    sync_interval_minutes = models.PositiveIntegerField(
        default=15,
        validators=[MinValueValidator(5), MaxValueValidator(1440)],
        verbose_name=_("Sinxronizatsiya oralig'i (daqiqa)"),
        help_text=_("Qancha vaqt oralig'ida ma'lumotlar sinxronlanadi")
    )

    # Faollashtirish
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Faol"),
        help_text=_("Qurilma tizimda faol yoki yo'q")
    )
    auto_sync_enabled = models.BooleanField(
        default=True,
        verbose_name=_("Avtomatik sinxronizatsiya"),
        help_text=_("Avtomatik sinxronizatsiya yoqilgan yoki yo'q")
    )

    # Vaqt belgilari
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Yaratilgan vaqt")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("O'zgartirilgan vaqt")
    )

    class Meta:
        verbose_name = _("Hikvision qurilma")
        verbose_name_plural = _("Hikvision qurilmalar")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['branch'], name='hik_branch_idx'),
            models.Index(fields=['ip_address'], name='hik_ip_idx'),
            models.Index(fields=['status'], name='hik_status_idx'),
            models.Index(fields=['is_active'], name='hik_active_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['ip_address', 'port'],
                name='unique_device_endpoint'
            )
        ]

    def __str__(self) -> str:
        """
        Qurilmani string sifatida qaytarish.

        Returns:
            str: Qurilma nomi va IP manzili
        """
        return f"{self.name} ({self.ip_address})"

    def __repr__(self) -> str:
        """
        Debug uchun to'liq ma'lumot.

        Returns:
            str: Model va asosiy ma'lumotlar
        """
        return (
            f"<HikvisionDevice(id={self.pk}, name='{self.name}', "
            f"ip='{self.ip_address}', status='{self.status}')>"
        )

    @property
    def organization(self):
        """
        Tegishli tashkilotni qaytarish.

        Returns:
            Organization: Tashkilot obyekti
        """
        return self.branch.organization

    @property
    def base_url(self) -> str:
        """
        Qurilma API URL manzilini qaytarish.

        Returns:
            str: HTTP URL manzili

        Example:
            >>> device.base_url
            'http://192.168.1.100:80'
        """
        return f"http://{self.ip_address}:{self.port}"

    @property
    def is_online(self) -> bool:
        """
        Qurilma online ekanligini tekshirish.

        Returns:
            bool: True agar status ONLINE bo'lsa
        """
        return self.status == self.Status.ONLINE

    @property
    def sync_overdue(self) -> bool:
        """
        Sinxronizatsiya kechikkanligini tekshirish.

        Returns:
            bool: True agar oxirgi sinxrondan keyin belgilangan
                  vaqtdan ko'proq vaqt o'tgan bo'lsa
        """
        if not self.last_sync or not self.auto_sync_enabled:
            return False

        expected_time = self.last_sync + timedelta(minutes=self.sync_interval_minutes)
        return timezone.now() > expected_time

    @property
    def minutes_since_last_sync(self) -> Optional[int]:
        """
        Oxirgi sinxronizatsiyadan o'tgan daqiqalar.

        Returns:
            int | None: Daqiqalar soni yoki None
        """
        if not self.last_sync:
            return None
        delta = timezone.now() - self.last_sync
        return int(delta.total_seconds() / 60)

    def update_status(self, new_status: str, save: bool = True) -> None:
        """
        Qurilma holatini yangilash.

        Args:
            new_status: Yangi holat qiymati
            save: True bo'lsa, o'zgarishlarni saqlaydi

        Side Effects:
            status maydoni o'zgaradi
        """
        self.status = new_status
        if new_status == self.Status.ONLINE:
            self.last_heartbeat = timezone.now()
        if save:
            self.save(update_fields=['status', 'last_heartbeat', 'updated_at'])

    def mark_sync_complete(self, save: bool = True) -> None:
        """
        Sinxronizatsiya tugaganini belgilash.

        Args:
            save: True bo'lsa, o'zgarishlarni saqlaydi

        Side Effects:
            last_sync va status maydonlari yangilanadi
        """
        self.last_sync = timezone.now()
        self.status = self.Status.ONLINE
        if save:
            self.save(update_fields=['last_sync', 'status', 'updated_at'])

    def deactivate(self, reason: str = None) -> None:
        """
        Qurilmani o'chirish.

        Args:
            reason: O'chirish sababi (description ga qo'shiladi)

        Side Effects:
            is_active va status maydonlari o'zgaradi
        """
        self.is_active = False
        self.status = self.Status.OFFLINE
        if reason:
            self.description = f"{self.description or ''}\n\nO'chirildi: {reason}".strip()
        self.save()

    def get_recent_logs(self, limit: int = 10):
        """
        So'nggi sinxronizatsiya loglarini olish.

        Args:
            limit: Qaytariladigan yozuvlar soni

        Returns:
            QuerySet: SyncLog yozuvlari
        """
        return self.sync_logs.all()[:limit]

    def clean(self) -> None:
        """
        Model validatsiyasi.

        Raises:
            ValidationError: Noto'g'ri ma'lumotlar bo'lsa
        """
        if self.ip_address:
            # IPv4 formatini tekshirish
            parts = str(self.ip_address).split('.')
            if len(parts) == 4:
                try:
                    for part in parts:
                        if not 0 <= int(part) <= 255:
                            raise ValidationError({
                                'ip_address': _("Noto'g'ri IP manzil formati")
                            })
                except ValueError:
                    raise ValidationError({
                        'ip_address': _("Noto'g'ri IP manzil formati")
                    })


class SyncLog(models.Model):
    """
    Sinxronizatsiya loglari modeli.

    Har bir sinxronizatsiya jarayoni haqida batafsil ma'lumot saqlanadi.
    Muvaffaqiyatli va muvaffaqiyatsiz urinishlar kuzatiladi.

    Attributes:
        device (HikvisionDevice): Sinxronizatsiya qilingan qurilma
        started_at (datetime): Boshlangan vaqt
        finished_at (datetime): Tugagan vaqt
        status (str): Sinxronizatsiya holati
        records_fetched (int): Qurilmadan olingan yozuvlar soni
        records_processed (int): Muvaffaqiyatli qayta ishlangan yozuvlar
        records_failed (int): Xatolik bilan yakunlangan yozuvlar
        sync_type (str): Sinxronizatsiya turi
        error_message (str): Xatolik xabari
        error_details (JSON): Batafsil xatolik ma'lumotlari
        triggered_by (str): Kim/nima tomonidan boshlangan

    Properties:
        duration_seconds: Davomiyligi (soniyalarda)
        success_rate: Muvaffaqiyat foizi
        is_successful: Muvaffaqiyatli yakunlangan yoki yo'q

    Example:
        >>> log = SyncLog.objects.filter(device=device).first()
        >>> log.success_rate
        98.5
        >>> log.duration_seconds
        45
    """

    class Status(models.TextChoices):
        """
        Sinxronizatsiya holatlari.

        Attributes:
            PENDING: Kutilmoqda
            IN_PROGRESS: Jarayonda
            SUCCESS: Muvaffaqiyatli
            PARTIAL: Qisman muvaffaqiyatli
            FAILED: Xatolik
            CANCELLED: Bekor qilingan
        """
        PENDING = 'pending', _('Kutilmoqda')
        IN_PROGRESS = 'in_progress', _('Jarayonda')
        SUCCESS = 'success', _('Muvaffaqiyatli')
        PARTIAL = 'partial', _('Qisman')
        FAILED = 'failed', _('Xatolik')
        CANCELLED = 'cancelled', _('Bekor qilingan')

    class SyncType(models.TextChoices):
        """
        Sinxronizatsiya turlari.

        Attributes:
            AUTO: Avtomatik (jadval bo'yicha)
            MANUAL: Qo'lda boshlangan
            INITIAL: Dastlabki sinxronizatsiya
            RECOVERY: Xatolikdan keyin qayta urinish
        """
        AUTO = 'auto', _('Avtomatik')
        MANUAL = 'manual', _('Qo\'lda')
        INITIAL = 'initial', _('Dastlabki')
        RECOVERY = 'recovery', _('Qayta urinish')

    device = models.ForeignKey(
        HikvisionDevice,
        on_delete=models.CASCADE,
        related_name='sync_logs',
        verbose_name=_("Qurilma"),
        help_text=_("Sinxronizatsiya qilingan qurilma")
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Boshlangan vaqt"),
        help_text=_("Sinxronizatsiya boshlangan vaqt")
    )
    finished_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Tugagan vaqt"),
        help_text=_("Sinxronizatsiya tugagan vaqt")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Holat"),
        help_text=_("Sinxronizatsiya holati")
    )

    # Statistika
    records_fetched = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Olingan yozuvlar"),
        help_text=_("Qurilmadan olingan yozuvlar soni")
    )
    records_processed = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Qayta ishlangan"),
        help_text=_("Muvaffaqiyatli qayta ishlangan yozuvlar")
    )
    records_failed = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Xatolik bilan"),
        help_text=_("Xatolik yuz bergan yozuvlar soni")
    )

    # Sinxronizatsiya turi
    sync_type = models.CharField(
        max_length=20,
        choices=SyncType.choices,
        default=SyncType.AUTO,
        verbose_name=_("Sinxronizatsiya turi"),
        help_text=_("Qanday tarzda boshlangan")
    )

    # Xatolik ma'lumotlari
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Xatolik xabari"),
        help_text=_("Xatolik haqida qisqa xabar")
    )
    error_details = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("Xatolik tafsilotlari"),
        help_text=_("Batafsil xatolik ma'lumotlari (JSON)")
    )

    # Qo'shimcha ma'lumotlar
    triggered_by = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Kim tomonidan"),
        help_text=_("Sinxronizatsiyani kim/nima boshladi")
    )
    metadata = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("Qo'shimcha ma'lumot"),
        help_text=_("Boshqa foydali ma'lumotlar")
    )

    class Meta:
        verbose_name = _("Sinxronizatsiya logi")
        verbose_name_plural = _("Sinxronizatsiya loglari")
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['device', 'started_at'], name='sync_dev_time_idx'),
            models.Index(fields=['status'], name='sync_status_idx'),
            models.Index(fields=['started_at'], name='sync_time_idx'),
        ]

    def __str__(self) -> str:
        """
        Logni string sifatida qaytarish.

        Returns:
            str: Qurilma, vaqt va holat
        """
        return f"{self.device.name} - {self.started_at} - {self.get_status_display()}"

    def __repr__(self) -> str:
        """
        Debug uchun to'liq ma'lumot.

        Returns:
            str: Model va asosiy ma'lumotlar
        """
        return (
            f"<SyncLog(id={self.pk}, device='{self.device.name}', "
            f"status='{self.status}', records={self.records_processed})>"
        )

    @property
    def duration_seconds(self) -> Optional[int]:
        """
        Sinxronizatsiya davomiyligini soniyalarda qaytarish.

        Returns:
            int | None: Davomiylik yoki None agar tugamagan bo'lsa
        """
        if not self.finished_at:
            return None
        delta = self.finished_at - self.started_at
        return int(delta.total_seconds())

    @property
    def duration_display(self) -> str:
        """
        Davomiylikni o'qishga qulay formatda qaytarish.

        Returns:
            str: "2 daqiqa 30 soniya" formatida
        """
        seconds = self.duration_seconds
        if seconds is None:
            return "-"

        if seconds < 60:
            return f"{seconds} soniya"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes} daqiqa {secs} soniya"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours} soat {minutes} daqiqa"

    @property
    def success_rate(self) -> float:
        """
        Muvaffaqiyat foizini hisoblash.

        Returns:
            float: Muvaffaqiyat foizi (0-100)

        Example:
            >>> log.success_rate
            98.5
        """
        if self.records_fetched == 0:
            return 0.0
        return round((self.records_processed / self.records_fetched) * 100, 1)

    @property
    def is_successful(self) -> bool:
        """
        Sinxronizatsiya muvaffaqiyatli yakunlanganligini tekshirish.

        Returns:
            bool: True agar status SUCCESS bo'lsa
        """
        return self.status == self.Status.SUCCESS

    @property
    def is_in_progress(self) -> bool:
        """
        Sinxronizatsiya davom etayotganligini tekshirish.

        Returns:
            bool: True agar hali tugamagan bo'lsa
        """
        return self.status in [self.Status.PENDING, self.Status.IN_PROGRESS]

    def start(self) -> None:
        """
        Sinxronizatsiyani boshlash.

        Side Effects:
            status IN_PROGRESS ga o'zgaradi
        """
        self.status = self.Status.IN_PROGRESS
        self.save(update_fields=['status'])

    def complete(
        self,
        records_fetched: int = 0,
        records_processed: int = 0,
        records_failed: int = 0
    ) -> None:
        """
        Sinxronizatsiyani muvaffaqiyatli yakunlash.

        Args:
            records_fetched: Olingan yozuvlar soni
            records_processed: Qayta ishlangan yozuvlar
            records_failed: Xatolik bilan yakunlangan yozuvlar

        Side Effects:
            status, finished_at va statistika maydonlari yangilanadi
        """
        self.finished_at = timezone.now()
        self.records_fetched = records_fetched
        self.records_processed = records_processed
        self.records_failed = records_failed

        if records_failed == 0 and records_fetched > 0:
            self.status = self.Status.SUCCESS
        elif records_processed > 0:
            self.status = self.Status.PARTIAL
        else:
            self.status = self.Status.FAILED

        self.save()

        # Qurilma holatini yangilash
        self.device.mark_sync_complete()

    def fail(self, error_message: str, error_details: dict = None) -> None:
        """
        Sinxronizatsiyani xatolik bilan yakunlash.

        Args:
            error_message: Xatolik xabari
            error_details: Batafsil ma'lumotlar (dict)

        Side Effects:
            status FAILED ga o'zgaradi, xatolik ma'lumotlari saqlanadi
        """
        self.finished_at = timezone.now()
        self.status = self.Status.FAILED
        self.error_message = error_message
        self.error_details = error_details
        self.save()

        # Qurilma holatini yangilash
        self.device.update_status(HikvisionDevice.Status.ERROR)

    def cancel(self) -> None:
        """
        Sinxronizatsiyani bekor qilish.

        Side Effects:
            status CANCELLED ga o'zgaradi
        """
        self.finished_at = timezone.now()
        self.status = self.Status.CANCELLED
        self.save()


class DeviceCommand(models.Model):
    """
    Qurilmaga yuborilgan buyruqlar modeli.

    Qurilmaga yuborilgan har bir buyruq va uning natijasi saqlanadi.
    Debugging va audit uchun foydali.

    Attributes:
        device (HikvisionDevice): Maqsad qurilma
        command_type (str): Buyruq turi
        endpoint (str): API endpoint
        request_data (JSON): Yuborilgan ma'lumotlar
        response_data (JSON): Javob ma'lumotlari
        status_code (int): HTTP status kodi
        is_successful (bool): Muvaffaqiyatli yoki yo'q
        error_message (str): Xatolik xabari
        execution_time_ms (int): Bajarilish vaqti (millisekund)

    Example:
        >>> cmd = DeviceCommand.objects.create(
        ...     device=device,
        ...     command_type='get_users',
        ...     endpoint='/ISAPI/AccessControl/UserInfo/Search'
        ... )
    """

    class CommandType(models.TextChoices):
        """
        Buyruq turlari.
        """
        GET_DEVICE_INFO = 'get_device_info', _('Qurilma ma\'lumoti')
        GET_USERS = 'get_users', _('Foydalanuvchilar ro\'yxati')
        GET_EVENTS = 'get_events', _('Hodisalar ro\'yxati')
        ADD_USER = 'add_user', _('Foydalanuvchi qo\'shish')
        DELETE_USER = 'delete_user', _('Foydalanuvchi o\'chirish')
        SYNC_TIME = 'sync_time', _('Vaqtni sinxronlash')
        REBOOT = 'reboot', _('Qayta yuklash')
        OTHER = 'other', _('Boshqa')

    device = models.ForeignKey(
        HikvisionDevice,
        on_delete=models.CASCADE,
        related_name='commands',
        verbose_name=_("Qurilma")
    )
    command_type = models.CharField(
        max_length=30,
        choices=CommandType.choices,
        verbose_name=_("Buyruq turi")
    )
    endpoint = models.CharField(
        max_length=500,
        verbose_name=_("API endpoint"),
        help_text=_("So'rov yuborilgan URL yo'li")
    )
    http_method = models.CharField(
        max_length=10,
        default='GET',
        verbose_name=_("HTTP metod"),
        help_text=_("GET, POST, PUT, DELETE")
    )
    request_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("So'rov ma'lumotlari"),
        help_text=_("Yuborilgan ma'lumotlar (JSON)")
    )
    response_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("Javob ma'lumotlari"),
        help_text=_("Qurilmadan kelgan javob (JSON)")
    )
    status_code = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_("HTTP status kodi")
    )
    is_successful = models.BooleanField(
        default=False,
        verbose_name=_("Muvaffaqiyatli"),
        help_text=_("Buyruq muvaffaqiyatli bajarildi yoki yo'q")
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Xatolik xabari")
    )
    execution_time_ms = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Bajarilish vaqti (ms)"),
        help_text=_("Buyruq bajarilish vaqti millisekund")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Yaratilgan vaqt")
    )

    class Meta:
        verbose_name = _("Qurilma buyrug'i")
        verbose_name_plural = _("Qurilma buyruqlari")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device', 'created_at'], name='cmd_dev_time_idx'),
            models.Index(fields=['command_type'], name='cmd_type_idx'),
            models.Index(fields=['is_successful'], name='cmd_success_idx'),
        ]

    def __str__(self) -> str:
        """
        Buyruqni string sifatida qaytarish.

        Returns:
            str: Qurilma, buyruq turi va vaqt
        """
        status = "OK" if self.is_successful else "FAIL"
        return f"{self.device.name} - {self.get_command_type_display()} [{status}]"

    @property
    def execution_time_display(self) -> str:
        """
        Bajarilish vaqtini o'qishga qulay formatda.

        Returns:
            str: "150 ms" yoki "1.5 s" formatida
        """
        if not self.execution_time_ms:
            return "-"

        if self.execution_time_ms < 1000:
            return f"{self.execution_time_ms} ms"
        else:
            seconds = self.execution_time_ms / 1000
            return f"{seconds:.1f} s"
