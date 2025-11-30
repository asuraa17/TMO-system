from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    class Role(models.TextChoices):
        #choice name = database value, display value
        Showroom = 'showroom', 'Showroom user'
        Buyer = 'buyer', 'Buyer'
        Tmo_officer = 'tmo_officer', 'TMO Officer'
        Inspector = 'inspector', 'Inspector'
        System_admin = 'system_admin', 'System Admin'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.Showroom,
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class BuyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="buyer_profile")
    full_name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    dob = models.DateField(null=True, blank=True, verbose_name="Date of Birth")

    citizenship_file = models.FileField(
        upload_to='buyer_docs/',
        null=True,
        blank=True,
        help_text="Upload citizenship document file"
        )
    
    nid_file = models.FileField(
        upload_to='buyer_docs/',
        null=True,
        blank=True,
        help_text="Upload NID document file"
        )
    
    passport_photo = models.FileField(
        upload_to='buyer_docs/',
        null=True,
        blank=True,
        help_text="Upload passport size photo (required)"
        )
    
    signature_image = models.FileField(
        upload_to='buyer_docs/',
        null=True,
        blank=True,
        help_text="Upload signature (required)"
        )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"BuyerProfile: {self.full_name}"
    
    class Meta:
        verbose_name = "Buyer Profile"
        verbose_name_plural = "Buyer Profiles"
