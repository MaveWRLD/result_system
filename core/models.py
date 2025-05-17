from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    email = models.EmailField(unique=True)
    ROLES = [
        ('L', 'lecturer'),
        ('S', 'student'),
        ('EO', 'exam officer')
    ]
    role = models.CharField(max_length=20, choices=ROLES, null=True, blank=True)
