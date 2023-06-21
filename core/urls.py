from django.urls import path

from core.views import PasswordValidationViewSet


urlpatterns = [
    path('password/validate/', PasswordValidationViewSet.as_view({'post': 'validate_password'}), name='validate-password'),
]