from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['first_name', 'last_name', 'is_lecturer', 'is_dro', 'is_fro', 'is_co','username']
    fieldsets = BaseUserAdmin.fieldsets + (
        (("UserRoles info"), {"fields": ('is_lecturer', 'is_dro', 'is_fro', 'is_co')}),        
    )
    add_fieldsets = (
        (None, {
            'classes':('wide'),
            'fields':('username', 'password1', 'password2', 
                      'email', 'first_name', 'last_name' ,
                       'is_lecturer', 'is_dro', 'is_fro', 'is_co'),
        }),
    )
# Register your models here.
