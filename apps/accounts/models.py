from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from timezone_field import TimeZoneField

from apps.core.models import TimeStampedModel
# from glucoses.models import Category, Unit

class TimeStampedModel(models.Model):
    """
    Abstract base class that provides self-updating 'created' and 'modified'
    fields.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UserSettings(TimeStampedModel):
    """
    Model to store additional user settings and preferences. Extends User model.
    """
    user = models.OneToOneField(User, related_name='settings', on_delete=models.CASCADE)
    primary_phone = models.CharField(max_length=25)
    secondary_phone = models.CharField(max_length=25, null=True)
    date_of_birth = models.DateField(null=True)
    address = models.CharField(max_length=100, null=True)


    def username(self):
        return self.user.username
    username.admin_order_field = 'user__username'

    class Meta:
        verbose_name_plural = 'User Settings'
        
class UserWalletAddress(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True, db_index=True)
    user = models.OneToOneField(User, related_name='wallet_address', on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    provider = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.user} - {self.address[:10]}...'
    
    class Meta:
        verbose_name_plural = 'User Wallet Addresses'