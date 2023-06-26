from django.urls import path
from rest_framework_nested.routers import DefaultRouter

from core.views import PasswordValidationViewSet
urlpatterns = [
    path('password/validate/', PasswordValidationViewSet.as_view({'post': 'validate_password'}), name='validate-password'),
]