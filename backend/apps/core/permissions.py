"""
API Permissions va Decorators.

TZ talabiga mos permission system.
"""

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from functools import wraps
from django.http import JsonResponse


class IsEmployee(permissions.BasePermission):
    """Oddiy xodim huquqi."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_employee


class IsManager(permissions.BasePermission):
    """Bo'lim boshlig'i huquqi."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_manager


class IsAccountant(permissions.BasePermission):
    """Buxgalter huquqi."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_accountant


class IsChiefAccountant(permissions.BasePermission):
    """Glavniy buxgalter huquqi."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_chief_accountant


class IsSuperuser(permissions.BasePermission):
    """Administrator huquqi."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser_role


class CanEditSalary(permissions.BasePermission):
    """
    Ish haqini tahrirlash huquqi.

    TZ talabi:
    - Employee: Yo'q
    - Manager: Faqat o'z bo'limidagi hodimlar
    - Accountant: Hamma (izoh bilan)
    - Chief Accountant: Hamma
    - Superuser: Hamma
    """

    def has_object_permission(self, request, view, obj):
        """
        Obyekt darajasida permission tekshirish.

        obj - bu SalaryCalculation yoki Employee obyekti bo'lishi mumkin.
        """
        user = request.user

        # GET request - ko'rish huquqi
        if request.method == 'GET':
            if hasattr(obj, 'employee'):
                employee = obj.employee
            else:
                employee = obj

            return user.can_view_salary_for_employee(employee)

        # PUT/PATCH/DELETE - tahrirlash huquqi
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            if hasattr(obj, 'employee'):
                employee = obj.employee
            else:
                employee = obj

            return user.can_edit_salary_for_employee(employee)

        return False


class CanApproveSalary(permissions.BasePermission):
    """
    Ish haqini tasdiqlash huquqi.

    Faqat Accountant, Chief Accountant va Superuser.
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (
            user.is_accountant or
            user.is_chief_accountant or
            user.is_superuser_role
        )


class CanFinalApprove(permissions.BasePermission):
    """
    Yakuniy tasdiqlash va 1C ga yuklash huquqi.

    Faqat Chief Accountant va Superuser.
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (
            user.is_chief_accountant or
            user.is_superuser_role
        )


# Decorator funksiyalar

def require_role(*roles):
    """
    View uchun rol talab qiladigan decorator.

    Usage:
        @require_role('manager', 'accountant')
        @api_view(['GET'])
        def my_view(request):
            ...

    Args:
        *roles: Ruxsat berilgan rollar ro'yxati
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({
                    'error': 'Authentication required'
                }, status=401)

            user_role = request.user.role
            if user_role not in roles and not request.user.is_superuser_role:
                return JsonResponse({
                    'error': f'Permission denied. Required roles: {", ".join(roles)}'
                }, status=403)

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_permission(permission_name):
    """
    View uchun permission talab qiladigan decorator.

    Usage:
        @require_permission('can_edit_salary')
        @api_view(['POST'])
        def edit_salary(request):
            ...

    Args:
        permission_name: Permission nomi
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({
                    'error': 'Authentication required'
                }, status=401)

            if not request.user.has_permission(permission_name):
                return JsonResponse({
                    'error': f'Permission denied: {permission_name}'
                }, status=403)

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def check_department_access(view_func):
    """
    Manager uchun faqat o'z bo'limiga dostup beruvchi decorator.

    Usage:
        @check_department_access
        @api_view(['GET'])
        def department_employees(request, department_id):
            # department_id o'z bo'limiga tegishli ekanligini tekshiradi
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'error': 'Authentication required'
            }, status=401)

        # Superuser va Chief/Accountant lar hammaga dostup
        if (request.user.is_superuser_role or
            request.user.is_chief_accountant or
            request.user.is_accountant):
            return view_func(request, *args, **kwargs)

        # Manager - faqat o'z bo'limi
        if request.user.is_manager:
            department_id = kwargs.get('department_id') or kwargs.get('pk')
            if department_id:
                managed_dept = request.user.managed_department
                if managed_dept and str(managed_dept.id) == str(department_id):
                    return view_func(request, *args, **kwargs)
                else:
                    return JsonResponse({
                        'error': 'You can only access your own department'
                    }, status=403)

        return JsonResponse({
            'error': 'Permission denied'
        }, status=403)

    return wrapper


def require_comment_for_edit(view_func):
    """
    Tahrirlash uchun comment majburiy qiladigan decorator.

    TZ talabi: Buxgalter va Managerlar tahrirlashda izoh qoldirishi shart.

    Usage:
        @require_comment_for_edit
        @api_view(['PUT', 'PATCH'])
        def update_salary(request, pk):
            comment = request.data.get('comment')
            # comment mavjudligini tekshiradi
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Faqat PUT/PATCH metodlari uchun
        if request.method in ['PUT', 'PATCH']:
            comment = request.data.get('comment') or request.data.get('notes')

            # Superuser uchun comment majburiy emas (lekin tavsiya etiladi)
            if request.user.is_superuser_role:
                return view_func(request, *args, **kwargs)

            # Boshqa rollar uchun comment MAJBURIY
            if not comment or not comment.strip():
                return JsonResponse({
                    'error': 'Comment is required for editing (TZ requirement)',
                    'field': 'comment'
                }, status=400)

        return view_func(request, *args, **kwargs)

    return wrapper


class RoleBasedPermission(permissions.BasePermission):
    """
    Universal role-based permission class.

    Usage in ViewSet:
        permission_classes = [RoleBasedPermission]
        role_permissions = {
            'list': ['employee', 'manager', 'accountant', 'chief_accountant', 'superuser'],
            'retrieve': ['employee', 'manager', 'accountant', 'chief_accountant', 'superuser'],
            'create': ['manager', 'accountant', 'chief_accountant', 'superuser'],
            'update': ['manager', 'accountant', 'chief_accountant', 'superuser'],
            'destroy': ['superuser'],
        }
    """

    def has_permission(self, request, view):
        """Permission tekshirish."""
        if not request.user or not request.user.is_authenticated:
            return False

        # ViewSet'da role_permissions mavjudligini tekshirish
        if not hasattr(view, 'role_permissions'):
            # Agar belgilanmagan bo'lsa, authenticated user lar uchun ruxsat
            return True

        # Action nomini olish
        action = view.action if hasattr(view, 'action') else None
        if not action:
            return True

        # Action uchun ruxsat berilgan rollarni olish
        allowed_roles = view.role_permissions.get(action, [])

        # Superuser har doim ruxsat oladi
        if request.user.is_superuser_role:
            return True

        # Foydalanuvchi roli ruxsat berilgan rollar ichida bormi
        return request.user.role in allowed_roles


def log_action(action_name):
    """
    API action'ni audit log'ga yozadigan decorator.

    Usage:
        @log_action('salary_updated')
        @api_view(['PUT'])
        def update_salary(request, pk):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # View'ni bajarish
            response = view_func(request, *args, **kwargs)

            # Audit log yozish (agar success bo'lsa)
            if response.status_code in [200, 201, 204]:
                try:
                    from apps.core.models import log_model_change

                    # Request'dan ma'lumotlarni olish
                    ip_address = request.META.get('REMOTE_ADDR')
                    user_agent = request.META.get('HTTP_USER_AGENT')
                    comment = request.data.get('comment', f'Action: {action_name}')

                    # Log yozish (instance kerak bo'ladi, shuning uchun bu yerda faqat marker)
                    # Actual logging view ichida amalga oshiriladi
                    request._audit_action = action_name
                    request._audit_ip = ip_address
                    request._audit_user_agent = user_agent

                except Exception as e:
                    # Audit log xatosi asosiy jarayonga ta'sir qilmasligi kerak
                    pass

            return response
        return wrapper
    return decorator
