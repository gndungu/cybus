from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    class Meta:
        verbose_name_plural = "User"


    class AccountType(models.TextChoices):
        ADMINISTRATOR = 'ADMINISTRATOR', 'Administrator'
        CUSTOMER = 'CUSTOMER', 'Customer'

    class Role(models.TextChoices):
        MANAGEMENT = 'MANAGEMENT', 'MANAGEMENT'
        REPRESENTATIVE = 'REPRESENTATIVE', 'REPRESENTATIVE'

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255, null=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    use_two_factor_authentication = models.BooleanField(default=True, verbose_name="Two Factor Authentication")
    account_type = models.CharField(max_length=32, choices=AccountType.choices, default=AccountType.CUSTOMER , verbose_name="Account Type")
    signature = models.ImageField(upload_to="signatures/", null=True, blank=True)
    role = models.CharField(max_length=35, choices=Role.choices, null=True, blank=True)
    department_head = models.BooleanField(default=False, verbose_name="Department Head")
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']  # Optional fields during createsuperuser

    def __str__(self):
        return f"{self.full_name} - {self.email}"
