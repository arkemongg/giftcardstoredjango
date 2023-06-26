from django.shortcuts import render
from django.contrib.auth import login
from django.http import HttpResponse
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin
from djoser import views
from rest_framework import status
from .serializers import CurrentPasswordSerializer, UserCreateSerializer
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

class PasswordValidationViewSet(views.UserViewSet):
    serializer_class = CurrentPasswordSerializer
    def validate_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Password is valid'}, status=status.HTTP_200_OK)