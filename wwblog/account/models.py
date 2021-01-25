from django.db import models
from django.utils.timezone import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, email, username, password, **kwargs):
        if not email:
            raise ValueError("You must provide an email address")
        if not password:
            raise ValueError("You must provide a password")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **kwargs
        )
        user.set_password(password)
        user.save()
        # user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('is_superuser', True)
        # kwargs.setdefault('is_admin', True)

        if kwargs.get('is_staff') is not True:
            raise ValueError("superuser must be staff")
        if kwargs.get('is_superuser') is not True:
            raise ValueError("superuser must be have is_superuser == True")
        if kwargs.get('is_active') is not True:
            raise ValueError("superuser must be active")

        return self.create_user(email, username, password, **kwargs)


# class User(AbstractBaseUser, PermissionsMixin):
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    # password =
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    # last_login = models.DateTimeField(verbose_name='last login', auto_now=True) # is included by default
    # is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)  # if false the user cannot log in to admin
    # is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = [
        # 'username',
        'email',
        # 'password'
    ]

    # register custom object manager
    object = UserManager()

    def __str__(self):
        return f"{self.username} {self.email}"
