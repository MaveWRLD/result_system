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


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_name', 'course_code', 'credit_hours', 'semester_offered','lecturer', 'department']
    list_filter = ['course_name', 'department', 'lecturer']
    ordering = ['department']
    search_fields = ['course_name__istartwith', 'lecturer_istartwith']
    autocomplete_fields = ['lecturer', 'department']

@admin.register(models.Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'score', 'status', 'is_archived', 'author', 'created_at', 'updated_at']
    list_filter = ['course', 'author', 'created_at']
    list_select_related = ['student', 'course', 'created_by']
    ordering = ['course']
    search_fields = ['course__istartwith']
    autocomplete_fields = ['student', 'course', 'author']


# Register your models here.
