# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = (
        'phone',
        'username',
        'email',
        'is_active',
        'is_staff',
        'is_superuser',
        'created_at',
    )

    list_filter = ('is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal Info', {'fields': ('username', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone', 
                'username', 
                'email', 
                'password1', 
                'password2', 
                'is_active', 
                'is_staff'
                ),
        }),
    )

    readonly_fields = ('created_at', 'last_login')

    search_fields = ('phone', 'username', 'email')
    ordering = ('-created_at',)
