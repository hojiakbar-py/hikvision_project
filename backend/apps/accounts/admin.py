"""
Admin configuration for accounts app.

Bu modul User va UserAccess modellarini Django admin panelida
boshqarish uchun konfiguratsiyani o'z ichiga oladi.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserAccess


class UserAccessInline(admin.TabularInline):
    """
    User admin ichida dostuplarni ko'rsatish uchun inline.

    Bu orqali foydalanuvchiga dostup berilayotgan joylarni
    bir sahifada ko'rish va tahrirlash mumkin.
    """
    model = UserAccess
    fk_name = 'user'  # UserAccess modelida ikkita User FK bor (user va granted_by)
    extra = 1
    fields = [
        'access_type',
        'organization',
        'branch',
        'department',
        'can_view',
        'can_edit',
        'can_delete',
        'is_active',
        'expires_at'
    ]
    autocomplete_fields = ['organization', 'branch', 'department']


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Kengaytirilgan User admin konfiguratsiyasi.

    Features:
        - Inline UserAccess boshqaruvi
        - Employee bog'lanish
        - Role-based filtering
        - Last activity tracking
    """
    list_display = [
        'username',
        'email',
        'full_name',
        'role',
        'employee',
        'is_active',
        'last_activity'
    ]
    list_filter = ['role', 'is_active', 'is_staff', 'is_verified']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    autocomplete_fields = ['employee']

    fieldsets = UserAdmin.fieldsets + (
        (_('Rol va Huquqlar'), {
            'fields': ('role', 'is_verified')
        }),
        (_('Qo\'shimcha Ma\'lumotlar'), {
            'fields': ('phone', 'avatar', 'employee', 'last_activity')
        }),
    )

    inlines = [UserAccessInline]

    def full_name(self, obj):
        """To'liq ism ko'rsatish."""
        return obj.full_name
    full_name.short_description = _("To'liq ism")


@admin.register(UserAccess)
class UserAccessAdmin(admin.ModelAdmin):
    """
    UserAccess admin konfiguratsiyasi.

    Foydalanuvchi dostuplarini boshqarish uchun admin panel.
    """
    list_display = [
        'user',
        'access_type',
        'get_target',
        'permissions_summary',
        'is_active',
        'granted_by',
        'granted_at',
        'expires_at'
    ]
    list_filter = [
        'access_type',
        'is_active',
        'can_view',
        'can_edit',
        'can_delete',
        'granted_at'
    ]
    search_fields = [
        'user__username',
        'user__email',
        'organization__name',
        'branch__name',
        'department__name'
    ]
    autocomplete_fields = ['user', 'organization', 'branch', 'department', 'granted_by']
    date_hierarchy = 'granted_at'

    fieldsets = (
        (_('Asosiy Ma\'lumotlar'), {
            'fields': ('user', 'access_type')
        }),
        (_('Dostup Ob\'ekti'), {
            'fields': ('organization', 'branch', 'department'),
            'description': _("Faqat bitta ob'ektni tanlang (access type ga mos)")
        }),
        (_('Huquqlar'), {
            'fields': ('can_view', 'can_edit', 'can_delete')
        }),
        (_('Metadata'), {
            'fields': ('granted_by', 'expires_at', 'is_active', 'notes'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['granted_at']

    def get_target(self, obj):
        """Dostup ob'ektini ko'rsatish."""
        return obj.get_target_display()
    get_target.short_description = _("Dostup Ob'ekti")

    def save_model(self, request, obj, form, change):
        """Saqlashda granted_by ni avtomatik to'ldirish."""
        if not change:  # Yangi yaratilayotgan bo'lsa
            obj.granted_by = request.user
        super().save_model(request, obj, form, change)
