from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):


    GENDER = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    
    gender = models.CharField(max_length=30, blank=True, null=True, default="F", choices=GENDER)
    email = models.EmailField(max_length=150, unique=True)
    user_credits = models.PositiveIntegerField(default=0)

    #USERNAME_FIELD = 'email'
    #REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return f"{self.username} {self.user_credits}"
