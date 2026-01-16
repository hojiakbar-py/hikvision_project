"""
Employees Application Models.

Bu modul tashkilot hodimlarini boshqarish uchun modellarni o'z ichiga oladi.
Ierarxik tuzilma:

    Organization (core app)
        └── Branch (core app)
                └── Department (shu yerda)
                        └── Position (shu yerda)
                                └── Employee (shu yerda)

Models:
    - Department: Bo'limlar (filialga tegishli)
    - Position: Lavozimlar
    - Employee: Hodimlar
    - EmployeeDocument: Hodim hujjatlari

Example:
    >>> from apps.employees.models import Department, Position, Employee
    >>> dept = Department.objects.create(
    ...     branch=branch,
    ...     name="IT Bo'limi",
    ...     code="IT"
    ... )
"""

from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import time
from typing import Optional


class Department(models.Model):
    """
    Bo'lim modeli.

    Har bir bo'lim ma'lum bir filialga tegishli. Bo'limlar ierarxik
    tuzilmaga ega bo'lishi mumkin (parent orqali).

    Attributes:
        branch (Branch): Tegishli filial
        parent (Department): Yuqori bo'lim (ierarxiya uchun)
        name (str): Bo'lim nomi
        code (str): Bo'lim kodi
        description (str): Tavsif
        head (Employee): Bo'lim boshlig'i
        budget_code (str): Byudjet kodi
        cost_center (str): Xarajat markazi
        is_active (bool): Faol yoki yo'q
        sort_order (int): Tartib raqami

    Properties:
        full_name: Filial bilan to'liq nomi
        employee_count: Hodimlar soni
        full_path: To'liq ierarxik yo'l

    Example:
        >>> dept = Department.objects.get(code='IT', branch=branch)
        >>> dept.full_path
        "Mega Holding > Toshkent Bosh Ofis > IT Bo'limi"
    """

    branch = models.ForeignKey(
        'core.Branch',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='departments',
        verbose_name=_("Filial"),
        help_text=_("Bo'lim tegishli filial")
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_("Yuqori bo'lim"),
        help_text=_("Ierarxik tuzilma uchun")
    )

    # Asosiy ma'lumotlar
    name = models.CharField(
        max_length=100,
        verbose_name=_("Bo'lim nomi"),
        help_text=_("Bo'limning to'liq nomi")
    )
    code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("Bo'lim kodi"),
        help_text=_("Qisqa identifikator (masalan: IT, HR, FIN)")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Tavsif"),
        help_text=_("Bo'lim haqida qisqacha ma'lumot")
    )

    # Boshqaruv
    head = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        verbose_name=_("Bo'lim boshlig'i"),
        help_text=_("Bo'limning rahbari")
    )

    # Moliyaviy kodlar
    budget_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Byudjet kodi"),
        help_text=_("Moliyaviy hisobot uchun byudjet kodi")
    )
    cost_center = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Xarajat markazi"),
        help_text=_("Cost center kodi")
    )

    # Holat va tartib
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Faol"),
        help_text=_("Bo'lim faol yoki arxivlangan")
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Tartib"),
        help_text=_("Ro'yxatdagi tartib raqami")
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
        verbose_name = _("Bo'lim")
        verbose_name_plural = _("Bo'limlar")
        ordering = ['branch', 'sort_order', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['branch', 'code'],
                name='unique_dept_code_per_branch'
            )
        ]
        indexes = [
            models.Index(fields=['branch', 'code'], name='dept_branch_code_idx'),
            models.Index(fields=['is_active'], name='dept_active_idx'),
        ]

    def __str__(self) -> str:
        """
        Bo'limni string sifatida qaytarish.

        Returns:
            str: Bo'lim nomi
        """
        branch_code = self.branch.code if self.branch else "N/A"
        return f"{self.name} ({branch_code})"

    def __repr__(self) -> str:
        """
        Debug uchun to'liq ma'lumot.

        Returns:
            str: Model va asosiy ma'lumotlar
        """
        return f"<Department(id={self.pk}, code='{self.code}', branch='{self.branch.code}')>"

    @property
    def full_name(self) -> str:
        """
        Filial bilan to'liq nomni qaytarish.

        Returns:
            str: "Filial - Bo'lim" formatida
        """
        return f"{self.branch.name} - {self.name}"

    @property
    def employee_count(self) -> int:
        """
        Bo'limdagi faol hodimlar sonini qaytarish.

        Returns:
            int: Hodimlar soni
        """
        return self.employees.filter(status='active').count()

    @property
    def full_path(self) -> str:
        """
        Bo'limning to'liq ierarxik yo'lini qaytarish.

        Returns:
            str: "Tashkilot > Filial > Bo'lim" formatida
        """
        path_parts = [self.name]
        current = self.parent
        while current:
            path_parts.insert(0, current.name)
            current = current.parent
        path_parts.insert(0, self.branch.name)
        path_parts.insert(0, self.branch.organization.name)
        return " > ".join(path_parts)

    @property
    def organization(self):
        """
        Tegishli tashkilotni qaytarish.

        Returns:
            Organization: Tashkilot obyekti
        """
        return self.branch.organization

    def get_children_recursive(self) -> list:
        """
        Barcha pastki bo'limlarni rekursiv olish.

        Returns:
            list: Barcha child bo'limlar
        """
        children = list(self.children.filter(is_active=True))
        for child in list(children):
            children.extend(child.get_children_recursive())
        return children

    def get_all_employees(self, include_children: bool = False):
        """
        Bo'limdagi barcha hodimlarni olish.

        Args:
            include_children: True bo'lsa, pastki bo'limlar ham qo'shiladi

        Returns:
            QuerySet: Employee yozuvlari
        """
        if include_children:
            dept_ids = [self.pk] + [d.pk for d in self.get_children_recursive()]
            return Employee.objects.filter(department_id__in=dept_ids)
        return self.employees.all()

    def get_position_tree(self) -> dict:
        """
        Lavozimlar va hodimlar daraxtini qaytarish.

        Returns:
            dict: Bo'lim, lavozimlar va hodimlar ierarxiyasi
        """
        return {
            'id': self.pk,
            'name': self.name,
            'code': self.code,
            'employee_count': self.employee_count,
            'children': [
                child.get_position_tree()
                for child in self.children.filter(is_active=True)
            ],
            'positions': [
                {
                    'id': pos.pk,
                    'name': pos.name,
                    'employee_count': pos.employee_count
                }
                for pos in self.positions.filter(is_active=True)
            ]
        }

    def clean(self) -> None:
        """
        Model validatsiyasi.

        Raises:
            ValidationError: Noto'g'ri bog'lanishlar bo'lsa
        """
        if self.parent:
            # Parent boshqa filialga tegishli bo'lmasligi kerak
            if self.parent.branch_id != self.branch_id:
                raise ValidationError({
                    'parent': _("Yuqori bo'lim boshqa filialga tegishli bo'lishi mumkin emas")
                })
            # O'ziga o'zi parent bo'lmasligi kerak
            if self.pk and self.parent_id == self.pk:
                raise ValidationError({
                    'parent': _("Bo'lim o'ziga o'zi yuqori bo'lim bo'lishi mumkin emas")
                })


class Position(models.Model):
    """
    Lavozim modeli.

    Har bir lavozim ma'lum bir bo'limga tegishli. Lavozimga ish haqi
    diapazoni, daraja va talablar belgilanishi mumkin.

    Attributes:
        department (Department): Tegishli bo'lim
        name (str): Lavozim nomi
        code (str): Lavozim kodi
        level (int): Lavozim darajasi (1-10)
        description (str): Lavozim vazifalari tavsifi
        min_salary (Decimal): Minimal ish haqi
        max_salary (Decimal): Maksimal ish haqi
        requirements (str): Lavozim talablari
        is_manager (bool): Boshqaruv lavozimi yoki yo'q
        is_active (bool): Lavozim faol yoki yo'q
        headcount (int): Rejalashtirilgan shtat soni

    Properties:
        employee_count: Bu lavozimdagi hodimlar soni
        full_name: Bo'lim bilan to'liq nomi
        vacancy_count: Bo'sh o'rinlar soni

    Example:
        >>> pos = Position.objects.get(code='DEV-SR')
        >>> pos.vacancy_count
        2
    """

    class Level(models.IntegerChoices):
        """
        Lavozim darajalari.
        """
        INTERN = 1, _('Stajyor')
        JUNIOR = 2, _('Junior')
        MIDDLE = 3, _('Middle')
        SENIOR = 4, _('Senior')
        LEAD = 5, _('Lead/Boshlovchi')
        MANAGER = 6, _('Menejer')
        DIRECTOR = 7, _('Direktor')
        VP = 8, _('Vitse-prezident')
        C_LEVEL = 9, _('C-Level')
        CEO = 10, _('Bosh direktor')

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name=_("Bo'lim"),
        help_text=_("Lavozim tegishli bo'lim")
    )

    # Asosiy ma'lumotlar
    name = models.CharField(
        max_length=100,
        verbose_name=_("Lavozim nomi"),
        help_text=_("Lavozimning to'liq nomi")
    )
    code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("Lavozim kodi"),
        help_text=_("Qisqa identifikator")
    )
    level = models.IntegerField(
        choices=Level.choices,
        default=Level.MIDDLE,
        verbose_name=_("Daraja"),
        help_text=_("Lavozim darajasi (1-10)")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Tavsif"),
        help_text=_("Lavozim vazifalari va mas'uliyatlari")
    )

    # Ish haqi
    min_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_("Minimal ish haqi"),
        help_text=_("Lavozim uchun minimal oylik")
    )
    max_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_("Maksimal ish haqi"),
        help_text=_("Lavozim uchun maksimal oylik")
    )

    # Talablar va qo'shimcha
    requirements = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Talablar"),
        help_text=_("Lavozim uchun zarur bilim va ko'nikmalar")
    )
    is_manager = models.BooleanField(
        default=False,
        verbose_name=_("Boshqaruv lavozimi"),
        help_text=_("Bu lavozim boshqaruv vazifasini bajaradimi")
    )
    headcount = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Shtat soni"),
        help_text=_("Bu lavozim uchun rejalashtirilgan hodimlar soni")
    )

    # Holat
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Faol"),
        help_text=_("Lavozim faol yoki arxivlangan")
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
        verbose_name = _("Lavozim")
        verbose_name_plural = _("Lavozimlar")
        ordering = ['department', '-level', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['department', 'name'],
                name='unique_position_per_dept'
            )
        ]
        indexes = [
            models.Index(fields=['department'], name='pos_dept_idx'),
            models.Index(fields=['level'], name='pos_level_idx'),
            models.Index(fields=['is_active'], name='pos_active_idx'),
        ]

    def __str__(self) -> str:
        """
        Lavozimni string sifatida qaytarish.

        Returns:
            str: Lavozim nomi va bo'limi
        """
        return f"{self.name} ({self.department.name})"

    def __repr__(self) -> str:
        """
        Debug uchun to'liq ma'lumot.

        Returns:
            str: Model va asosiy ma'lumotlar
        """
        return f"<Position(id={self.pk}, name='{self.name}', dept='{self.department.name}')>"

    @property
    def full_name(self) -> str:
        """
        Bo'lim bilan to'liq nomni qaytarish.

        Returns:
            str: "Bo'lim - Lavozim" formatida
        """
        return f"{self.department.name} - {self.name}"

    @property
    def employee_count(self) -> int:
        """
        Bu lavozimdagi faol hodimlar sonini qaytarish.

        Returns:
            int: Hodimlar soni
        """
        return self.employees.filter(status='active').count()

    @property
    def vacancy_count(self) -> int:
        """
        Bo'sh o'rinlar sonini qaytarish.

        Returns:
            int: Headcount - hozirgi hodimlar soni
        """
        return max(0, self.headcount - self.employee_count)

    @property
    def branch(self):
        """
        Tegishli filialni qaytarish.

        Returns:
            Branch: Filial obyekti
        """
        return self.department.branch

    @property
    def organization(self):
        """
        Tegishli tashkilotni qaytarish.

        Returns:
            Organization: Tashkilot obyekti
        """
        return self.department.branch.organization

    @property
    def salary_range_display(self) -> str:
        """
        Ish haqi diapazonini formatlangan ko'rinishda qaytarish.

        Returns:
            str: "1,000,000 - 2,000,000" formatida
        """
        if self.min_salary and self.max_salary:
            return f"{self.min_salary:,.0f} - {self.max_salary:,.0f}"
        elif self.min_salary:
            return f"{self.min_salary:,.0f} dan"
        elif self.max_salary:
            return f"{self.max_salary:,.0f} gacha"
        return "-"


class Employee(models.Model):
    """
    Hodim modeli.

    Tashkilot xodimlarining barcha ma'lumotlarini saqlash uchun asosiy model.
    Har bir hodim ma'lum bir filial va bo'limga tegishli.

    Attributes:
        branch (Branch): Tegishli filial
        department (Department): Tegishli bo'lim
        position (Position): Lavozim
        employee_id (str): Hikvision'dagi unikal ID
        first_name (str): Hodim ismi
        last_name (str): Hodim familiyasi
        middle_name (str): Otasining ismi
        phone (str): Telefon raqami
        email (str): Email manzili
        work_start_time (time): Ish boshlanish vaqti
        work_end_time (time): Ish tugash vaqti
        status (str): Hodim holati
        hire_date (date): Ishga qabul sanasi
        termination_date (date): Ishdan bo'shatilgan sana
        photo (ImageField): Hodim rasmi
        birth_date (date): Tug'ilgan sana
        gender (str): Jinsi
        address (str): Yashash manzili
        emergency_contact (str): Favqulodda aloqa
        notes (str): Qo'shimcha izohlar

    Properties:
        full_name: To'liq ism
        short_name: Qisqa ism
        is_working_now: Hozir ish vaqtida yoki yo'q
        years_of_service: Ishlagan yillar
        age: Yoshi
        organization: Tegishli tashkilot

    Example:
        >>> emp = Employee.objects.get(employee_id="EMP001")
        >>> emp.full_name
        "Valiyev Ali Karimovich"
        >>> emp.organization.name
        "Mega Holding"
    """

    class Status(models.TextChoices):
        """
        Hodim holatlari.

        Attributes:
            ACTIVE: Faol ishlamoqda
            INACTIVE: Nofaol (vaqtincha)
            ON_LEAVE: Ta'tilda
            PROBATION: Sinov muddatida
            TERMINATED: Ishdan bo'shatilgan
        """
        ACTIVE = 'active', _('Faol')
        INACTIVE = 'inactive', _('Nofaol')
        ON_LEAVE = 'on_leave', _("Ta'tilda")
        PROBATION = 'probation', _('Sinov muddati')
        TERMINATED = 'terminated', _('Bo\'shatilgan')

    class Gender(models.TextChoices):
        """
        Jins turlari.
        """
        MALE = 'male', _('Erkak')
        FEMALE = 'female', _('Ayol')

    class EmploymentType(models.TextChoices):
        """
        Ish turi.
        """
        FULL_TIME = 'full_time', _("To'liq stavka")
        PART_TIME = 'part_time', _('Yarim stavka')
        CONTRACT = 'contract', _('Shartnoma')
        INTERN = 'intern', _('Stajirovka')
        REMOTE = 'remote', _('Masofadan')

    # Telefon validatori
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Telefon raqami to'g'ri formatda bo'lishi kerak: '+998901234567'")
    )

    # Tashkilot bog'lanishlari
    branch = models.ForeignKey(
        'core.Branch',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name=_("Filial"),
        help_text=_("Hodim ishlaydigan filial")
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name=_("Bo'lim"),
        help_text=_("Hodim ishlaydigan bo'lim")
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name=_("Lavozim"),
        help_text=_("Hodimning lavozimi")
    )
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates',
        verbose_name=_("Rahbar"),
        help_text=_("Hodimning bevosita rahbari")
    )

    # Asosiy identifikatsiya
    employee_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Hodim ID"),
        help_text=_("Hikvision qurilmasidagi unikal identifikator")
    )
    personnel_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("Tabel raqami"),
        help_text=_("Ichki tabel raqami")
    )

    # Shaxsiy ma'lumotlar
    first_name = models.CharField(
        max_length=100,
        verbose_name=_("Ism"),
        help_text=_("Hodimning ismi")
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name=_("Familiya"),
        help_text=_("Hodimning familiyasi")
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Otasining ismi"),
        help_text=_("Hodimning otasining ismi")
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Tug'ilgan sana"),
        help_text=_("Hodimning tug'ilgan sanasi")
    )
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True,
        null=True,
        verbose_name=_("Jinsi"),
        help_text=_("Hodimning jinsi")
    )
    photo = models.ImageField(
        upload_to='employees/photos/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_("Rasm"),
        help_text=_("Hodimning rasmi")
    )

    # Aloqa ma'lumotlari
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[phone_validator],
        verbose_name=_("Telefon"),
        help_text=_("Asosiy telefon raqami")
    )
    personal_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[phone_validator],
        verbose_name=_("Shaxsiy telefon"),
        help_text=_("Qo'shimcha shaxsiy telefon")
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_("Email"),
        help_text=_("Ish email manzili")
    )
    personal_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_("Shaxsiy email"),
        help_text=_("Shaxsiy email manzili")
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Manzil"),
        help_text=_("Yashash manzili")
    )
    emergency_contact_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Favqulodda aloqa (ism)"),
        help_text=_("Favqulodda holatlarda bog'lanish uchun shaxs")
    )
    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[phone_validator],
        verbose_name=_("Favqulodda aloqa (telefon)"),
        help_text=_("Favqulodda aloqa telefon raqami")
    )

    # Ish ma'lumotlari
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
        verbose_name=_("Ish turi"),
        help_text=_("To'liq stavka, yarim stavka va h.k.")
    )
    hire_date = models.DateField(
        verbose_name=_("Ishga qabul sanasi"),
        help_text=_("Ishga qabul qilingan sana")
    )
    probation_end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Sinov muddati tugashi"),
        help_text=_("Sinov muddati qachon tugaydi")
    )
    termination_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Bo'shatilgan sana"),
        help_text=_("Ishdan bo'shatilgan sana (agar mavjud bo'lsa)")
    )
    termination_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Bo'shatilish sababi"),
        help_text=_("Ishdan bo'shatilish sababi")
    )

    # Ish vaqti sozlamalari
    work_start_time = models.TimeField(
        default=time(9, 0),
        verbose_name=_("Ish boshlanish vaqti"),
        help_text=_("Kunlik ish boshlanish vaqti")
    )
    work_end_time = models.TimeField(
        default=time(18, 0),
        verbose_name=_("Ish tugash vaqti"),
        help_text=_("Kunlik ish tugash vaqti")
    )
    use_branch_schedule = models.BooleanField(
        default=True,
        verbose_name=_("Filial jadvalini ishlatish"),
        help_text=_("True bo'lsa, filialning standart ish vaqti ishlatiladi")
    )

    # Holat
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_("Holat"),
        help_text=_("Hodimning joriy holati")
    )

    # Qo'shimcha ma'lumotlar
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Izohlar"),
        help_text=_("Qo'shimcha ma'lumotlar")
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
        verbose_name = _("Hodim")
        verbose_name_plural = _("Hodimlar")
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['employee_id'], name='emp_id_idx'),
            models.Index(fields=['status'], name='emp_status_idx'),
            models.Index(fields=['branch'], name='emp_branch_idx'),
            models.Index(fields=['department'], name='emp_dept_idx'),
            models.Index(fields=['last_name', 'first_name'], name='emp_name_idx'),
        ]

    def __str__(self) -> str:
        """
        Hodimni string sifatida qaytarish.

        Returns:
            str: Familiya, ism va ID
        """
        return f"{self.last_name} {self.first_name} ({self.employee_id})"

    def __repr__(self) -> str:
        """
        Debug uchun to'liq ma'lumot.

        Returns:
            str: Model va asosiy ma'lumotlar
        """
        return f"<Employee(id={self.pk}, emp_id='{self.employee_id}', name='{self.full_name}')>"

    @property
    def full_name(self) -> str:
        """
        Hodimning to'liq ismini qaytarish.

        Returns:
            str: Familiya, ism va otasining ismi

        Example:
            >>> emp.full_name
            "Valiyev Ali Karimovich"
        """
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)

    @property
    def short_name(self) -> str:
        """
        Qisqa ism (Familiya va ism bosh harfi).

        Returns:
            str: "Valiyev A."
        """
        return f"{self.last_name} {self.first_name[0]}."

    @property
    def organization(self):
        """
        Tegishli tashkilotni qaytarish.

        Returns:
            Organization: Tashkilot obyekti
        """
        return self.branch.organization

    @property
    def effective_work_start(self) -> time:
        """
        Haqiqiy ish boshlanish vaqtini qaytarish.

        Returns:
            time: Individual yoki filial vaqti
        """
        if self.use_branch_schedule:
            return self.branch.work_start_time
        return self.work_start_time

    @property
    def effective_work_end(self) -> time:
        """
        Haqiqiy ish tugash vaqtini qaytarish.

        Returns:
            time: Individual yoki filial vaqti
        """
        if self.use_branch_schedule:
            return self.branch.work_end_time
        return self.work_end_time

    @property
    def is_working_now(self) -> bool:
        """
        Hodim hozir ish vaqtida yoki yo'qligini tekshirish.

        Returns:
            bool: True agar hozir ish vaqti bo'lsa
        """
        if self.status != self.Status.ACTIVE:
            return False

        now = timezone.localtime().time()
        return self.effective_work_start <= now <= self.effective_work_end

    @property
    def years_of_service(self) -> float:
        """
        Hodim ishlagan yillar sonini hisoblash.

        Returns:
            float: Ishlagan yillar soni

        Example:
            >>> emp.years_of_service
            2.5
        """
        end_date = self.termination_date or timezone.now().date()
        delta = end_date - self.hire_date
        return round(delta.days / 365.25, 1)

    @property
    def age(self) -> Optional[int]:
        """
        Hodim yoshini hisoblash.

        Returns:
            int | None: Yosh yoki None agar tug'ilgan sana yo'q bo'lsa
        """
        if not self.birth_date:
            return None
        today = timezone.now().date()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    @property
    def is_on_probation(self) -> bool:
        """
        Sinov muddatida yoki yo'qligini tekshirish.

        Returns:
            bool: True agar sinov muddatida bo'lsa
        """
        if not self.probation_end_date:
            return False
        return timezone.now().date() <= self.probation_end_date

    def get_subordinates(self, direct_only: bool = True):
        """
        Bo'ysunuvchilarni olish.

        Args:
            direct_only: True bo'lsa, faqat bevosita bo'ysunuvchilar

        Returns:
            QuerySet: Employee yozuvlari
        """
        if direct_only:
            return self.subordinates.filter(status=self.Status.ACTIVE)

        # Rekursiv barcha bo'ysunuvchilar
        all_subordinates = list(self.subordinates.filter(status=self.Status.ACTIVE))
        for sub in list(all_subordinates):
            all_subordinates.extend(sub.get_subordinates(direct_only=False))
        return all_subordinates

    def get_attendance_for_date(self, date) -> Optional['DailyAttendance']:
        """
        Berilgan sana uchun davomat ma'lumotini olish.

        Args:
            date: Tekshiriladigan sana

        Returns:
            DailyAttendance | None: Davomat yozuvi yoki None
        """
        return self.daily_attendances.filter(date=date).first()

    def get_monthly_stats(self, year: int, month: int) -> dict:
        """
        Oylik davomat statistikasini olish.

        Args:
            year: Yil
            month: Oy

        Returns:
            dict: Statistika ma'lumotlari
        """
        from django.db.models import Sum, Count

        attendances = self.daily_attendances.filter(
            date__year=year,
            date__month=month
        )

        stats = attendances.aggregate(
            total_days=Count('id'),
            present_days=Count('id', filter=models.Q(
                status__in=['present', 'late', 'early_leave', 'late_and_early']
            )),
            late_days=Count('id', filter=models.Q(
                status__in=['late', 'late_and_early']
            )),
            absent_days=Count('id', filter=models.Q(status='absent')),
            total_late_minutes=Sum('late_minutes'),
            total_overtime_minutes=Sum('overtime_minutes'),
            total_work_minutes=Sum('total_work_minutes'),
        )

        return {
            'total_days': stats['total_days'] or 0,
            'present_days': stats['present_days'] or 0,
            'late_days': stats['late_days'] or 0,
            'absent_days': stats['absent_days'] or 0,
            'total_late_minutes': stats['total_late_minutes'] or 0,
            'total_overtime_minutes': stats['total_overtime_minutes'] or 0,
            'total_work_minutes': stats['total_work_minutes'] or 0,
        }

    def terminate(self, termination_date=None, reason: str = None) -> None:
        """
        Hodimni ishdan bo'shatish.

        Args:
            termination_date: Bo'shatilgan sana (default: bugun)
            reason: Bo'shatilish sababi

        Side Effects:
            status va termination_date maydonlari o'zgaradi
        """
        self.status = self.Status.TERMINATED
        self.termination_date = termination_date or timezone.now().date()
        if reason:
            self.termination_reason = reason
        self.save()

    def transfer(self, new_branch=None, new_department=None, new_position=None) -> None:
        """
        Hodimni ko'chirish (transfer).

        Args:
            new_branch: Yangi filial
            new_department: Yangi bo'lim
            new_position: Yangi lavozim

        Side Effects:
            branch, department va/yoki position maydonlari o'zgaradi
        """
        if new_branch:
            self.branch = new_branch
        if new_department:
            self.department = new_department
        if new_position:
            self.position = new_position
        self.save()

    def clean(self) -> None:
        """
        Model validatsiyasi.

        Raises:
            ValidationError: Noto'g'ri bog'lanishlar bo'lsa
        """
        # Bo'lim filialga tegishli bo'lishi kerak
        if self.department and self.department.branch_id != self.branch_id:
            raise ValidationError({
                'department': _("Bo'lim boshqa filialga tegishli")
            })

        # Lavozim bo'limga tegishli bo'lishi kerak
        if self.position and self.department:
            if self.position.department_id != self.department_id:
                raise ValidationError({
                    'position': _("Lavozim boshqa bo'limga tegishli")
                })

        # Rahbar bir xil tashkilotga tegishli bo'lishi kerak
        if self.manager:
            if self.manager.branch.organization_id != self.branch.organization_id:
                raise ValidationError({
                    'manager': _("Rahbar boshqa tashkilotga tegishli")
                })


class EmployeeDocument(models.Model):
    """
    Hodim hujjatlari modeli.

    Hodimga tegishli barcha hujjatlarni saqlash uchun.
    Passport, diploma, sertifikatlar va boshqalar.

    Attributes:
        employee (Employee): Hodim
        document_type (str): Hujjat turi
        title (str): Hujjat nomi
        document_number (str): Hujjat raqami
        file (FileField): Hujjat fayli
        issue_date (date): Berilgan sana
        expiry_date (date): Amal qilish muddati
        issued_by (str): Kim tomonidan berilgan
        notes (str): Izohlar

    Properties:
        is_expired: Muddati o'tganmi
        days_until_expiry: Muddatgacha qolgan kunlar

    Example:
        >>> doc = EmployeeDocument.objects.create(
        ...     employee=emp,
        ...     document_type='passport',
        ...     title='Passport',
        ...     document_number='AA1234567'
        ... )
    """

    class DocumentType(models.TextChoices):
        """
        Hujjat turlari.
        """
        PASSPORT = 'passport', _('Passport')
        ID_CARD = 'id_card', _('ID karta')
        DIPLOMA = 'diploma', _('Diplom')
        CERTIFICATE = 'certificate', _('Sertifikat')
        CONTRACT = 'contract', _('Shartnoma')
        LICENSE = 'license', _('Litsenziya')
        MEDICAL = 'medical', _('Tibbiy ma\'lumotnoma')
        OTHER = 'other', _('Boshqa')

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_("Hodim")
    )
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        default=DocumentType.OTHER,
        verbose_name=_("Hujjat turi")
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("Hujjat nomi"),
        help_text=_("Hujjatning qisqa nomi")
    )
    document_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Hujjat raqami"),
        help_text=_("Hujjatning seriya va raqami")
    )
    file = models.FileField(
        upload_to='employees/documents/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_("Fayl"),
        help_text=_("Hujjat fayli (PDF, JPG, PNG)")
    )
    issue_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Berilgan sana"),
        help_text=_("Hujjat qachon berilgan")
    )
    expiry_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Amal qilish muddati"),
        help_text=_("Hujjat qachongacha amal qiladi")
    )
    issued_by = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Kim tomonidan berilgan"),
        help_text=_("Hujjatni bergan organ/tashkilot")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Izohlar")
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Yuklangan vaqt")
    )

    class Meta:
        verbose_name = _("Hodim hujjati")
        verbose_name_plural = _("Hodim hujjatlari")
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['employee', 'document_type'], name='doc_emp_type_idx'),
            models.Index(fields=['expiry_date'], name='doc_expiry_idx'),
        ]

    def __str__(self) -> str:
        """
        Hujjatni string sifatida qaytarish.

        Returns:
            str: Hodim va hujjat nomi
        """
        return f"{self.employee.short_name} - {self.title}"

    @property
    def is_expired(self) -> bool:
        """
        Hujjat muddati o'tganligini tekshirish.

        Returns:
            bool: True agar muddat o'tgan bo'lsa
        """
        if not self.expiry_date:
            return False
        return self.expiry_date < timezone.now().date()

    @property
    def days_until_expiry(self) -> Optional[int]:
        """
        Muddatgacha qolgan kunlar soni.

        Returns:
            int | None: Kunlar soni yoki None
        """
        if not self.expiry_date:
            return None
        delta = self.expiry_date - timezone.now().date()
        return delta.days

    @property
    def is_expiring_soon(self) -> bool:
        """
        Muddat tez orada tugashini tekshirish (30 kun).

        Returns:
            bool: True agar 30 kundan kam qolgan bo'lsa
        """
        days = self.days_until_expiry
        if days is None:
            return False
        return 0 < days <= 30
