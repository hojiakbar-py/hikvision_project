"""
Core Application Views.

Bu modul Organization va Branch modellarini API orqali
boshqarish uchun ViewSet larni o'z ichiga oladi.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date
from datetime import date, timedelta

from .models import Organization, Branch, OrganizationSettings
from .serializers import (
    OrganizationSerializer,
    BranchSerializer,
    BranchAttendanceStatsSerializer,
    BranchAttendanceSummarySerializer,
    DepartmentAttendanceBreakdownSerializer,
    TopLatecomersSerializer,
    OrganizationSettingsSerializer
)


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    Organization CRUD va statistika API.

    Endpoints:
        GET    /api/organizations/          - Barcha tashkilotlar
        POST   /api/organizations/          - Yangi tashkilot yaratish
        GET    /api/organizations/{id}/     - Bitta tashkilot
        PUT    /api/organizations/{id}/     - Tashkilotni yangilash
        DELETE /api/organizations/{id}/     - Tashkilotni o'chirish
    """

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Foydalanuvchi dostup qila oladigan tashkilotlarni qaytarish.
        """
        user = self.request.user

        if user.is_admin:
            return Organization.objects.all()

        # UserAccess orqali dostup berilgan tashkilotlar
        return user.get_accessible_organizations()


class BranchViewSet(viewsets.ModelViewSet):
    """
    Branch CRUD va davomat statistikasi API.

    Endpoints:
        GET    /api/branches/                       - Barcha filiallar
        POST   /api/branches/                       - Yangi filial yaratish
        GET    /api/branches/{id}/                  - Bitta filial
        PUT    /api/branches/{id}/                  - Filialni yangilash
        DELETE /api/branches/{id}/                  - Filialni o'chirish
        GET    /api/branches/{id}/attendance_stats/ - Kunlik davomat statistikasi
        GET    /api/branches/{id}/attendance_summary/ - Davr bo'yicha xulosa
        GET    /api/branches/{id}/department_breakdown/ - Bo'limlar bo'yicha
        GET    /api/branches/{id}/top_latecomers/   - Eng ko'p kechikkanlar
    """

    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Foydalanuvchi dostup qila oladigan filiallarni qaytarish.
        """
        user = self.request.user

        if user.is_admin:
            return Branch.objects.all()

        # UserAccess orqali dostup berilgan filiallar
        return user.get_accessible_branches()

    @action(detail=True, methods=['get'])
    def attendance_stats(self, request, pk=None):
        """
        Filial uchun kunlik davomat statistikasi.

        Query params:
            - date: YYYY-MM-DD (default: bugun)
            - include_children: true/false (default: false)

        Example:
            GET /api/branches/1/attendance_stats/?date=2024-01-15&include_children=true

        Response:
            {
                "date": "2024-01-15",
                "total_employees": 50,
                "present": 45,
                "absent": 3,
                "late": 8,
                "half_day": 1,
                "on_leave": 2,
                "present_percentage": 90.0,
                "late_percentage": 16.0
            }
        """
        branch = self.get_object()

        # Query parameters
        date_param = request.query_params.get('date')
        include_children = request.query_params.get('include_children', 'false').lower() == 'true'

        if date_param:
            stats_date = parse_date(date_param)
            if not stats_date:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            stats_date = date.today()

        # Statistika olish
        stats = branch.get_attendance_stats(
            date=stats_date,
            include_children=include_children
        )

        serializer = BranchAttendanceStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        """
        Filial uchun davr bo'yicha davomat xulosasi.

        Query params:
            - start_date: YYYY-MM-DD (required)
            - end_date: YYYY-MM-DD (required)
            - include_children: true/false (default: false)

        Example:
            GET /api/branches/1/attendance_summary/?start_date=2024-01-01&end_date=2024-01-31

        Response:
            {
                "period": {
                    "start": "2024-01-01",
                    "end": "2024-01-31",
                    "days": 31
                },
                "total_employees": 50,
                "total_records": 1100,
                "total_late_minutes": 2340,
                "total_overtime_minutes": 1200,
                "average_work_hours": 8.5,
                "present_count": 1000,
                "late_count": 150,
                "absent_count": 50,
                "average_present_per_day": 45.45,
                "average_late_per_day": 6.82,
                "average_absent_per_day": 2.27
            }
        """
        branch = self.get_object()

        # Query parameters
        start_date_param = request.query_params.get('start_date')
        end_date_param = request.query_params.get('end_date')
        include_children = request.query_params.get('include_children', 'false').lower() == 'true'

        if not start_date_param or not end_date_param:
            return Response(
                {'error': 'Both start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        start_date = parse_date(start_date_param)
        end_date = parse_date(end_date_param)

        if not start_date or not end_date:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if start_date > end_date:
            return Response(
                {'error': 'start_date must be before end_date'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Xulosa olish
        summary = branch.get_attendance_summary(
            start_date=start_date,
            end_date=end_date,
            include_children=include_children
        )

        serializer = BranchAttendanceSummarySerializer(summary)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def department_breakdown(self, request, pk=None):
        """
        Bo'limlar bo'yicha davomat taqsimoti.

        Query params:
            - date: YYYY-MM-DD (default: bugun)

        Example:
            GET /api/branches/1/department_breakdown/?date=2024-01-15

        Response:
            [
                {
                    "department_id": 1,
                    "department_name": "IT",
                    "department_code": "IT",
                    "total_employees": 15,
                    "present": 14,
                    "late": 3,
                    "absent": 1,
                    "half_day": 0,
                    "on_leave": 0,
                    "present_percentage": 93.33
                },
                ...
            ]
        """
        branch = self.get_object()

        # Query parameters
        date_param = request.query_params.get('date')

        if date_param:
            breakdown_date = parse_date(date_param)
            if not breakdown_date:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            breakdown_date = date.today()

        # Taqsimot olish
        breakdown = branch.get_department_attendance_breakdown(date=breakdown_date)

        serializer = DepartmentAttendanceBreakdownSerializer(breakdown, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def top_latecomers(self, request, pk=None):
        """
        Eng ko'p kechikkan hodimlar ro'yxati.

        Query params:
            - start_date: YYYY-MM-DD (required)
            - end_date: YYYY-MM-DD (required)
            - limit: integer (default: 10)

        Example:
            GET /api/branches/1/top_latecomers/?start_date=2024-01-01&end_date=2024-01-31&limit=5

        Response:
            [
                {
                    "employee_id": 5,
                    "personnel_number": "EMP001",
                    "employee_name": "Ali Valiyev",
                    "department": "IT",
                    "late_count": 12,
                    "total_late_minutes": 180,
                    "average_late_minutes": 15.0
                },
                ...
            ]
        """
        branch = self.get_object()

        # Query parameters
        start_date_param = request.query_params.get('start_date')
        end_date_param = request.query_params.get('end_date')
        limit = int(request.query_params.get('limit', 10))

        if not start_date_param or not end_date_param:
            return Response(
                {'error': 'Both start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        start_date = parse_date(start_date_param)
        end_date = parse_date(end_date_param)

        if not start_date or not end_date:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Eng ko'p kechikkanlarni olish
        latecomers = branch.get_top_latecomers(
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )

        serializer = TopLatecomersSerializer(latecomers, many=True)
        return Response(serializer.data)


class OrganizationSettingsViewSet(viewsets.ModelViewSet):
    """
    Organization Settings API.

    Endpoints:
        GET    /api/organization-settings/     - Barcha sozlamalar
        POST   /api/organization-settings/     - Yangi sozlama yaratish
        GET    /api/organization-settings/{id}/ - Bitta sozlama
        PUT    /api/organization-settings/{id}/ - Sozlamani yangilash
    """

    queryset = OrganizationSettings.objects.all()
    serializer_class = OrganizationSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Foydalanuvchi dostup qila oladigan tashkilot sozlamalarini qaytarish.
        """
        user = self.request.user

        if user.is_admin:
            return OrganizationSettings.objects.all()

        # Faqat dostup berilgan tashkilotlar sozlamalari
        accessible_orgs = user.get_accessible_organizations()
        return OrganizationSettings.objects.filter(organization__in=accessible_orgs)
