from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['first_name', 'last_name', 'username']
    add_fieldsets = (
        (None, {
            'classes':('wide'),
            'fields':('username', 'password1', 'password2', 
                      'email', 'first_name', 'last_name'),
        }),
    )
# Register your models here.
