from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import random

# Create your models here.

class UserManager(BaseUserManager):

    def _create_user(self, phone, password=None, **extra_fields):
        first_name = extra_fields.get("first_name")
        last_name = extra_fields.get("last_name")
        user_name  = extra_fields.get("user_name")

        if not phone:
            raise ValueError("The phone field must be set.")
        
        if not first_name or not last_name or not user_name:
            raise ValueError("The first name and last name and user name fields must be set.")
        
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_user(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_active") is not True:
            raise ValueError("Superuser must have is_active=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        
        return self._create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    phone = models.CharField(max_length=11, unique=True)
    user_name = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["first_name", "last_name", 'user_name']

    def __str__(self):
        return self.phone
    
class PasswordResetOTPCode(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='password_reset_otp')
    otp_code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def generate_otp(cls,user):
        otp_code = str(random.randint(100000,999999))
        is_used = False
        cls.objects.create(
            user=user,
            otp_code=otp_code,
            is_used=is_used
        )
        return otp_code
    
class PhoneResetOTP(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='phone_reset_otp')
    new_phone = models.CharField(max_length=11)
    otp_code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def generate_otp(cls,user,new_phone):
        otp_code = str(random.randint(100000,999999))
        is_used = False
        cls.objects.create(
            user=user,
            new_phone=new_phone,
            otp_code=otp_code,
            is_used=is_used
        )
        return otp_code