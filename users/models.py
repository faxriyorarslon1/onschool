from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail
from .managers import CustomUserManager


GENDER_CHOICES = (
    ('Erkak', 'Erkak'),
    ('Ayol', 'Ayol')
)



class User(AbstractUser):
    
    username = models.CharField('First name',
                                max_length=20, unique=False)
    last_name = models.CharField(max_length=20)
    middlename = models.CharField(max_length=20)
    email = models.EmailField(_('email address'), unique=True)
    dob = models.DateField('Date of Birth')
    phone = models.CharField(max_length=12, unique=True)
    gender = models.CharField(max_length=8, choices=GENDER_CHOICES)
    course = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username', 'last_name', 'middlename', 'dob',
                       'email', 'gender', 'course', 'password']

    def __str__(self):
        return "{} {}".format(self.username, self.last_name)

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'