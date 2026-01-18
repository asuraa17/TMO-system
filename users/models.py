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
        ('rejected', 'Rejected'),
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

class ShowroomProfile(models.Model):
    """Profile model for Showroom created via registration"""
    
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="showroom_profile"
    )
    
    # Information
    showroom_name = models.CharField(max_length=255)
    registration_number = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Business registration number"
    )
    pan_number = models.CharField(
        max_length=20,
        help_text="PAN number of the showroom"
    )
    
    # Contact Information
    address = models.TextField()
    phone = models.CharField(max_length=15)
    alternative_phone = models.CharField(max_length=15, blank=True)
    
    # Owner/Manager Information
    owner_name = models.CharField(max_length=255)
    owner_citizenship = models.CharField(max_length=50)
    
    # Documents
    registration_certificate = models.FileField(
        upload_to='showroom_docs/',
        help_text="Business registration certificate"
    )
    pan_certificate = models.FileField(
        upload_to='showroom_docs/',
        help_text="PAN registration certificate"
    )
    owner_citizenship_file = models.FileField(
        upload_to='showroom_docs/',
        help_text="Owner's citizenship document"
    )
    showroom_photo = models.ImageField(
        upload_to='showroom_docs/',
        help_text="Photo of the showroom"
    )
    
    # Verification fields
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending',
        help_text="Verification status by TMO Officer"
    )
    
    verified_by = models.ForeignKey(
        'tmo.TMOOfficer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_showrooms',
        help_text="TMO Officer who verified this showroom"
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
        return f"{self.showroom_name} - {self.registration_number}"
    
    def save(self, *args, **kwargs):
        if self.verification_status in ['verified', 'rejected'] and not self.verified_at:
            from django.utils import timezone
            self.verified_at = timezone.now()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Showroom Profile"
        verbose_name_plural = "Showroom Profiles"
        ordering = ['-created_at']


class Vehicle(models.Model):
    """Model for vehicle information"""
    
    VEHICLE_TYPE_CHOICES = [
        ('car', 'Car'),
        ('motorcycle', 'Motorcycle'),
        ('truck', 'Truck'),
        ('bus', 'Bus'),
        ('van', 'Van'),
    ]
    
    FUEL_TYPE_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
    ]
    
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    # Vehicle Basic Information
    showroom = models.ForeignKey(
        ShowroomProfile,
        on_delete=models.CASCADE,
        related_name='vehicles'
    )
    
    chassis_number = models.CharField(max_length=50, unique=True)
    engine_number = models.CharField(max_length=50)
    
    make = models.CharField(max_length=100, help_text="e.g., Toyota, Honda")
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    color = models.CharField(max_length=50)
    
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES)
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES)
    
    engine_cc = models.IntegerField(help_text="Engine capacity in CC")
    seating_capacity = models.IntegerField()
    
    # Vehicle photos (4 sides)
    photo_front = models.ImageField(upload_to='vehicle_photos/')
    photo_back = models.ImageField(upload_to='vehicle_photos/')
    photo_left = models.ImageField(upload_to='vehicle_photos/')
    photo_right = models.ImageField(upload_to='vehicle_photos/')
    
    # Current Owner
    current_owner = models.ForeignKey(
        BuyerProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name='owned_vehicles'
    )
    
    # Price and payment
    price = models.DecimalField(max_digits=12, decimal_places=2)
    payment_receipt = models.FileField(
        upload_to='payment_receipts/',
        help_text="Cheque or payment receipt"
    )
    
    # Number plate information
    temporary_plate_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Temporary number plate"
    )
    permanent_plate_number = models.CharField(
        max_length=20,
        blank=True,
        unique=True,
        null=True,
        help_text="Permanent number plate (assigned by TMO officer)"
    )
    
    # Verification fields - FIXED: Use verification_status consistently
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending',
        help_text="Verification status by TMO Officer"
    )
    
    verified_by = models.ForeignKey(
        'tmo.TMOOfficer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_vehicles'
    )
    verification_remarks = models.TextField(blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def is_verified(self):
        """Helper property to check if vehicle is verified"""
        return self.verification_status == 'verified'
    
    def __str__(self):
        return f"{self.make} {self.model} ({self.chassis_number})"
    
    def save(self, *args, **kwargs):
        # Auto-set verified_at when status changes to verified or rejected
        if self.verification_status in ['verified', 'rejected'] and not self.verified_at:
            from django.utils import timezone
            self.verified_at = timezone.now()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"
        ordering = ['-created_at']

class VehicleOwnershipHistory(models.Model):
    """Track ownership history of vehicles"""
    
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='ownership_history'
    )
    
    owner = models.ForeignKey(
        BuyerProfile,
        on_delete=models.CASCADE,
        related_name='vehicle_history'
    )
    
    is_current_owner = models.BooleanField(default=True)
    
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    sale_date = models.DateField(null=True, blank=True)
    sale_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.vehicle} - {self.owner.full_name} ({'Current' if self.is_current_owner else 'Past'})"
    
    class Meta:
        verbose_name = "Vehicle Ownership History"
        verbose_name_plural = "Vehicle Ownership Histories"
        ordering = ['-purchase_date']
