from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, ProviderProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'user_type', 'is_email_verified', 'is_active')
    list_filter = ('user_type', 'is_email_verified', 'is_active', 'is_staff')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'username')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom Fields', {'fields': ('user_type', 'phone_number', 'date_of_birth', 'profile_picture', 'is_email_verified')}),
    )

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'state')
    search_fields = ('user__email', 'user__username')

@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'license_number')
    list_filter = ('specialization',)
    search_fields = ('user__email', 'license_number', 'specialization')
