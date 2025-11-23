from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User

# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = ['username', 'email', 'role', 'is_staff', 'is_active', 'date_joined']

    list_filter = ['role', 'is_staff', 'is_active', 'date_joined']

    search_fields = ['username', 'email', 'first_name', 'last_name']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

    def save_related(self, request, form, formsets, change):
        """
        Save the user and sync groups with role.
        """
        super().save_related(request, form, formsets, change)
        
        ROLE_GROUPS = {
            User.Role.Showroom: 'showroom_user',
            User.Role.Buyer: 'buyer',
            User.Role.Tmo_officer: 'tmo_officer',
            User.Role.Inspector: 'inspector',
            User.Role.System_admin: 'system_admin',
        }

        user = form.instance
        group_name = ROLE_GROUPS.get(user.role)
        
        if group_name:
            user.groups.clear()
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
