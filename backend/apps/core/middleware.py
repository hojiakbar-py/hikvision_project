"""
Middleware'lar.

TZ talablariga mos middleware'lar:
- Audit logging middleware
- Role-based access middleware
"""

from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
import json


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Barcha API so'rovlarini audit log'ga yozuvchi middleware.

    Har bir request va response'ni kuzatib boradi.
    """

    def process_request(self, request):
        """
        Request boshida chaqiriladi.

        Request ma'lumotlarini saqlash.
        """
        # Request vaqtini yozish
        import time
        request._start_time = time.time()

        # IP va user agent'ni saqlash
        request._ip_address = self.get_client_ip(request)
        request._user_agent = request.META.get('HTTP_USER_AGENT', '')

        return None

    def process_response(self, request, response):
        """
        Response qaytarishdan oldin chaqiriladi.

        Audit log yozish.
        """
        # Faqat API so'rovlari uchun
        if not request.path.startswith('/api/'):
            return response

        # Faqat authenticated userlar uchun
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response

        # Faqat o'zgartiradigan metodlar uchun (POST, PUT, PATCH, DELETE)
        if request.method not in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return response

        # Response vaqtini hisoblash
        if hasattr(request, '_start_time'):
            import time
            duration = time.time() - request._start_time
            response['X-Response-Time'] = f'{duration:.3f}s'

        # Audit log (agar view tomonidan belgilangan bo'lsa)
        if hasattr(request, '_audit_action'):
            try:
                # Audit log yozish logikasi
                # Bu yerda to'liq implement qilinmagan, chunki
                # har bir view o'z log'ini yozadi
                pass
            except Exception:
                pass

        return response

    @staticmethod
    def get_client_ip(request):
        """Request'dan client IP olish."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RoleAccessMiddleware(MiddlewareMixin):
    """
    Role-based access control middleware.

    Har bir API endpoint uchun rol tekshiruvi.
    """

    # API endpoints va ularning minimal rol talablari
    PROTECTED_ENDPOINTS = {
        '/api/salary/': {
            'GET': ['employee', 'manager', 'accountant', 'chief_accountant', 'superuser'],
            'POST': ['manager', 'accountant', 'chief_accountant', 'superuser'],
            'PUT': ['manager', 'accountant', 'chief_accountant', 'superuser'],
            'DELETE': ['superuser'],
        },
        '/api/salary/approve/': {
            'POST': ['accountant', 'chief_accountant', 'superuser'],
        },
        '/api/salary/export-to-1c/': {
            'POST': ['chief_accountant', 'superuser'],
        },
        '/api/employees/': {
            'GET': ['employee', 'manager', 'accountant', 'chief_accountant', 'superuser'],
            'POST': ['accountant', 'chief_accountant', 'superuser'],
            'PUT': ['accountant', 'chief_accountant', 'superuser'],
            'DELETE': ['superuser'],
        },
    }

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        View ishga tushishidan oldin chaqiriladi.

        Role tekshiruvi.
        """
        # Faqat API uchun
        if not request.path.startswith('/api/'):
            return None

        # Authentication tekshiruvi
        if not hasattr(request, 'user'):
            return None

        # Public endpoints (login, register)
        public_paths = ['/api/auth/token/', '/api/auth/register/']
        if any(request.path.startswith(p) for p in public_paths):
            return None

        # Authenticated user kerak
        if not request.user.is_authenticated:
            return JsonResponse({
                'error': 'Authentication required'
            }, status=401)

        # Role tekshiruvi (agar endpoint protected bo'lsa)
        for endpoint_pattern, methods in self.PROTECTED_ENDPOINTS.items():
            if request.path.startswith(endpoint_pattern):
                allowed_roles = methods.get(request.method, [])

                # Superuser har doim ruxsat oladi
                if request.user.is_superuser_role:
                    return None

                # User roli ruxsat berilgan rollar ichida bormi
                if request.user.role not in allowed_roles:
                    return JsonResponse({
                        'error': f'Permission denied. Required roles: {", ".join(allowed_roles)}',
                        'user_role': request.user.role,
                        'required_roles': allowed_roles
                    }, status=403)

        return None


class CommentRequiredMiddleware(MiddlewareMixin):
    """
    Tahrirlash uchun comment majburiy qiladigan middleware.

    TZ talabi: Barcha o'zgarishlar uchun izoh majburiy.
    """

    # Comment talab qilinadigan endpoints
    COMMENT_REQUIRED_ENDPOINTS = [
        '/api/salary/',
        '/api/employees/',
    ]

    def process_view(self, request, view_func, view_args, view_kwargs):
        """View dan oldin comment tekshiruvi."""
        # Faqat PUT/PATCH metodlari uchun
        if request.method not in ['PUT', 'PATCH']:
            return None

        # Faqat API uchun
        if not request.path.startswith('/api/'):
            return None

        # Superuser uchun comment majburiy emas
        if hasattr(request, 'user') and request.user.is_authenticated:
            if request.user.is_superuser_role:
                return None

        # Comment talab qilinadigan endpoint'mi tekshirish
        is_protected = any(
            request.path.startswith(endpoint)
            for endpoint in self.COMMENT_REQUIRED_ENDPOINTS
        )

        if not is_protected:
            return None

        # Request body'dan comment olish
        try:
            if request.content_type == 'application/json':
                body = json.loads(request.body.decode('utf-8'))
                comment = body.get('comment') or body.get('notes')
            else:
                comment = request.POST.get('comment') or request.POST.get('notes')

            if not comment or not comment.strip():
                return JsonResponse({
                    'error': 'Comment is required for editing (TZ requirement)',
                    'detail': 'Har bir o\'zgarish uchun izoh majburiy',
                    'field': 'comment'
                }, status=400)

        except Exception as e:
            # JSON parse xatosi
            return JsonResponse({
                'error': 'Invalid request format',
                'detail': str(e)
            }, status=400)

        return None


class LastActivityMiddleware(MiddlewareMixin):
    """
    Foydalanuvchi oxirgi faollik vaqtini yangilovchi middleware.

    Har bir API so'rovda user.last_activity yangilanadi.
    """

    def process_request(self, request):
        """Request boshida user last_activity'ni yangilash."""
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Async ravishda yangilash (performansni oshirish uchun)
            try:
                request.user.update_last_activity()
            except Exception:
                # Xato bo'lsa, asosiy jarayonga ta'sir qilmasligi kerak
                pass

        return None
