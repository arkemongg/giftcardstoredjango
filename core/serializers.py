
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer,UserSerializer as BaseUserSerializer , TokenCreateSerializer as BaseTokenCreateSerializer ,CurrentPasswordSerializer as BaseCurrentPasswordSerializer,UserDeleteSerializer as BaseUserDeleteSerializer
from django.contrib.auth import authenticate, login
from .models import User
from rest_framework import status
from django.urls import reverse



class UserCreateSerializer(BaseUserCreateSerializer):
    password_confirmation = serializers.CharField(write_only=True,style={'input_type': 'password'})
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirmation']:
            raise serializers.ValidationError("Password and password confirmation do not match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirmation', None)
        return super().create(validated_data)
    
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['email','username','password','password_confirmation','first_name','last_name']

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['email','username','first_name','last_name']

    def validate_email(self,value):
        data_dict = self.__dict__
        email = data_dict['_kwargs']['data']['email']
        return email
    
    def update(self, instance, validated_data):
        validated_data.pop('email', None)
        return super().update(instance, validated_data)
    


class TokenCreateSerializer(BaseTokenCreateSerializer):
    pass
class CurrentPasswordSerializer(BaseCurrentPasswordSerializer):
    pass




