"""
Accounts Application Models.

Bu modul foydalanuvchi autentifikatsiyasi va avtorizatsiyasi uchun
modellarni o'z ichiga oladi. Django'ning AbstractUser modelidan
meros olib, qo'shimcha maydonlar va funksionallik qo'shilgan.

Modellar:
    - User: Kengaytirilgan foydalanuvchi modeli
    - UserAccess: Foydalanuvchi huquqlari (qaysi tashkilot/filial/bo'limga kirishishi)

Access Control Ierarxiyasi:
    - ADMIN: Barcha tashkilotlarga to'liq dostup
    - HR/VIEWER: Faqat UserAccess orqali belgilangan joylarga dostup
    - Hodim: Agar User.employee bog'langan bo'lsa, faqat o'z ma'lumotlariga dostup

Example:
    >>> from apps.accounts.models import User, UserAccess
    >>> user = User.objects.create_user(
    ...     username='hr_manager',
    ...     email='hr@example.com',
    ...     password='secure_password',
    ...     role='hr'
    ... )
    >>> # Foydalanuvchiga Toshkent filialiga dostup berish
    >>> UserAccess.objects.create(
    ...     user=user,
    ...     access_type='branch',
    ...     branch=tashkent_branch,
    ...     can_edit=True
    ... )
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from apps.employees.models import Employee
    from apps.core.models import Organization, Branch


class User(AbstractUser):
    """
    Kengaytirilgan foydalanuvchi modeli.

    Django'ning standart User modeliga qo'shimcha maydonlar qo'shilgan:
    - role: Foydalanuvchi roli (admin, hr, viewer)
    - phone: Telefon raqami
    - avatar: Profil rasmi
    - is_verified: Email tasdiqlangan yoki yo'q
    - last_activity: Oxirgi faollik vaqti
    - employee: Agar foydalanuvchi hodim bo'lsa, bog'langan hodim

    Access Control:
        - Admin: Barcha resurslarga to'liq dostup
        - HR/Viewer: UserAccess orqali belgilangan tashkilot/filial/bo'limlarga dostup
        - Employee user: Faqat o'z profiliga dostup

    Attributes:
        role (str): Foydalanuvchi roli
        phone (str): Telefon raqami
        avatar (ImageField): Profil rasmi
        is_verified (bool): Email tasdiqlangan holati
        last_activity (datetime): Oxirgi faollik vaqti
        employee (Employee): Bog'langan hodim (agar mavjud bo'lsa)

    Properties:
        is_admin: Admin ekanligini tekshirish
        is_hr: HR manager ekanligini tekshirish
        full_name: To'liq ism

    Methods:
        get_accessible_organizations(): Dostup berilgan tashkilotlar
        get_accessible_branches(): Dostup berilgan filiallar
        get_accessible_departments(): Dostup berilgan bo'limlar
        get_accessible_employees(): Dostup berilgan hodimlar
        has_access_to_employee(employee): Ma'lum hodimga dostup bormi
        has_access_to_branch(branch): Ma'lum filialga dostup bormi

    Example:
        >>> user = User.objects.get(username='hr_tashkent')
        >>> user.is_hr
        True
        >>> user.get_accessible_branches()
        <QuerySet [<Branch: Toshkent Bosh Ofis>]>
    """

    class Role(models.TextChoices):
        """
        Foydalanuvchi rollari.

        Attributes:
            ADMIN: Tizim administratori - barcha huquqlarga ega
            HR: HR menejeri - hodimlar va davomat boshqaruvi
            VIEWER: Ko'ruvchi - faqat o'qish huquqi
        """
        ADMIN = 'admin', _('Administrator')
        HR = 'hr', _('HR Manager')
        VIEWER = 'viewer', _('Viewer')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
        verbose_name=_("Rol"),
        help_text=_("Foydalanuvchining tizimda huquqlari")
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("Telefon"),
        help_text=_("Aloqa uchun telefon raqami")
    )
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_("Avatar"),
        help_text=_("Profil rasmi")
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("Tasdiqlangan"),
        help_text=_("Email manzili tasdiqlangan yoki yo'q")
    )
    last_activity = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Oxirgi faollik"),
        help_text=_("Foydalanuvchining oxirgi faollik vaqti")
    )
    employee = models.OneToOneField(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_account',
        verbose_name=_("Bog'langan hodim"),
        help_text=_("Agar foydalanuvchi hodim bo'lsa, uning profili")
    )

    class Meta:
        verbose_name = _("Foydalanuvchi")
        verbose_name_plural = _("Foydalanuvchilar")
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['role'], name='user_role_idx'),
            models.Index(fields=['is_active'], name='user_active_idx'),
        ]

    def __str__(self) -> str:
        """
        Foydalanuvchini string sifatida qaytarish.

        Returns:
            str: Username va rol ko'rinishida
        """
        return f"{self.username} ({self.get_role_display()})"

    def __repr__(self) -> str:
        """
        Debug uchun to'liq ma'lumot.

        Returns:
            str: Model nomi va asosiy ma'lumotlar
        """
        return f"<User(id={self.pk}, username='{self.username}', role='{self.role}')>"

    @property
    def is_admin(self) -> bool:
        """
        Foydalanuvchi admin ekanligini tekshirish.

        Returns:
            bool: True agar admin bo'lsa
        """
        return self.role == self.Role.ADMIN

    @property
    def is_hr(self) -> bool:
        """
        Foydalanuvchi HR manager ekanligini tekshirish.

        Returns:
            bool: True agar HR manager bo'lsa
        """
        return self.role == self.Role.HR

    @property
    def full_name(self) -> str:
        """
        Foydalanuvchining to'liq ismini qaytarish.

        Returns:
            str: Ism va familiya yoki username
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def has_permission(self, permission: str) -> bool:
        """
        Ma'lum bir ruxsatni tekshirish.

        Args:
            permission: Tekshiriladigan ruxsat nomi

        Returns:
            bool: True agar ruxsat mavjud bo'lsa

        Example:
            >>> user.has_permission('can_edit_employees')
            True
        """
        permission_map = {
            'can_manage_users': [self.Role.ADMIN],
            'can_edit_employees': [self.Role.ADMIN, self.Role.HR],
            'can_view_reports': [self.Role.ADMIN, self.Role.HR, self.Role.VIEWER],
            'can_manage_devices': [self.Role.ADMIN],
            'can_sync_attendance': [self.Role.ADMIN, self.Role.HR],
        }
        allowed_roles = permission_map.get(permission, [])
        return self.role in allowed_roles

    def update_last_activity(self) -> None:
        """
        Oxirgi faollik vaqtini yangilash.

        Side Effects:
            last_activity maydoni hozirgi vaqtga o'zgaradi
        """
        from django.utils import timezone
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])

    def get_accessible_organizations(self):
        """
        Foydalanuvchi dostup qila oladigan tashkilotlarni qaytarish.

        Returns:
            QuerySet: Organization obyektlari

        Example:
            >>> user.get_accessible_organizations()
            <QuerySet [<Organization: Mega Holding>]>
        """
        from apps.core.models import Organization

        # Admin barcha tashkilotlarni ko'radi
        if self.is_admin:
            return Organization.objects.filter(is_active=True)

        # UserAccess orqali dostup berilgan tashkilotlar
        org_ids = self.access_permissions.filter(
            access_type='organization',
            organization__isnull=False
        ).values_list('organization_id', flat=True)

        return Organization.objects.filter(id__in=org_ids, is_active=True)

    def get_accessible_branches(self):
        """
        Foydalanuvchi dostup qila oladigan filiallarni qaytarish.

        Returns:
            QuerySet: Branch obyektlari

        Example:
            >>> user.get_accessible_branches()
            <QuerySet [<Branch: Toshkent Bosh Ofis>, <Branch: Samarqand Filial>]>
        """
        from apps.core.models import Branch

        # Admin barcha filiallarni ko'radi
        if self.is_admin:
            return Branch.objects.filter(is_active=True)

        # UserAccess orqali dostup
        branch_ids = set()

        # 1. To'g'ridan-to'g'ri filialga dostup
        branch_ids.update(
            self.access_permissions.filter(
                access_type='branch',
                branch__isnull=False
            ).values_list('branch_id', flat=True)
        )

        # 2. Tashkilotga dostup bo'lsa, uning barcha filiallari
        org_ids = self.access_permissions.filter(
            access_type='organization',
            organization__isnull=False
        ).values_list('organization_id', flat=True)

        if org_ids:
            branch_ids.update(
                Branch.objects.filter(
                    organization_id__in=org_ids,
                    is_active=True
                ).values_list('id', flat=True)
            )

        return Branch.objects.filter(id__in=branch_ids, is_active=True)

    def get_accessible_departments(self):
        """
        Foydalanuvchi dostup qila oladigan bo'limlarni qaytarish.

        Returns:
            QuerySet: Department obyektlari

        Example:
            >>> user.get_accessible_departments()
            <QuerySet [<Department: IT bo'limi>, <Department: HR bo'limi>]>
        """
        from apps.employees.models import Department

        # Admin barcha bo'limlarni ko'radi
        if self.is_admin:
            return Department.objects.filter(is_active=True)

        dept_ids = set()

        # 1. To'g'ridan-to'g'ri bo'limga dostup
        dept_ids.update(
            self.access_permissions.filter(
                access_type='department',
                department__isnull=False
            ).values_list('department_id', flat=True)
        )

        # 2. Filialga dostup bo'lsa, uning barcha bo'limlari
        accessible_branches = self.get_accessible_branches()
        dept_ids.update(
            Department.objects.filter(
                branch__in=accessible_branches,
                is_active=True
            ).values_list('id', flat=True)
        )

        return Department.objects.filter(id__in=dept_ids, is_active=True)

    def get_accessible_employees(self):
        """
        Foydalanuvchi dostup qila oladigan hodimlarni qaytarish.

        Access ierarxiyasi:
            1. Admin: Barcha hodimlar
            2. Manager (employee bog'langan): O'z qo'l ostidagi hodimlar
            3. UserAccess: Belgilangan tashkilot/filial/bo'limdagi hodimlar

        Returns:
            QuerySet: Employee obyektlari

        Example:
            >>> user.get_accessible_employees()
            <QuerySet [<Employee: Ali Valiyev>, <Employee: Vali Aliyev>]>
        """
        from apps.employees.models import Employee

        # Admin barcha hodimlarni ko'radi
        if self.is_admin:
            return Employee.objects.filter(status='active')

        employee_ids = set()

        # 1. Agar foydalanuvchi o'zi hodim bo'lsa va rahbar bo'lsa
        if self.employee:
            # O'zini qo'shish
            employee_ids.add(self.employee.id)

            # O'z qo'l ostidagi hodimlarni rekursiv olish
            subordinates = self._get_all_subordinates(self.employee)
            employee_ids.update(subordinates)

        # 2. UserAccess orqali dostup berilgan hodimlar
        # Bo'limga dostup
        accessible_depts = self.get_accessible_departments()
        employee_ids.update(
            Employee.objects.filter(
                department__in=accessible_depts,
                status='active'
            ).values_list('id', flat=True)
        )

        # Filialga dostup
        accessible_branches = self.get_accessible_branches()
        employee_ids.update(
            Employee.objects.filter(
                branch__in=accessible_branches,
                status='active'
            ).values_list('id', flat=True)
        )

        return Employee.objects.filter(id__in=employee_ids)

    def _get_all_subordinates(self, manager_employee) -> set:
        """
        Rahbar ostidagi barcha hodimlarni rekursiv olish.

        Args:
            manager_employee: Rahbar hodim obyekti

        Returns:
            set: Barcha qo'l ostidagi hodimlar ID lari

        Example:
            >>> user._get_all_subordinates(employee)
            {12, 15, 18, 22, 25}
        """
        subordinate_ids = set()

        # To'g'ridan-to'g'ri qo'l ostidagilar
        direct_subordinates = manager_employee.subordinates.filter(status='active')

        for subordinate in direct_subordinates:
            subordinate_ids.add(subordinate.id)
            # Rekursiv: har bir qo'l ostidagining ham qo'l ostidagilarini olish
            subordinate_ids.update(self._get_all_subordinates(subordinate))

        return subordinate_ids

    def has_access_to_employee(self, employee) -> bool:
        """
        Ma'lum hodimga dostup borligini tekshirish.

        Args:
            employee: Tekshiriladigan Employee obyekti

        Returns:
            bool: True agar dostup bo'lsa

        Example:
            >>> user.has_access_to_employee(some_employee)
            True
        """
        # Admin barcha hodimlarni ko'radi
        if self.is_admin:
            return True

        # O'zi bo'lsa
        if self.employee and self.employee.id == employee.id:
            return True

        # Dostup berilgan hodimlar ichida bormi
        return employee.id in self.get_accessible_employees().values_list('id', flat=True)

    def has_access_to_branch(self, branch) -> bool:
        """
        Ma'lum filialga dostup borligini tekshirish.

        Args:
            branch: Tekshiriladigan Branch obyekti

        Returns:
            bool: True agar dostup bo'lsa

        Example:
            >>> user.has_access_to_branch(tashkent_branch)
            True
        """
        # Admin barcha filiallarga dostup
        if self.is_admin:
            return True

        # Dostup berilgan filiallar ichida bormi
        return branch.id in self.get_accessible_branches().values_list('id', flat=True)

    def has_access_to_department(self, department) -> bool:
        """
        Ma'lum bo'limga dostup borligini tekshirish.

        Args:
            department: Tekshiriladigan Department obyekti

        Returns:
            bool: True agar dostup bo'lsa

        Example:
            >>> user.has_access_to_department(hr_dept)
            True
        """
        # Admin barcha bo'limlarga dostup
        if self.is_admin:
            return True

        # Dostup berilgan bo'limlar ichida bormi
        return department.id in self.get_accessible_departments().values_list('id', flat=True)


class UserAccess(models.Model):
    """
    Foydalanuvchi dostup huquqlari modeli.

    Bu model orqali foydalanuvchilarga tashkilot/filial/bo'limlarga
    dostup beriladi. Granular (detal) access control tizimi.

    Access turlari:
        - organization: Butun tashkilotga dostup
        - branch: Ma'lum filialga dostup
        - department: Ma'lum bo'limga dostup

    Attributes:
        user (User): Foydalanuvchi
        access_type (str): Dostup turi
        organization (Organization): Tashkilot (agar tur=organization)
        branch (Branch): Filial (agar tur=branch)
        department (Department): Bo'lim (agar tur=department)
        can_view (bool): Ko'rish huquqi
        can_edit (bool): Tahrirlash huquqi
        can_delete (bool): O'chirish huquqi
        granted_by (User): Kim dostup berdi
        granted_at (datetime): Qachon berildi
        expires_at (datetime): Qachon amal qilish muddati tugaydi

    Example:
        >>> # HR ga Toshkent filialiga to'liq dostup berish
        >>> UserAccess.objects.create(
        ...     user=hr_user,
        ...     access_type='branch',
        ...     branch=tashkent_branch,
        ...     can_view=True,
        ...     can_edit=True,
        ...     granted_by=admin_user
        ... )
    """

    class AccessType(models.TextChoices):
        """
        Dostup turlari.

        Attributes:
            ORGANIZATION: Butun tashkilotga dostup
            BRANCH: Ma'lum filialga dostup
            DEPARTMENT: Ma'lum bo'limga dostup
        """
        ORGANIZATION = 'organization', _('Tashkilot')
        BRANCH = 'branch', _('Filial')
        DEPARTMENT = 'department', _("Bo'lim")

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='access_permissions',
        verbose_name=_("Foydalanuvchi"),
        help_text=_("Kimga dostup berilmoqda")
    )
    access_type = models.CharField(
        max_length=20,
        choices=AccessType.choices,
        verbose_name=_("Dostup turi"),
        help_text=_("Qaysi darajada dostup beriladi")
    )

    # Bog'lanishlar (faqat bittasi to'ldiriladi)
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_accesses',
        verbose_name=_("Tashkilot"),
        help_text=_("Dostup beriladigan tashkilot")
    )
    branch = models.ForeignKey(
        'core.Branch',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_accesses',
        verbose_name=_("Filial"),
        help_text=_("Dostup beriladigan filial")
    )
    department = models.ForeignKey(
        'employees.Department',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_accesses',
        verbose_name=_("Bo'lim"),
        help_text=_("Dostup beriladigan bo'lim")
    )

    # Huquqlar
    can_view = models.BooleanField(
        default=True,
        verbose_name=_("Ko'rish"),
        help_text=_("Ma'lumotlarni ko'rish huquqi")
    )
    can_edit = models.BooleanField(
        default=False,
        verbose_name=_("Tahrirlash"),
        help_text=_("Ma'lumotlarni o'zgartirish huquqi")
    )
    can_delete = models.BooleanField(
        default=False,
        verbose_name=_("O'chirish"),
        help_text=_("Ma'lumotlarni o'chirish huquqi")
    )

    # Metadata
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='granted_accesses',
        verbose_name=_("Kim berdi"),
        help_text=_("Dostupni kim berdi")
    )
    granted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Berilgan vaqt"),
        help_text=_("Qachon dostup berildi")
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Amal qilish muddati"),
        help_text=_("Qachon dostup tugaydi (bo'sh bo'lsa - abadiy)")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Faol"),
        help_text=_("Dostup faolmi")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Izoh"),
        help_text=_("Dostup haqida qo'shimcha ma'lumot")
    )

    class Meta:
        verbose_name = _("Foydalanuvchi dostupi")
        verbose_name_plural = _("Foydalanuvchi dostuplari")
        ordering = ['-granted_at']
        indexes = [
            models.Index(fields=['user', 'access_type'], name='useraccess_user_type_idx'),
            models.Index(fields=['is_active'], name='useraccess_active_idx'),
            models.Index(fields=['expires_at'], name='useraccess_expires_idx'),
        ]
        constraints = [
            # Har bir user uchun bir xil joyga faqat bitta dostup
            models.UniqueConstraint(
                fields=['user', 'organization'],
                condition=Q(organization__isnull=False),
                name='unique_user_organization_access'
            ),
            models.UniqueConstraint(
                fields=['user', 'branch'],
                condition=Q(branch__isnull=False),
                name='unique_user_branch_access'
            ),
            models.UniqueConstraint(
                fields=['user', 'department'],
                condition=Q(department__isnull=False),
                name='unique_user_department_access'
            ),
        ]

    def __str__(self) -> str:
        """
        UserAccess string ko'rinishi.

        Returns:
            str: Foydalanuvchi va dostup ob'ekti

        Example:
            >>> str(access)
            "hr_manager -> Toshkent Bosh Ofis (branch)"
        """
        target = self.get_target_display()
        return f"{self.user.username} -> {target} ({self.access_type})"

    def __repr__(self) -> str:
        """
        Debug uchun to'liq ma'lumot.

        Returns:
            str: Model va asosiy parametrlar
        """
        return (
            f"<UserAccess(id={self.pk}, user='{self.user.username}', "
            f"type='{self.access_type}', active={self.is_active})>"
        )

    def get_target_display(self) -> str:
        """
        Dostup ob'ektini string sifatida qaytarish.

        Returns:
            str: Tashkilot/Filial/Bo'lim nomi

        Example:
            >>> access.get_target_display()
            "Mega Holding"
        """
        if self.organization:
            return str(self.organization)
        elif self.branch:
            return str(self.branch)
        elif self.department:
            return str(self.department)
        return "N/A"

    @property
    def is_expired(self) -> bool:
        """
        Dostup muddati tugaganmi tekshirish.

        Returns:
            bool: True agar muddat tugagan bo'lsa
        """
        from django.utils import timezone
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    @property
    def permissions_summary(self) -> str:
        """
        Huquqlar xulosasi.

        Returns:
            str: Qisqacha huquqlar tavsifi

        Example:
            >>> access.permissions_summary
            "Ko'rish, Tahrirlash"
        """
        perms = []
        if self.can_view:
            perms.append("Ko'rish")
        if self.can_edit:
            perms.append("Tahrirlash")
        if self.can_delete:
            perms.append("O'chirish")
        return ", ".join(perms) if perms else "Huquq yo'q"

    def clean(self) -> None:
        """
        Model validatsiyasi.

        Raises:
            ValidationError: Noto'g'ri qiymatlar bo'lsa
        """
        from django.core.exceptions import ValidationError

        # Access type ga mos ob'ekt to'ldirilgan bo'lishi kerak
        if self.access_type == self.AccessType.ORGANIZATION and not self.organization:
            raise ValidationError({
                'organization': _("Access type 'organization' bo'lsa, organization to'ldirilishi kerak")
            })
        elif self.access_type == self.AccessType.BRANCH and not self.branch:
            raise ValidationError({
                'branch': _("Access type 'branch' bo'lsa, branch to'ldirilishi kerak")
            })
        elif self.access_type == self.AccessType.DEPARTMENT and not self.department:
            raise ValidationError({
                'department': _("Access type 'department' bo'lsa, department to'ldirilishi kerak")
            })

        # Faqat bitta ob'ekt to'ldirilishi kerak
        filled_count = sum([
            bool(self.organization),
            bool(self.branch),
            bool(self.department)
        ])
        if filled_count > 1:
            raise ValidationError(
                _("Faqat bitta ob'ekt (organization, branch yoki department) to'ldirilishi mumkin")
            )

    def save(self, *args, **kwargs) -> None:
        """
        UserAccess saqlash.

        Note:
            full_clean() avtomatik chaqiriladi validatsiya uchun
        """
        self.full_clean()
        super().save(*args, **kwargs)
