from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin

class UserAdminConfig(UserAdmin):
    ordering = ('-date_joined', 'id')
    list_display = ('email',
                    'username',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'date_joined'
                    )

    fieldsets = (
        (None, {'fields': ('username', 'email')}),
        ('details', {'fields': ('last_login', 'date_joined', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups',)}),
    )
    # 'user_permissions'

    readonly_fields = (
        'date_joined', 'last_login',
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password1')
        }),
    )


admin.site.register(User, UserAdminConfig)
