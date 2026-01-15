from django.contrib import admin
from .models import Role,BusinessElement,AccessRule, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'is_deleted']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']

@admin.register(BusinessElement)
class BusinessElementAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']

@admin.register(AccessRule)
class AccessRuleAdmin(admin.ModelAdmin):
    list_display = ['role', 'element', 'can_read', 'can_create']
    list_filter = ['role', 'element']
