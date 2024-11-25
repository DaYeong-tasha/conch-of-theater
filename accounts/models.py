from django.db import models

# Create your models here.


from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from COT import settings
from django.contrib.auth.models import AbstractUser
from django import forms


class Users(AbstractUser):
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    preferences = models.TextField(null=True, blank=True)
    fullname = models.CharField(max_length=100)
    birth = models.DateField(null=True, blank=True)
    my_keyword = models.TextField(null=True, blank=True)
    my_act = models.TextField(null=True, blank=True)
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ['email', 'fullname']  # 필수 필드 설정

    class Meta:
        db_table = 'users'
    def __str__(self):
        return f"{self.username}'s Profile"


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Users
        exclude = ['address', 'my_genre']  # 주소와 선호도 필드를 제외
