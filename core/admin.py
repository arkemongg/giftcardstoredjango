import django.conf
from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['id',"username",'email','first_name','last_name','is_staff','is_active']
    list_editable = ['is_active']
