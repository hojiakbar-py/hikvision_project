"""
Core Application Models.

Bu modul katta korxona tuzilmasini boshqarish uchun asosiy modellarni
o'z ichiga oladi. Ierarxik tuzilma quyidagicha:

    Organization (Bosh kompaniya)
        └── Branch (Filiallar)
                └── Department (Bo'limlar)
                        └── Position (Lavozimlar)
                                └── Employee (Hodimlar)

Models:
    - Organization: Bosh kompaniya/holding
    - Branch: Filiallar va ofislar
    - OrganizationSettings: Tizim sozlamalari

Example:
    >>> from apps.core.models import Organization, Branch
    >>> org = Organization.objects.create(
    ...     name="Mega Holding",
    ...     legal_name="Mega Holding LLC"
    ... )
    >>> branch = Branch.objects.create(
    ...     organization=org,
    ...     name="Toshkent Bosh Ofis",
    ...     branch_type='head_office'
    ... )
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import (
    RegexValidator,
    MinValueValidator,
    MaxValueValidator
)
from django.core.exceptions import ValidationError
from datetime import time
from typing import Optional


class Organization(models.Model):
    """
    Bosh tashkilot/kompaniya/holding modeli.

    Butun tizimning eng yuqori darajasi. Bitta tizimda bir nechta
    mustaqil tashkilotlarni boshqarish mumkin (multi-tenant).

    Attributes:
        name (str): Tashkilot nomi
        legal_name (str): Rasmiy yuridik nomi
        code (str): Qisqa kod (identifikator)
        inn (str): Soliq to'lovchi raqami (INN/TIN)
        logo (ImageField): Tashkilot logotipi
        description (str): Tavsif
        address (str): Yuridik manzil
        phone (str): Asosiy telefon
        email (str): Asosiy email
        website (str): Veb-sayt
        founded_date (date): Tashkil etilgan sana
        industry (str): Faoliyat sohasi
        employee_count (int): Taxminiy hodimlar soni
        is_active (bool): Faol yoki yo'q
        timezone (str): Vaqt zonasi
        currency (str): Asosiy valyuta
        language (str): Asosiy til

    Properties:
        total_branches: Jami filiallar soni
        total_employees: Jami hodimlar soni
        active_branches: Faol filiallar

    Example:
        >>> org = Organization.objects.get(code='MEGA')
        >>> org.total_branches
        15
        >>> org.total_employees
        1250
    """

    class Industry(models.TextChoices):
        """
        Faoliyat sohalari.
        """
        IT = 'it', _('IT va dasturlash')
        FINANCE = 'finance', _('Moliya va bank')
        RETAIL = 'retail', _('Chakana savdo')
        MANUFACTURING = 'manufacturing', _('Ishlab chiqarish')
        HEALTHCARE = 'healthcare', _('Sog\'liqni saqlash')
        EDUCATION = 'education', _('Ta\'lim')
        CONSTRUCTION = 'construction', _('Qurilish')
        TRANSPORT = 'transport', _('Transport va logistika')
        AGRICULTURE = 'agriculture', _('Qishloq xo\'jaligi')
        HOSPITALITY = 'hospitality', _('Mehmonxona va restoran')
        TELECOM = 'telecom', _('Telekommunikatsiya')
        ENERGY = 'energy', _('Energetika')
        GOVERNMENT = 'government', _('Davlat tashkiloti')
        OTHER = 'other', _('Boshqa')

    class Currency(models.TextChoices):
        """
        Valyutalar.
        """
        UZS = 'UZS', _("O'zbek so'mi")
        USD = 'USD', _('AQSH dollari')
        EUR = 'EUR', _('Yevro')
        RUB = 'RUB', _('Rossiya rubli')

    class Language(models.TextChoices):
        """
        Tillar.
        """
        UZ = 'uz', _("O'zbek")
        RU = 'ru', _('Rus')
        EN = 'en', _('Ingliz')

    # Telefon validatori
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Telefon raqami to'g'ri formatda bo'lishi kerak")
    )

    # Asosiy ma'lumotlar
    name = models.CharField(
        max_length=200,
        verbose_name=_("Tashkilot nomi"),
        help_text=_("Tashkilotning umumiy nomi")
    )
    legal_name = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name=_("Yuridik nomi"),
        help_text=_("Rasmiy hujjatlardagi to'liq nomi")
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Kod"),
        help_text=_("Qisqa unikal identifikator (masalan: MEGA, ABC)")
    )
    inn = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_("INN/STIR"),
        help_text=_("Soliq to'lovchi identifikatsiya raqami")
    )

    # Vizual
    logo = models.ImageField(
        upload_to='organizations/logos/',
        blank=True,
        null=True,
        verbose_name=_("Logo"),
        help_text=_("Tashkilot logotipi")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Tavsif"),
        help_text=_("Tashkilot haqida qisqacha ma'lumot")
    )

    # Aloqa ma'lumotlari
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Yuridik manzil"),
        help_text=_("Rasmiy ro'yxatdan o'tgan manzil")
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[phone_validator],
        verbose_name=_("Telefon"),
        help_text=_("Asosiy aloqa telefoni")
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_("Email"),
        help_text=_("Asosiy email manzili")
    )
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Veb-sayt"),
        help_text=_("Rasmiy veb-sayt manzili")
    )

    # Biznes ma'lumotlari
    founded_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Tashkil etilgan sana"),
        help_text=_("Kompaniya qachon tashkil etilgan")
    )
    industry = models.CharField(
        max_length=30,
        choices=Industry.choices,
        default=Industry.OTHER,
        verbose_name=_("Faoliyat sohasi"),
        help_text=_("Asosiy faoliyat yo'nalishi")
    )
    employee_count = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Hodimlar soni"),
        help_text=_("Taxminiy jami hodimlar soni")
    )

    # Sozlamalar
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Faol"),
        help_text=_("Tashkilot tizimda faol yoki yo'q")
    )
    timezone = models.CharField(
        max_length=50,
        default='Asia/Tashkent',
        verbose_name=_("Vaqt zonasi"),
        help_text=_("Tashkilotning asosiy vaqt zonasi")
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.UZS,
        verbose_name=_("Valyuta"),
        help_text=_("Asosiy hisob-kitob valyutasi")
    )
    language = models.CharField(
        max_length=5,
        choices=Language.choices,
        default=Language.UZ,
        verbose_name=_("Til"),
        help_text=_("Tizimning asosiy tili")
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
        verbose_name = _("Tashkilot")
        verbose_name_plural = _("Tashkilotlar")
        ordering = ['name']
        indexes = [
            models.Index(fields=['code'], name='org_code_idx'),
            models.Index(fields=['is_active'], name='org_active_idx'),
        ]

    def __str__(self) -> str:
        """
        Tashkilotni string sifatida qaytarish.

        Returns:
            str: Tashkilot nomi
        """
        return self.name

    def __repr__(self) -> str:
        """
        Debug uchun to'liq ma'lumot.

        Returns:
            str: Model va asosiy ma'lumotlar
        """
        return f"<Organization(id={self.pk}, code='{self.code}', name='{self.name}')>"

    @property
    def total_branches(self) -> int:
        """
        Jami filiallar sonini qaytarish.

        Returns:
            int: Barcha filiallar soni
        """
        return self.branches.count()

    @property
    def active_branches(self) -> int:
        """
        Faol filiallar sonini qaytarish.

        Returns:
            int: Faol filiallar soni
        """
        return self.branches.filter(is_active=True).count()

    @property
    def total_employees(self) -> int:
        """
        Jami hodimlar sonini qaytarish.

        Returns:
            int: Barcha filiallardagi hodimlar soni
        """
        from apps.employees.models import Employee
        return Employee.objects.filter(
            branch__organization=self,
            status='active'
        ).count()

    @property
    def total_departments(self) -> int:
        """
        Jami bo'limlar sonini qaytarish.

        Returns:
            int: Barcha bo'limlar soni
        """
        from apps.employees.models import Department
        return Department.objects.filter(
            branch__organization=self
        ).count()

    def get_hierarchy_tree(self) -> dict:
        """
        To'liq ierarxik tuzilmani qaytarish.

        Returns:
            dict: Filiallar, bo'limlar va hodimlar daraxt ko'rinishida

        Example:
            >>> org.get_hierarchy_tree()
            {
                'name': 'Mega Holding',
                'branches': [
                    {
                        'name': 'Toshkent Bosh Ofis',
                        'departments': [...]
                    }
                ]
            }
        """
        return {
            'id': self.pk,
            'name': self.name,
            'code': self.code,
            'branches': [
                branch.get_department_tree()
                for branch in self.branches.filter(is_active=True)
            ]
        }


class Branch(models.Model):
    """
    Filial/Ofis modeli.

    Tashkilotning turli joylardagi bo'linmalari. Har bir filialda
    o'zining bo'limlari, hodimlar va qurilmalari bo'ladi.

    Attributes:
        organization (Organization): Tegishli tashkilot
        parent (Branch): Yuqori filial (ierarxiya uchun)
        name (str): Filial nomi
        code (str): Filial kodi
        branch_type (str): Filial turi (bosh ofis, filial, omborxona)
        address (str): Filial manzili
        city (str): Shahar
        region (str): Viloyat/hudud
        country (str): Davlat
        phone (str): Telefon
        email (str): Email
        manager (Employee): Filial rahbari
        work_start_time (time): Ish boshlanish vaqti
        work_end_time (time): Ish tugash vaqti
        timezone (str): Vaqt zonasi
        is_active (bool): Faol yoki yo'q
        is_head_office (bool): Bosh ofis yoki yo'q

    Properties:
        full_address: To'liq manzil
        employee_count: Hodimlar soni
        department_count: Bo'limlar soni

    Example:
        >>> branch = Branch.objects.get(code='TSH-01')
        >>> branch.employee_count
        125
        >>> branch.full_address
        "Toshkent sh., Yunusobod t., Amir Temur ko'chasi, 15-uy"
    """

    class BranchType(models.TextChoices):
        """
        Filial turlari.

        Attributes:
            HEAD_OFFICE: Bosh ofis
            REGIONAL_OFFICE: Hududiy ofis
            BRANCH: Oddiy filial
            WAREHOUSE: Omborxona
            FACTORY: Zavod/fabrika
            STORE: Do'kon
            SERVICE_CENTER: Xizmat ko'rsatish markazi
        """
        HEAD_OFFICE = 'head_office', _('Bosh ofis')
        REGIONAL_OFFICE = 'regional_office', _('Hududiy ofis')
        BRANCH = 'branch', _('Filial')
        WAREHOUSE = 'warehouse', _('Omborxona')
        FACTORY = 'factory', _('Zavod/Fabrika')
        STORE = 'store', _("Do'kon")
        SERVICE_CENTER = 'service_center', _('Xizmat markazi')

    # Telefon validatori
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Telefon raqami to'g'ri formatda bo'lishi kerak")
    )

    # Bog'lanishlar
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='branches',
        verbose_name=_("Tashkilot"),
        help_text=_("Filial tegishli tashkilot")
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_("Yuqori filial"),
        help_text=_("Ierarxik bog'lanish (masalan: hududiy ofis -> bosh ofis)")
    )

    # Asosiy ma'lumotlar
    name = models.CharField(
        max_length=200,
        verbose_name=_("Filial nomi"),
        help_text=_("Filialning to'liq nomi")
    )
    code = models.CharField(
        max_length=20,
        verbose_name=_("Filial kodi"),
        help_text=_("Unikal identifikator (masalan: TSH-01, SAM-02)")
    )
    branch_type = models.CharField(
        max_length=20,
        choices=BranchType.choices,
        default=BranchType.BRANCH,
        verbose_name=_("Filial turi"),
        help_text=_("Filialning vazifasi bo'yicha turi")
    )

    # Manzil ma'lumotlari
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Manzil"),
        help_text=_("To'liq ko'cha manzili")
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Shahar"),
        help_text=_("Shahar nomi")
    )
    region = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Viloyat/Hudud"),
        help_text=_("Viloyat yoki hudud nomi")
    )
    country = models.CharField(
        max_length=100,
        default="O'zbekiston",
        verbose_name=_("Davlat"),
        help_text=_("Davlat nomi")
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name=_("Kenglik"),
        help_text=_("GPS koordinata (latitude)")
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name=_("Uzunlik"),
        help_text=_("GPS koordinata (longitude)")
    )

    # Aloqa ma'lumotlari
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[phone_validator],
        verbose_name=_("Telefon"),
        help_text=_("Asosiy aloqa telefoni")
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_("Email"),
        help_text=_("Filial email manzili")
    )

    # Ish vaqti sozlamalari
    work_start_time = models.TimeField(
        default=time(9, 0),
        verbose_name=_("Ish boshlanish vaqti"),
        help_text=_("Filialning standart ish boshlanish vaqti")
    )
    work_end_time = models.TimeField(
        default=time(18, 0),
        verbose_name=_("Ish tugash vaqti"),
        help_text=_("Filialning standart ish tugash vaqti")
    )
    timezone = models.CharField(
        max_length=50,
        default='Asia/Tashkent',
        verbose_name=_("Vaqt zonasi"),
        help_text=_("Filialning vaqt zonasi")
    )

    # Holat
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Faol"),
        help_text=_("Filial faol yoki yo'q")
    )
    is_head_office = models.BooleanField(
        default=False,
        verbose_name=_("Bosh ofis"),
        help_text=_("Bu filial bosh ofis hisoblanadimi")
    )

    # Qo'shimcha
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Tavsif"),
        help_text=_("Filial haqida qo'shimcha ma'lumot")
    )
    established_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Ochilgan sana"),
        help_text=_("Filial qachon ochilgan")
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
        verbose_name = _("Filial")
        verbose_name_plural = _("Filiallar")
        ordering = ['organization', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'code'],
                name='unique_branch_code_per_org'
            )
        ]
        indexes = [
            models.Index(fields=['organization', 'code'], name='branch_org_code_idx'),
            models.Index(fields=['is_active'], name='branch_active_idx'),
            models.Index(fields=['branch_type'], name='branch_type_idx'),
            models.Index(fields=['city'], name='branch_city_idx'),
        ]

    def __str__(self) -> str:
        """
        Filialni string sifatida qaytarish.

        Returns:
            str: Filial nomi va kodi
        """
        return f"{self.name} ({self.code})"

    def __repr__(self) -> str:
        """
        Debug uchun to'liq ma'lumot.

        Returns:
            str: Model va asosiy ma'lumotlar
        """
        return (
            f"<Branch(id={self.pk}, code='{self.code}', "
            f"name='{self.name}', org='{self.organization.code}')>"
        )

    @property
    def full_address(self) -> str:
        """
        To'liq manzilni qaytarish.

        Returns:
            str: Formatlangan to'liq manzil

        Example:
            >>> branch.full_address
            "O'zbekiston, Toshkent sh., Chilonzor t., Bunyodkor ko'chasi 12"
        """
        parts = []
        if self.country:
            parts.append(self.country)
        if self.region:
            parts.append(self.region)
        if self.city:
            parts.append(f"{self.city} sh.")
        if self.address:
            parts.append(self.address)
        return ", ".join(parts) if parts else ""

    @property
    def employee_count(self) -> int:
        """
        Filialdagi faol hodimlar sonini qaytarish.

        Returns:
            int: Hodimlar soni
        """
        from apps.employees.models import Employee
        return Employee.objects.filter(
            branch=self,
            status='active'
        ).count()

    @property
    def department_count(self) -> int:
        """
        Filialdagi bo'limlar sonini qaytarish.

        Returns:
            int: Bo'limlar soni
        """
        return self.departments.filter(is_active=True).count()

    @property
    def device_count(self) -> int:
        """
        Filialdagi qurilmalar sonini qaytarish.

        Returns:
            int: Qurilmalar soni
        """
        return self.devices.filter(is_active=True).count()

    @property
    def full_path(self) -> str:
        """
        To'liq ierarxik yo'lni qaytarish.

        Returns:
            str: "Tashkilot > Hududiy ofis > Filial" formatida
        """
        path_parts = [self.name]
        current = self.parent
        while current:
            path_parts.insert(0, current.name)
            current = current.parent
        path_parts.insert(0, self.organization.name)
        return " > ".join(path_parts)

    def get_department_tree(self) -> dict:
        """
        Bo'limlar daraxtini qaytarish.

        Returns:
            dict: Bo'limlar va lavozimlar ierarxiyasi
        """
        return {
            'id': self.pk,
            'name': self.name,
            'code': self.code,
            'type': self.branch_type,
            'employee_count': self.employee_count,
            'departments': [
                dept.get_position_tree()
                for dept in self.departments.filter(is_active=True, parent__isnull=True)
            ]
        }

    def get_children_recursive(self) -> list:
        """
        Barcha pastki filiallarni rekursiv olish.

        Returns:
            list: Barcha child filiallar
        """
        children = list(self.children.filter(is_active=True))
        for child in list(children):
            children.extend(child.get_children_recursive())
        return children

    def get_all_employees(self, include_children: bool = False):
        """
        Filialdagi barcha hodimlarni olish.

        Args:
            include_children: True bo'lsa, pastki filiallar ham qo'shiladi

        Returns:
            QuerySet: Employee yozuvlari
        """
        from apps.employees.models import Employee

        if include_children:
            branch_ids = [self.pk] + [b.pk for b in self.get_children_recursive()]
            return Employee.objects.filter(branch_id__in=branch_ids)
        return Employee.objects.filter(branch=self)

    def get_attendance_stats(self, date=None, include_children: bool = False) -> dict:
        """
        Filial uchun davomat statistikasini olish.

        Args:
            date: Qaysi kun uchun (default: bugun)
            include_children: Pastki filiallar ham qo'shilsinmi

        Returns:
            dict: Davomat statistikasi

        Example:
            >>> branch.get_attendance_stats()
            {
                'total_employees': 50,
                'present': 45,
                'absent': 3,
                'late': 8,
                'on_leave': 2,
                'present_percentage': 90.0,
                'late_percentage': 16.0
            }
        """
        from apps.attendance.models import DailyAttendance
        from apps.employees.models import Employee

        if date is None:
            from datetime import date as dt_date
            date = dt_date.today()

        # Filial hodimlarini olish
        employees = self.get_all_employees(include_children=include_children)
        total_employees = employees.filter(status='active').count()

        if total_employees == 0:
            return {
                'date': date,
                'total_employees': 0,
                'present': 0,
                'absent': 0,
                'late': 0,
                'half_day': 0,
                'on_leave': 0,
                'present_percentage': 0,
                'late_percentage': 0
            }

        # Davomat statistikasi
        attendance_qs = DailyAttendance.objects.filter(
            employee__in=employees,
            date=date
        )

        stats = {
            'date': date,
            'total_employees': total_employees,
            'present': attendance_qs.filter(status='present').count(),
            'absent': attendance_qs.filter(status='absent').count(),
            'late': attendance_qs.filter(status='late').count(),
            'half_day': attendance_qs.filter(status='half_day').count(),
            'on_leave': attendance_qs.filter(status='on_leave').count(),
        }

        # Foizlarni hisoblash
        stats['present_percentage'] = round(
            (stats['present'] / total_employees) * 100, 2
        ) if total_employees > 0 else 0

        stats['late_percentage'] = round(
            (stats['late'] / total_employees) * 100, 2
        ) if total_employees > 0 else 0

        return stats

    def get_attendance_summary(self, start_date, end_date, include_children: bool = False) -> dict:
        """
        Ma'lum davr uchun davomat xulosasi.

        Args:
            start_date: Boshlanish sanasi
            end_date: Tugash sanasi
            include_children: Pastki filiallar ham qo'shilsinmi

        Returns:
            dict: Davomat xulosasi

        Example:
            >>> branch.get_attendance_summary(
            ...     start_date=date(2024, 1, 1),
            ...     end_date=date(2024, 1, 31)
            ... )
            {
                'period': {'start': '2024-01-01', 'end': '2024-01-31'},
                'total_working_days': 22,
                'average_present': 45.5,
                'average_late': 5.2,
                'total_late_minutes': 2340,
                'departments': {...}
            }
        """
        from apps.attendance.models import DailyAttendance
        from django.db.models import Avg, Sum, Count, Q

        employees = self.get_all_employees(include_children=include_children)

        attendance_qs = DailyAttendance.objects.filter(
            employee__in=employees,
            date__gte=start_date,
            date__lte=end_date
        )

        # Aggregatsiyalar
        aggregations = attendance_qs.aggregate(
            total_records=Count('id'),
            total_late_minutes=Sum('late_minutes'),
            total_overtime_minutes=Sum('overtime_minutes'),
            average_work_hours=Avg('work_hours'),
            present_count=Count('id', filter=Q(status='present')),
            late_count=Count('id', filter=Q(status='late')),
            absent_count=Count('id', filter=Q(status='absent'))
        )

        # Ish kunlari soni
        from datetime import timedelta
        delta = end_date - start_date
        working_days = delta.days + 1

        summary = {
            'period': {
                'start': start_date,
                'end': end_date,
                'days': working_days
            },
            'total_employees': employees.filter(status='active').count(),
            'total_records': aggregations['total_records'] or 0,
            'total_late_minutes': aggregations['total_late_minutes'] or 0,
            'total_overtime_minutes': aggregations['total_overtime_minutes'] or 0,
            'average_work_hours': round(aggregations['average_work_hours'] or 0, 2),
            'present_count': aggregations['present_count'] or 0,
            'late_count': aggregations['late_count'] or 0,
            'absent_count': aggregations['absent_count'] or 0
        }

        # O'rtacha ko'rsatkichlar
        if working_days > 0:
            summary['average_present_per_day'] = round(
                summary['present_count'] / working_days, 2
            )
            summary['average_late_per_day'] = round(
                summary['late_count'] / working_days, 2
            )
            summary['average_absent_per_day'] = round(
                summary['absent_count'] / working_days, 2
            )

        return summary

    def get_department_attendance_breakdown(self, date=None) -> list:
        """
        Bo'limlar bo'yicha davomat taqsimoti.

        Args:
            date: Qaysi kun uchun (default: bugun)

        Returns:
            list: Har bir bo'lim uchun statistika

        Example:
            >>> branch.get_department_attendance_breakdown()
            [
                {
                    'department': 'IT',
                    'total': 15,
                    'present': 14,
                    'late': 3,
                    'absent': 1
                },
                ...
            ]
        """
        from apps.attendance.models import DailyAttendance
        from apps.employees.models import Department
        from django.db.models import Count, Q

        if date is None:
            from datetime import date as dt_date
            date = dt_date.today()

        departments = self.departments.filter(is_active=True)
        breakdown = []

        for dept in departments:
            dept_employees = dept.employees.filter(status='active')
            total = dept_employees.count()

            if total == 0:
                continue

            attendance = DailyAttendance.objects.filter(
                employee__in=dept_employees,
                date=date
            ).aggregate(
                present=Count('id', filter=Q(status='present')),
                late=Count('id', filter=Q(status='late')),
                absent=Count('id', filter=Q(status='absent')),
                half_day=Count('id', filter=Q(status='half_day')),
                on_leave=Count('id', filter=Q(status='on_leave'))
            )

            breakdown.append({
                'department_id': dept.id,
                'department_name': dept.name,
                'department_code': dept.code,
                'total_employees': total,
                'present': attendance['present'] or 0,
                'late': attendance['late'] or 0,
                'absent': attendance['absent'] or 0,
                'half_day': attendance['half_day'] or 0,
                'on_leave': attendance['on_leave'] or 0,
                'present_percentage': round(
                    ((attendance['present'] or 0) / total) * 100, 2
                ) if total > 0 else 0
            })

        return breakdown

    def get_top_latecomers(self, start_date, end_date, limit: int = 10) -> list:
        """
        Eng ko'p kechikkan hodimlar ro'yxati.

        Args:
            start_date: Boshlanish sanasi
            end_date: Tugash sanasi
            limit: Nechta hodim qaytarish

        Returns:
            list: Eng ko'p kechikkanlar

        Example:
            >>> branch.get_top_latecomers(
            ...     start_date=date(2024, 1, 1),
            ...     end_date=date(2024, 1, 31),
            ...     limit=5
            ... )
            [
                {
                    'employee': 'Ali Valiyev',
                    'late_count': 12,
                    'total_late_minutes': 180
                },
                ...
            ]
        """
        from apps.attendance.models import DailyAttendance
        from django.db.models import Count, Sum, Q

        employees = self.get_all_employees()

        latecomers = DailyAttendance.objects.filter(
            employee__in=employees,
            date__gte=start_date,
            date__lte=end_date,
            status='late'
        ).values(
            'employee__id',
            'employee__first_name',
            'employee__last_name',
            'employee__personnel_number',
            'employee__department__name'
        ).annotate(
            late_count=Count('id'),
            total_late_minutes=Sum('late_minutes')
        ).order_by('-late_count')[:limit]

        result = []
        for item in latecomers:
            result.append({
                'employee_id': item['employee__id'],
                'personnel_number': item['employee__personnel_number'],
                'employee_name': f"{item['employee__first_name']} {item['employee__last_name']}",
                'department': item['employee__department__name'],
                'late_count': item['late_count'],
                'total_late_minutes': item['total_late_minutes'] or 0,
                'average_late_minutes': round(
                    (item['total_late_minutes'] or 0) / item['late_count'], 2
                ) if item['late_count'] > 0 else 0
            })

        return result

    def save(self, *args, **kwargs) -> None:
        """
        Filialni saqlash.

        Note:
            Agar is_head_office=True bo'lsa va branch_type boshqa bo'lsa,
            branch_type avtomatik HEAD_OFFICE ga o'zgaradi.
        """
        if self.is_head_office:
            self.branch_type = self.BranchType.HEAD_OFFICE
            # Boshqa head office larni false qilish
            Branch.objects.filter(
                organization=self.organization,
                is_head_office=True
            ).exclude(pk=self.pk).update(is_head_office=False)
        super().save(*args, **kwargs)

    def clean(self) -> None:
        """
        Model validatsiyasi.

        Raises:
            ValidationError: Noto'g'ri bog'lanishlar bo'lsa
        """
        if self.parent:
            # Parent boshqa tashkilotga tegishli bo'lmasligi kerak
            if self.parent.organization_id != self.organization_id:
                raise ValidationError({
                    'parent': _("Yuqori filial boshqa tashkilotga tegishli bo'lishi mumkin emas")
                })
            # O'ziga o'zi parent bo'lmasligi kerak
            if self.pk and self.parent_id == self.pk:
                raise ValidationError({
                    'parent': _("Filial o'ziga o'zi yuqori filial bo'lishi mumkin emas")
                })


class OrganizationSettings(models.Model):
    """
    Tashkilot sozlamalari modeli.

    Har bir tashkilot uchun alohida sozlamalar saqlash.

    Attributes:
        organization (Organization): Tegishli tashkilot
        late_threshold_minutes (int): Kechikish chegarasi
        early_leave_threshold_minutes (int): Erta ketish chegarasi
        overtime_calculation (bool): Overtime hisoblash
        auto_sync_interval (int): Avtomatik sinxronizatsiya oralig'i
        notification_email (str): Bildirishnoma email
        working_days (JSON): Ish kunlari
        allow_remote_work (bool): Masofadan ishlash ruxsati

    Example:
        >>> settings = OrganizationSettings.objects.get(organization=org)
        >>> settings.late_threshold_minutes
        5
    """

    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='settings',
        verbose_name=_("Tashkilot")
    )

    # Davomat sozlamalari
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
        help_text=_("Necha daqiqadan oldin ketsa erta ketish hisoblanadi")
    )
    overtime_calculation_enabled = models.BooleanField(
        default=True,
        verbose_name=_("Overtime hisoblash"),
        help_text=_("Qo'shimcha ish vaqtini hisoblash yoqilgan")
    )
    half_day_threshold_hours = models.PositiveIntegerField(
        default=4,
        validators=[MaxValueValidator(12)],
        verbose_name=_("Yarim kun chegarasi (soat)"),
        help_text=_("Necha soatdan kam ishlasa yarim kun hisoblanadi")
    )

    # Ish kunlari
    working_days = models.JSONField(
        default=list,
        verbose_name=_("Ish kunlari"),
        help_text=_("Ish kunlari ro'yxati [0-6]: 0=Dushanba, 6=Yakshanba")
    )

    # Sinxronizatsiya
    auto_sync_interval_minutes = models.PositiveIntegerField(
        default=15,
        validators=[MinValueValidator(5), MaxValueValidator(1440)],
        verbose_name=_("Avtomatik sinxronizatsiya (daqiqa)"),
        help_text=_("Qancha vaqt oralig'ida sinxronlanadi")
    )
    sync_history_days = models.PositiveIntegerField(
        default=30,
        verbose_name=_("Sinxronizatsiya tarixi (kun)"),
        help_text=_("Necha kunlik tarix saqlanadi")
    )

    # Bildirishnomalar
    notification_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_("Bildirishnoma email"),
        help_text=_("Muhim xabarlar uchun email")
    )
    send_daily_report = models.BooleanField(
        default=False,
        verbose_name=_("Kunlik hisobot yuborish"),
        help_text=_("Har kuni avtomatik hisobot yuborish")
    )
    send_late_notifications = models.BooleanField(
        default=True,
        verbose_name=_("Kechikish xabari"),
        help_text=_("Kechikganlar haqida xabar yuborish")
    )

    # Qo'shimcha sozlamalar
    allow_remote_work = models.BooleanField(
        default=False,
        verbose_name=_("Masofadan ishlash"),
        help_text=_("Hodimlar masofadan ishlashi mumkinmi")
    )
    require_photo_on_check = models.BooleanField(
        default=False,
        verbose_name=_("Rasm talab qilish"),
        help_text=_("Kirish/chiqishda rasm olish majburiymi")
    )
    allow_manual_attendance = models.BooleanField(
        default=True,
        verbose_name=_("Qo'lda davomat"),
        help_text=_("Admin qo'lda davomat kiritishi mumkinmi")
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
        verbose_name = _("Tashkilot sozlamasi")
        verbose_name_plural = _("Tashkilot sozlamalari")

    def __str__(self) -> str:
        """
        Sozlamani string sifatida qaytarish.

        Returns:
            str: Tashkilot nomi bilan
        """
        return f"Sozlamalar: {self.organization.name}"

    def get_working_days_display(self) -> str:
        """
        Ish kunlarini o'qishga qulay formatda qaytarish.

        Returns:
            str: "Dushanba - Juma" formatida
        """
        day_names = ['Du', 'Se', 'Chor', 'Pay', 'Ju', 'Sha', 'Yak']
        if not self.working_days:
            return "Dushanba - Juma"
        days = [day_names[d] for d in sorted(self.working_days)]
        return ", ".join(days)

    def save(self, *args, **kwargs) -> None:
        """
        Sozlamalarni saqlash.

        Note:
            Agar working_days bo'sh bo'lsa, default qiymat qo'yiladi.
        """
        if not self.working_days:
            self.working_days = [0, 1, 2, 3, 4]  # Dushanba - Juma
        super().save(*args, **kwargs)
