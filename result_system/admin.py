from django.contrib import admin
from . import models

@admin.register(models.Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name']

class ResultInine(admin.TabularInline):
    model = models.Result
    fk_name = 'student'
    autocomplete_fields = ['course', 'created_by']

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['role', 'department', 'email']
    list_per_page = 10
    list_filter = ['department', 'role']
    inlines = [ResultInine]
    ordering = ['role']
    autocomplete_fields = ['department']
    search_fields = ['role', 'username']

@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_name', 'course_code', 'lecturer', 'department']
    list_filter = ['course_name', 'department', 'lecturer']
    ordering = ['department']
    search_fields = ['course_name__istartwith', 'lecturer_istartwith']
    autocomplete_fields = ['lecturer', 'department']

@admin.register(models.Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'grade', 'semester', 'is_archived', 'created_by', 'created_at', 'updated_at']
    list_filter = ['course', 'created_by', 'created_at']
    list_select_related = ['student', 'course', 'created_by']
    ordering = ['course']
    search_fields = ['course__istartwith']
    autocomplete_fields = ['student', 'course', 'created_by']

#@admin.register(models.AuditLog)
#class AuditLogAdmin(admin.ModelAdmin):
#    list_display = ['action', 'table_name', 'record', 'user', 'old_value', 'new_value', 'action_time']
#    list_filter = ['action']
#    list_select_related = ['user']
#    ordering = ['action']
#    search_fields = ['record__istartwith']
#    autocomplete_fields = ['user']

# Register your models here.
