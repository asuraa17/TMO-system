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

