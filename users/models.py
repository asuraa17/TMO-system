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
    Verification_Status_Choices = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejectde', 'Rejected'),
    ]
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
    
    # Verification fields
    verification_status = models.CharField(
        max_length=20,
        choices=Verification_Status_Choices,
        default='pending',
        help_text="Verification status by TMO Officer"
    )
    
    verified_by = models.ForeignKey(
        'tmo.TMOOfficer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_buyers',
        help_text="TMO Officer who verified this buyer"
    )
    
    verification_remarks = models.TextField(
        blank=True,
        help_text="Remarks by TMO Officer during verification"
    )
    
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when verification was completed"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"BuyerProfile: {self.full_name}"
    
    def save(self, *args, **kwargs):
        # Auto-set verified_at when status changes to verified or rejected
        if self.verification_status in ['verified', 'rejected'] and not self.verified_at:
            from django.utils import timezone
            self.verified_at = timezone.now()
        super().save(*args, **kwargs)

    def reset_verification_if_rejected(self):
        """
        Reset verification status to pending if currently rejected
        This should be called when buyer updates their profile
        """
        if self.verification_status == 'rejected':
            self.verification_status = 'pending'
            self.verified_by = None
            self.verification_remarks = ''
            self.verified_at = None
    
    class Meta:
        verbose_name = "Buyer Profile"
        verbose_name_plural = "Buyer Profiles"
