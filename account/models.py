from django.db import models
# from django.utils.timezone import timezone
# from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group


from django.core import exceptions
from . import role_validation


class UserManager(BaseUserManager):
    def create_user(self, email, username, password, **kwargs):
        # not required because they are tested within the inherited class
        if not email:
            raise ValueError("You must provide an email address")
        if not password:
            raise ValueError("You must provide a password")
        if not username:
            raise ValueError("You must provide a username")
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **kwargs
        )
        user.set_password(password)
        user.save()
        # user.save(using=self._db)
        print(f"crated new user {username}")
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

    @staticmethod
    def get_max_role_name(user) -> str:
        if user.is_superuser:
            return role_validation.role_hierarchy[0]
        return role_validation.get_max_role_name(role_validation.get_user_groups(user))

    @staticmethod
    def activate_user(user) -> bool:
        try:
            user.is_active = True
            user.save()
            return True
        except Exception as e:
            print(f"cannot activate user {user.username} because:{e}")
            return False

    @staticmethod
    def get_role_users(role_name: str) -> list:
        """returns a list users that belong to a role"""
        if role_name not in role_validation.role_hierarchy:
            raise ValueError(f"This role \"{role_name}\" does not exist in the current roles")
        try:
            # g = Group.objects.get(name=role_name)
            users = User.objects.filter(groups__name=role_name)
        except exceptions.EmptyResultSet:
            users = []
        return users

    @staticmethod
    def get_users_up_to_role(role_name: str) -> list:
        """gets users from lowest privilege (highest role index) up to the specified role (non inclusive)"""
        if role_name not in role_validation.role_hierarchy:
            raise ValueError(f"This role \"{role_name}\" does not exist in the current roles")

        users = []
        # get list or roles bellow
        roles = role_validation.role_hierarchy
        index = roles.index(role_name)
        end = len(roles)
        for i in range(index+1, end-1):
            users += UserManager.get_role_users(roles[i])
        return users


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
        'email',
    ]

    class Meta:
        indexes = [
            models.Index(fields=['username', 'email']),
        ]

    # register custom object manager
    objects = UserManager()

    def __str__(self):
        return f"{self.username} {self.email}"

    @property
    def is_moderator_or_admin(self):
        return role_validation.is_moderator_or_admin(self)
