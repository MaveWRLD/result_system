from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f'{self.code}:{self.name}'

class User(AbstractUser):
    LECTURER = 'L'
    STUDENT = 'S'
    EXAM_OFFICER = 'EO'

    ROLES = [
        (LECTURER, 'lecturer'),
        (STUDENT, 'student'),
        (EXAM_OFFICER, 'exam officer')
    ]
    role = models.CharField(max_length=20, choices=ROLES)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL,
                                    null=True, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f'{self.username}'

class Course(models.Model):
    SEMESTER_CHOICES = [
        ("FIRST", "First"),
        ("SECOND", "Second")
    ]
    course_name = models.CharField(max_length=100, unique=True)
    course_code = models.CharField(max_length=10, unique=True)
    credit_hours = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)])
    semester_offered = models.CharField(max_length=50, choices=SEMESTER_CHOICES)
    lecturer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  limit_choices_to={'role':'L'})
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

class Result(models.Model):
    STATUS_CHOICES = [
        ("D", "Draft"),
        ("P", "Published")
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE,
                                limit_choices_to={'role':'S'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2,
                                validators = [MinValueValidator(0), MaxValueValidator(100)])
    semester = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="D")
    is_archived = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                  null=True, blank=True, limit_choices_to={'role':'L'}, related_name='created_results')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        permissions = [
            ('can_archive_results', 'Can Archive Results'),
            ('can_edit_results', 'Can Edit Results')
        ]

    #def __str__(self):
    #    return f"{self.student.username}'s grade {self.grade} in {self.course.course_code}"

#class AuditLog(models.Model):
#    ACTION_CHOICES = [
#        ('EDIT', 'Edit'),
#        ('ARCHIVE', 'Archive'),
#        ('REACTIVATE', 'Reactivate')
#    ]
#    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
#    table_name = models.CharField(max_length=20)
#    record = models.IntegerField()
#    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) #...
#    old_value = models.TextField()
#    new_value = models.TextField()
#    action_time = models.DateTimeField(auto_now_add=True)

# Create your models here.
