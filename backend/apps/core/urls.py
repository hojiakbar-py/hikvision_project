"""
Core Application URLs.

Bu modul core app uchun API routing ni o'z ichiga oladi.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrganizationViewSet,
    BranchViewSet,
    OrganizationSettingsViewSet
)

# Router yaratish
router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'organization-settings', OrganizationSettingsViewSet, basename='organization-settings')

urlpatterns = [
    path('', include(router.urls)),
]
