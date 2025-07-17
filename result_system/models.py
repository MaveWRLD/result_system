from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms import ValidationError


class Faculty(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profiles"
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True, blank=True
    )


class Program(models.Model):
    name = models.CharField(max_length=255, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    enrollment_year = models.IntegerField()

    def __str__(self):
        return f"{self.student_id} - {self.name}"


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="courses"
    )
    credit = models.PositiveBigIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)]
    )
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        related_name="courses",
    )

    def __str__(self):
        return f"{self.code} - {self.name}"


class Enrollment(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="enrolled_student"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrolled_course"
    )
    academic_year = models.IntegerField()  # e.g., 2025
    semester = models.CharField(
        max_length=10, choices=[("Sem1", "Semester 1"), ("Sem2", "Semester 2")]
    )

    class Meta:
        unique_together = [("student", "course", "academic_year", "semester")]

    def __str__(self):
        return f"{self.student} in {self.course}"


class Result(models.Model):
    RESULT_STATUS = [
        ("D", "Draft"),
        ("P_D", "Pending Department"),
        ("P_F", "Pending Faculty"),
        ("A", "Approved"),
        ("R", "Rejected"),
    ]
    course = models.OneToOneField(
        Course, on_delete=models.CASCADE, related_name="results"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=RESULT_STATUS, default="D")

    # def clean(self):
    #    # Ensure lecturer is assigned to the course
    #    if not self.course.lecturer == self.lecturer:
    #        raise ValidationError("Lecturer can only create results for their assigned courses")


#
# def __str__(self):
#    return f"{self.course.code} Results ({self.status})"


class Assessment(models.Model):
    result = models.ForeignKey(
        Result, on_delete=models.CASCADE, related_name="assessments"
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="students_assessment"
    )
    ca_slot1 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    ca_slot2 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    ca_slot3 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    ca_slot4 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    exam_mark = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(60)],
    )
    total_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,  # Prevents manual editing in forms/admin
    )
    grade = models.CharField(max_length=2, null=True, blank=True, editable=False)

    # Grading thresholds (adjust as needed)

    class Meta:
        unique_together = ["result", "student"]

    def clean(self):
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
        # Ensure student is enrolled in the course
        if not Enrollment.objects.filter(
            student=self.student, course=self.result.course
        ).exists():
            raise ValidationError("Student is not enrolled in this course")

    def save(self, *args, **kwargs):
        if self.exam_mark is not None:
            # Convert None to Decimal(0) for CA slots
            ca1 = self.ca_slot1 or Decimal("0")
            ca2 = self.ca_slot2 or Decimal("0")
            ca3 = self.ca_slot3 or Decimal("0")
            ca4 = self.ca_slot4 or Decimal("0")

            self.total_score = ca1 + ca2 + ca3 + ca4 + self.exam_mark

            if self.total_score >= 80:
                self.grade = "A"
            elif self.total_score >= 75:
                self.grade = "B+"
            elif self.total_score >= 70:
                self.grade = "B"
            elif self.total_score >= 65:
                self.grade = "C+"
            elif self.total_score >= 60:
                self.grade = "C"
            elif self.total_score >= 55:
                self.grade = "D+"
            elif self.total_score >= 50:
                self.grade = "D"
            else:
                self.grade = "E"
        else:
            self.total_score = None
            self.grade = "IC"
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.name} - {self.result.course.code}"


class ResultModificationLog(models.Model):
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="modification_logs"
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    old_data = models.JSONField()  # Stores previous CA/exam values
    new_data = models.JSONField()
    reason = models.TextField()
    modified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Modification by {self.modified_by} on {self.modified_at}"


# Create your models here.
