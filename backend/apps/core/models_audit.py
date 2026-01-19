"""
Audit va History modellari.

TZ talabi:
Har bir o'zgarish uchun majburiy:
- Kim o'zgartirdi
- Sana/vaqt
- Qaysi maydon
- Eski qiymat
- Yangi qiymat
- Izoh

History o'chirilmaydi va tahrirlanmaydi.
"""

from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
import json


class AuditLog(models.Model):
    """
    Universal audit log modeli.

    Har qanday model o'zgarishini yozib boradi.
    TZ talabi bo'yicha: History o'chirilmaydi va tahrirlanmaydi.

    Attributes:
        content_type: Qaysi model
        object_id: Qaysi obyekt
        content_object: Generic foreign key
        action: Qanday harakat (create/update/delete)
        user: Kim bajardi
        timestamp: Qachon
        field_changes: Maydon o'zgarishlari (JSON)
        comment: Majburiy izoh
        ip_address: IP manzil
        user_agent: Brauzer ma'lumoti

    Example:
        >>> AuditLog.objects.create(
        ...     content_object=salary_record,
        ...     action='update',
        ...     user=request.user,
        ...     field_changes={
        ...         'calculated_salary': {
        ...             'old': 5000000,
        ...             'new': 5500000
        ...         }
        ...     },
        ...     comment="Manager tomonidan tuzatildi"
        ... )
    """

    class Action(models.TextChoices):
        """Harakat turlari."""
        CREATE = 'create', _('Yaratildi')
        UPDATE = 'update', _('O\'zgartirildi')
        DELETE = 'delete', _('O\'chirildi')
        SUBMIT = 'submit', _('Yuborildi')
        APPROVE = 'approve', _('Tasdiqlandi')
        REJECT = 'reject', _('Rad etildi')
        LOCK = 'lock', _('Bloklandi')
        UNLOCK = 'unlock', _('Blok ochildi')

    # Generic Foreign Key - har qanday modelga bog'lanish
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Model turi")
    )
    object_id = models.PositiveIntegerField(
        verbose_name=_("Obyekt ID")
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    # Kim va qachon
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name=_("Foydalanuvchi"),
        help_text=_("Kim o'zgartirdi")
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name=_("Vaqt"),
        help_text=_("O'zgarish vaqti")
    )

    # Nima qilindi
    action = models.CharField(
        max_length=20,
        choices=Action.choices,
        verbose_name=_("Harakat"),
        help_text=_("Qanday harakat bajarildi")
    )

    # Qaysi maydonlar o'zgardi (JSON format)
    field_changes = models.JSONField(
        default=dict,
        verbose_name=_("Maydon o'zgarishlari"),
        help_text=_("O'zgargan maydonlar va ularning eski/yangi qiymatlari")
    )

    # Majburiy izoh (TZ talabi)
    comment = models.TextField(
        verbose_name=_("Izoh"),
        help_text=_("O'zgarish sababi (MAJBURIY)")
    )

    # Qo'shimcha metadata
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("IP manzil")
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Brauzer ma'lumoti")
    )

    class Meta:
        verbose_name = _("Audit log")
        verbose_name_plural = _("Audit logs")
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['content_type', 'object_id'], name='audit_content_idx'),
            models.Index(fields=['user'], name='audit_user_idx'),
            models.Index(fields=['timestamp'], name='audit_timestamp_idx'),
            models.Index(fields=['action'], name='audit_action_idx'),
        ]
        # TZ TALABI: History o'chirilmaydi va tahrirlanmaydi
        permissions = [
            ("view_audit_log", "Can view audit logs"),
            # O'chirish va tahrirlash huquqi yo'q!
        ]

    def __str__(self) -> str:
        """String ko'rinishi."""
        return f"{self.user} - {self.get_action_display()} - {self.timestamp}"

    def __repr__(self) -> str:
        """Debug uchun."""
        return (
            f"<AuditLog(id={self.pk}, user='{self.user}', "
            f"action='{self.action}', time='{self.timestamp}')>"
        )

    def get_field_changes_display(self) -> str:
        """
        Maydon o'zgarishlarini odam o'qiy oladigan formatda qaytarish.

        Returns:
            str: Formatlanmiş o'zgarishlar

        Example:
            >>> log.get_field_changes_display()
            "calculated_salary: 5000000 → 5500000\nstatus: draft → submitted"
        """
        if not self.field_changes:
            return "Maydon o'zgarishlari yo'q"

        lines = []
        for field, changes in self.field_changes.items():
            if isinstance(changes, dict) and 'old' in changes and 'new' in changes:
                old_val = changes['old']
                new_val = changes['new']
                lines.append(f"{field}: {old_val} → {new_val}")
            else:
                lines.append(f"{field}: {changes}")

        return "\n".join(lines)

    @property
    def change_summary(self) -> str:
        """
        O'zgarish xulosasi.

        Returns:
            str: Qisqa xulosa
        """
        field_count = len(self.field_changes)
        return f"{field_count} ta maydon o'zgartirildi"

    def save(self, *args, **kwargs):
        """
        TZ TALABI: Auditni saqlaganda hech qanday o'zgartirish qilinmasligi kerak.
        Faqat yangi yozuv qo'shish mumkin.
        """
        if self.pk:
            # Agar ID mavjud bo'lsa, bu update urinishi
            # TZ talabi: History tahrirlanmaydi!
            raise ValueError("Audit log yozuvlarini tahrirlash mumkin emas!")

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        TZ TALABI: Audit loglarni o'chirish mumkin emas!
        """
        raise ValueError("Audit log yozuvlarini o'chirish mumkin emas!")


class FieldChangeHistory(models.Model):
    """
    Maydon o'zgarishlari tarixi (detallashtirilgan).

    Har bir maydon o'zgarishi uchun alohida yozuv.
    AuditLog'dan farqi - bu maydon darajasida kuzatish.

    Attributes:
        audit_log: Bog'liq audit log
        field_name: Maydon nomi
        field_verbose_name: Maydon o'qiladigan nomi
        old_value: Eski qiymat (text)
        new_value: Yangi qiymat (text)
        value_type: Qiymat turi (string, integer, decimal, boolean, date, etc.)

    Example:
        >>> FieldChangeHistory.objects.create(
        ...     audit_log=audit,
        ...     field_name='calculated_salary',
        ...     field_verbose_name='Hisoblangan ish haqi',
        ...     old_value='5000000',
        ...     new_value='5500000',
        ...     value_type='decimal'
        ... )
    """

    audit_log = models.ForeignKey(
        AuditLog,
        on_delete=models.CASCADE,
        related_name='field_histories',
        verbose_name=_("Audit log")
    )

    field_name = models.CharField(
        max_length=100,
        verbose_name=_("Maydon nomi"),
        help_text=_("Model maydoni nomi (masalan: 'calculated_salary')")
    )
    field_verbose_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("O'qiladigan nom"),
        help_text=_("Maydonning o'zbekcha nomi")
    )

    old_value = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Eski qiymat")
    )
    new_value = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Yangi qiymat")
    )

    value_type = models.CharField(
        max_length=50,
        default='string',
        verbose_name=_("Qiymat turi"),
        help_text=_("string, integer, decimal, boolean, date, datetime, json")
    )

    class Meta:
        verbose_name = _("Maydon o'zgarish tarixi")
        verbose_name_plural = _("Maydon o'zgarish tarixlari")
        ordering = ['field_name']
        indexes = [
            models.Index(fields=['audit_log'], name='fieldhistory_audit_idx'),
            models.Index(fields=['field_name'], name='fieldhistory_field_idx'),
        ]

    def __str__(self) -> str:
        """String ko'rinishi."""
        return f"{self.field_verbose_name or self.field_name}: {self.old_value} → {self.new_value}"

    def get_typed_old_value(self):
        """Eski qiymatni to'g'ri tipda qaytarish."""
        return self._parse_value(self.old_value)

    def get_typed_new_value(self):
        """Yangi qiymatni to'g'ri tipda qaytarish."""
        return self._parse_value(self.new_value)

    def _parse_value(self, value):
        """Qiymatni tipiga qarab parse qilish."""
        if value is None:
            return None

        if self.value_type == 'integer':
            try:
                return int(value)
            except (ValueError, TypeError):
                return value
        elif self.value_type == 'decimal':
            try:
                from decimal import Decimal
                return Decimal(value)
            except:
                return value
        elif self.value_type == 'boolean':
            return str(value).lower() in ('true', '1', 'yes')
        elif self.value_type == 'json':
            try:
                return json.loads(value)
            except:
                return value
        else:
            return value


# Utility funksiyalar

def log_model_change(
    instance,
    user,
    action: str,
    field_changes: dict = None,
    comment: str = "",
    ip_address: str = None,
    user_agent: str = None
):
    """
    Model o'zgarishini log qilish utility funksiyasi.

    Args:
        instance: O'zgargan model instance
        user: Foydalanuvchi
        action: Harakat ('create', 'update', 'delete', etc.)
        field_changes: O'zgargan maydonlar {field: {'old': x, 'new': y}}
        comment: Izoh (MAJBURIY TZ talabi)
        ip_address: IP manzil
        user_agent: Brauzer

    Returns:
        AuditLog: Yaratilgan audit log

    Example:
        >>> log_model_change(
        ...     instance=salary_record,
        ...     user=request.user,
        ...     action='update',
        ...     field_changes={'status': {'old': 'draft', 'new': 'submitted'}},
        ...     comment="Manager tomonidan tasdiqlashga yuborildi"
        ... )
    """
    if not comment:
        raise ValueError("Izoh (comment) majburiy! TZ talabi.")

    content_type = ContentType.objects.get_for_model(instance)

    audit_log = AuditLog.objects.create(
        content_type=content_type,
        object_id=instance.pk,
        user=user,
        action=action,
        field_changes=field_changes or {},
        comment=comment,
        ip_address=ip_address,
        user_agent=user_agent
    )

    # Detallashtirilgan field history yaratish
    if field_changes:
        for field_name, changes in field_changes.items():
            if isinstance(changes, dict) and 'old' in changes and 'new' in changes:
                # Maydon verbose name olish
                try:
                    field = instance._meta.get_field(field_name)
                    field_verbose = str(field.verbose_name)
                except:
                    field_verbose = field_name

                # Value type aniqlash
                try:
                    field = instance._meta.get_field(field_name)
                    if hasattr(field, 'get_internal_type'):
                        internal_type = field.get_internal_type()
                        type_map = {
                            'IntegerField': 'integer',
                            'DecimalField': 'decimal',
                            'BooleanField': 'boolean',
                            'DateField': 'date',
                            'DateTimeField': 'datetime',
                            'JSONField': 'json',
                        }
                        value_type = type_map.get(internal_type, 'string')
                    else:
                        value_type = 'string'
                except:
                    value_type = 'string'

                FieldChangeHistory.objects.create(
                    audit_log=audit_log,
                    field_name=field_name,
                    field_verbose_name=field_verbose,
                    old_value=str(changes['old']) if changes['old'] is not None else None,
                    new_value=str(changes['new']) if changes['new'] is not None else None,
                    value_type=value_type
                )

    return audit_log


def get_model_history(instance, limit=None):
    """
    Biror model instance ning to'liq tarixini olish.

    Args:
        instance: Model instance
        limit: Maksimal yozuvlar soni

    Returns:
        QuerySet: AuditLog yozuvlari

    Example:
        >>> history = get_model_history(salary_record, limit=10)
        >>> for log in history:
        ...     print(f"{log.user} - {log.action} - {log.timestamp}")
    """
    content_type = ContentType.objects.get_for_model(instance)

    queryset = AuditLog.objects.filter(
        content_type=content_type,
        object_id=instance.pk
    ).select_related('user').prefetch_related('field_histories')

    if limit:
        queryset = queryset[:limit]

    return queryset
