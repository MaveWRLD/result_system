from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f'{self.code}:{self.name}'

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, 
                                on_delete=models.CASCADE, related_name='students')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='students')
    phone = models.CharField(max_length=10)


class Course(models.Model):
    SEMESTER_CHOICES = [
        ("F", "First"),
        ("S", "Second")
    ]
    course_name = models.CharField(max_length=100, unique=True)
    course_code = models.CharField(max_length=10, unique=True)
    credit_hours = models.PositiveIntegerField(validators=[MinValueValidator(1),
                                                MaxValueValidator(3)])
    semester_offered = models.CharField(max_length=50, choices=SEMESTER_CHOICES)
    lecturer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, blank=True, limit_choices_to={'role':'L'},
                                related_name='course')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

class Result(models.Model):
    STATUS_CHOICES = [
        ("I", "In active"),
        ("IC", "In-Complete"),
        ("WL", "With Lecturer"),
        ("D", "Department"),
        ("F", "Faculty")
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                limit_choices_to={'role':'S'}, related_name='student_results')
    score = models.DecimalField(max_digits=5, decimal_places=2,
                                validators = [MinValueValidator(0), MaxValueValidator(100)])
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, blank=True, limit_choices_to={'role':'L'},
                                related_name='authored_results')
    is_archived = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="I")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


    #def __str__(self):
    #    return f"{self.student.username}'s grade {self.grade} in {self.course.course_code}"


# Create your models here.
