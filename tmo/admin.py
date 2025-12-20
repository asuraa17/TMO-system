from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from .models import TMOOfficer
import random
import string

# Register your models here.

User = get_user_model()

def generate_officer_id():
    """Generate unique officer id"""
    prefix = "TMO"
    number = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}{number}"

def generate_default_password():
    """Generate a random default password"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

@admin.register(TMOOfficer)
class TMOOfficerAdmin(admin.ModelAdmin):
    list_display = [
        'officer_id', 
        'full_name', 
        'user', 
        'department', 
        'has_changed_password',
        'created_at'
    ]

    list_filter = [
        'department', 
        'has_changed_password',
        'created_at'
    ]

    search_fields = ['officer_id', 'full_name', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'has_changed_password']

    fieldsets = (
        ('User Account', {
            'fields': ('user',),
            'description': 'Select existing user or leave blank to create new TMO officer user'
        }),
        ('Officer Information', {
            'fields': ('officer_id', 'full_name', 'phone', 'department')
        }),
        ('Profile Status', {
            'fields': ('has_changed_password',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    def save_model(self, request, obj, form, change):
        """
        Override save to create User account if it's a new TMOOfficer
        """
        if not change:  # New officer being created

            # Generate officer ID if not provided
            if not obj.officer_id:
                obj.officer_id = generate_officer_id()
                while TMOOfficer.objects.filter(officer_id=obj.officer_id).exists():
                    obj.officer_id = generate_officer_id()
            
            # If no user is selected, create one
            if not obj.user_id:
                default_password = generate_default_password()
                
                # Create username from officer_id
                username = obj.officer_id.lower()
                
                # Create email (you can customize this)
                email = f"{username}@tmo.gov.np"
                
                # Create User
                user = User.objects.create(
                    username=username,
                    email=email,
                    password=make_password(default_password),
                    role=User.Role.Tmo_officer,
                    first_name=obj.full_name.split()[0] if obj.full_name else '',
                )
                
                obj.user = user
                
                # Display the generated credentials
                self.message_user(
                    request,
                    f"TMO Officer created successfully!\n"
                    f"Username: {username}\n"
                    f"Default Password: {default_password}\n"
                    f"Please share these credentials with the officer securely.",
                    level='SUCCESS'
                )
        
        super().save_model(request, obj, form, change)