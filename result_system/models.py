from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.forms import ValidationError
from django.core.exceptions import ValidationError

class Faculty(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Role(models.Model):
    ROLES = [
        ('L', 'Lecturer'),
        ('DRO', 'Department Results Officer'),
        ('FRO', 'Faculty Results Officer'),
        ('CO', 'Corrections Officer'),
    ]
    name = models.CharField(max_length=50, choices=ROLES, unique=True)

    def __str__(self):
        return self.get_name_display()


class UserRole(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'role'],
                name = 'unique_user_role_assignment'
            )
        ]


    def clean(self):
        role_name = self.role.name if self.role else None
        
        # DRO must have department, no faculty
        if role_name == 'DRO':
            if not self.department:
                raise ValidationError({'department': 'Department is required for DRO role'})
            if self.faculty:
                raise ValidationError({'faculty': 'DRO cannot be associated with a faculty'})

        # FRO must have faculty, no department
        elif role_name == 'FRO':
            if not self.faculty:
                raise ValidationError({'faculty': 'Faculty is required for FRO role'})
            if self.department:
                raise ValidationError({'department': 'FRO cannot be associated with a department'})

        # Other roles (Lecturer/Corrections Officer) have no associations
        else:
            if self.department or self.faculty:
                raise ValidationError('Only DRO/FRO roles can have department/faculty associations')

    def save(self, *args, **kwargs):
        self.full_clean()  # Enforce validation on save
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.role.get_name_display()}"
    
class Program(models.Model):
    name = models.CharField(max_length=255, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)


    # Optional: Add program code (e.g., "CS101")

    def __str__(self):
        return self.name
    
    
class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)  # e.g., "STD-2025-001"
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    enrollment_year = models.IntegerField()  # e.g., 2025

    def __str__(self):
        return f"{self.student_id} - {self.name}"

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)  # e.g., "CS101"
    name = models.CharField(max_length=255)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    credit = models.PositiveBigIntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)])
    lecturer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, related_name="courses")

    def __str__(self):
        return f"{self.code} - {self.name}"
    
class Enrollment(models.Model):
    student = models.ForeignKey(Student, 
                                on_delete=models.CASCADE, 
                                related_name='enrolled_student'
                                )
    course = models.ForeignKey(Course, 
                               on_delete=models.CASCADE, 
                               related_name='enrolled_course'
                               )
    academic_year = models.IntegerField()  # e.g., 2025
    semester = models.CharField(max_length=10, choices=[("Sem1", "Semester 1"), ("Sem2", "Semester 2")])

    class Meta:
        unique_together = [('student', 'course', 'academic_year', 'semester')]

    def __str__(self):
        return f"{self.student} in {self.course}"

class Result(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='results'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    #def clean(self):
    #    # Ensure lecturer is assigned to the course
    #    if not self.course.lecturer == self.lecturer:
    #        raise ValidationError("Lecturer can only create results for their assigned courses")
#
    #def __str__(self):
    #    return f"{self.course.code} Results ({self.status})"

class Assessment(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='assessments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='students_assessment')
    ca_slot1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ca_slot2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ca_slot3 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ca_slot4 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    exam_mark = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ['result', 'student']

    #def clean(self):
    #    # Validate CA marks sum <= 40
    #    ca_marks = [self.ca_slot1, self.ca_slot2, self.ca_slot3, self.ca_slot4]
    #    valid_marks = [m for m in ca_marks if m is not None]
    #    
    #    if sum(valid_marks) > 40:
    #        raise ValidationError("Total CA marks cannot exceed 40")
    #        
    #    if self.exam_mark > 60:
    #        raise ValidationError("Exam marks cannot exceed 60")
    #        
    #    # Ensure student is enrolled in the course
    #    if not Enrollment.objects.filter(
    #        student=self.student, 
    #        course=self.result.course
    #    ).exists():
    #        raise ValidationError("Student is not enrolled in this course")
#
    #def save(self, *args, **kwargs):
    #    self.full_clean()
    #    super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.name} - {self.result.course.code}"
    
class SubmittedResult(models.Model):
    RESULT_STATUS = [
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),

    ]
    submitted_at = models.DateField(auto_now_add=True)
    result_status = models.CharField(max_length=50, choices=RESULT_STATUS, default='P')
    lecturer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class SubmittedResultScore(models.Model):
    submitted_result = models.ForeignKey(SubmittedResult, on_delete=models.CASCADE, related_name='result_scores')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='students_score')
    ca_slot1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ca_slot2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ca_slot3 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ca_slot4 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    exam_mark = models.DecimalField(max_digits=5, decimal_places=2)


class ResultModificationLog(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name="modification_logs")
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, limit_choices_to={'role':'CO'})
    old_data = models.JSONField()  # Stores previous CA/exam values
    new_data = models.JSONField()
    reason = models.TextField()
    modified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Modification by {self.modified_by} on {self.modified_at}"

# Create your models here.
