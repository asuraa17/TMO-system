from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class TMOOfficer(models.Model):
    """
    Profile model for TMO Officer created by admin
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="tmo_officer_profile",
        null=True,
        blank=True
    )

    officer_id = models.CharField(
        max_length=20, 
        unique=True, 
        null=True,
        blank=True,
        help_text="Unique officer identification number"
    )

    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)

    department = models.CharField(
        max_length=100, 
        default="Vehicle Registration",
        help_text="Department within TMO"
    )

    has_changed_password = models.BooleanField(
        default=False,
        help_text="Whether officer has changed default password"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.officer_id} - {self.full_name}"
    
    class Meta:
        verbose_name = "TMO Officer"
        verbose_name_plural = "TMO Officers"
        ordering = ['-created_at']
