from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_lecturer = models.BooleanField(default=False)
    is_dro = models.BooleanField(default=False)
    is_fro = models.BooleanField(default=False)
    is_co = models.BooleanField(default=False)


    

# Create your models here.
