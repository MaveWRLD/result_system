from django.contrib import admin
from . import models

@admin.register(models.Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(models.Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'faculty']
    search_fields = ['name', 'faculty']
    autocomplete_fields = ['faculty']

@admin.register(models.Profile)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'department']
    list_filter = ['department']
    list_select_related = ['user']
    search_fields = ['department']
    autocomplete_fields = ['user','department']

@admin.register(models.Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'department']
    list_filter = ['department']
    search_fields = ['name']
    autocomplete_fields = ['department']

@admin.register(models.Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'name', 'email', 'program', 'enrollment_year']
    list_select_related = ['program']
    search_fields = ['student_id', 'name']

@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'program', 'credit', 'lecturer']
    list_filter = ['name', 'program', 'lecturer']
    ordering = ['program']
    list_select_related = ['lecturer','program']
    search_fields = ['name__istartwith', 'lecturer_istartwith', 'program_istartwith']
    autocomplete_fields = ['lecturer','program']

class AssessmentScoreInline(admin.TabularInline):
    model = models.Assessment
    fields = ['result', 'student', 'ca_slot1', 'ca_slot2', 'ca_slot3', 'ca_slot4', 'exam_mark']
    list_select_related = ['result', 'student']
    search_fields = ['result__course__istartwith', 'student__name__istartwith']
    autocomplete_fields = ['result', 'student']
    

@admin.register(models.Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'updated_at', 'submitted_at']
    list_filter = ['course']
    list_select_related = ['course']
    search_fields = ['course']
    autocomplete_fields = ['course']
    inlines = [AssessmentScoreInline]


@admin.register(models.ResultModificationLog)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['assessment', 'modified_by', 'old_data', 'new_data', 'reason', 'modified_at']
    list_select_related = ['assessment', 'modified_by']
    #search_fields = ['student_id', 'name']

# Register your models here.
