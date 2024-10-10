from __future__ import unicode_literals
import os
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator

from django.db import models
from django.db.models import ImageField
from django.forms import ValidationError
from django.utils.safestring import mark_safe
from django.template.defaultfilters import truncatechars, slugify  # or truncatewords
from django.contrib.gis.db import models as gismodels

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from telelbirds import settings
import random
import string


class Breed(models.Model):
    """
    Breed Model
    """
    id = models.BigAutoField(primary_key=True, unique=True, db_index=True, auto_created=True)
    code=models.CharField(null=True,blank=True,max_length=50, unique=True)
    poultry_type=models.CharField(null=True,blank=True,max_length=50)
    breed=models.CharField(null=True,blank=True,max_length=50)
    purpose=models.CharField(null=True,blank=True,max_length=50)
    eggs_year=models.IntegerField(null=True,blank=True,max_length=50)
    adult_weight=models.FloatField(null=True,blank=True,max_length=50)
    description=models.TextField(null=True,blank=True,max_length=250)
    front_photo = ProcessedImageField(upload_to='media/breed_photos',null=True,blank=True, processors=[ResizeToFit(1280)], format='JPEG', options={'quality': 70})
    side_photo = ProcessedImageField(upload_to='media/breed_photos',null=True,blank=True, processors=[ResizeToFit(1280)], format='JPEG', options={'quality': 70})
    back_photo = ProcessedImageField(upload_to='media/breed_photos',null=True,blank=True, processors=[ResizeToFit(1280)], format='JPEG', options={'quality': 70})
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        db_table = "breed"
        verbose_name = 'Breed'
        verbose_name_plural = "Breed"
        managed = True
    
    def clean(self):
        errors = {}
        for field in self._meta.get_fields():
            if isinstance(field, models.CharField) and field.max_length is not None:
                value = getattr(self, field.name)
                if value and len(value) > field.max_length:
                    name = field.attname.replace('_', ' ')
                    errors[field.name] = f"Field {name.capitalize()} has exceeded it's maximum length ({field.max_length})"
        if errors:
            raise ValidationError(errors)   
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        self.eggs_year = int(self.eggs_year) if self.eggs_year else None
        self.clean()
        super(Breed, self).save(*args, **kwargs)
        
    def generate_unique_code(self):
        while True:
            random_suffix = ''.join(random.choices(string.digits, k=4))
            unique_code = f'BRD-{random_suffix}'
            if not Breed.objects.filter(code=unique_code).exists():
                return unique_code

    def get_absolute_url(self):
        return '/breed/{}'.format(self.code)
    


class Breeders(models.Model):
    """
    Breeders Model
    """
    id = models.AutoField(primary_key=True)
    batch=models.CharField(null=True,blank=True,max_length=50, unique=True)
    breed=models.ForeignKey(Breed,
        related_name="breeders_breed", blank=True, null=True,
        on_delete=models.SET_NULL)
    hens=models.IntegerField(null=True,blank=True,max_length=50)
    cocks=models.IntegerField(null=True,blank=True,max_length=50)
    mortality=models.FloatField(null=True,blank=True,max_length=50)
    butchered = models.IntegerField(null=True,blank=True,max_length=50)
    sold = models.IntegerField(null=True,blank=True,max_length=50)
    current_number = models.IntegerField(null=True,blank=True,max_length=50)
    hens_photo = ProcessedImageField(upload_to='breeders_photos',null=True,blank=True, processors=[ResizeToFit(1280)], format='JPEG', options={'quality': 70})
    cocks_photo = ProcessedImageField(upload_to='breeders_photos',null=True,blank=True, processors=[ResizeToFit(1280)], format='JPEG', options={'quality': 70})
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        db_table = "breeders"
        verbose_name = 'Breeders'
        verbose_name_plural = "Breeders"
        managed = True
        
    def generate_unique_batch(self):
        while True:
            random_suffix = ''.join(random.choices(string.digits, k=4))
            unique_code = f'BRDR-{random_suffix}'
            if not Breeders.objects.filter(batch=unique_code).exists():
                return unique_code
            
    def clean(self):
        errors = {}
        for field in self._meta.get_fields():
            if isinstance(field, models.CharField) and field.max_length is not None:
                value = getattr(self, field.name)
                if value and len(value) > field.max_length:
                    name = field.attname.replace('_', ' ')
                    errors[field.name] = f"Field {name.capitalize()} has exceeded it's maximum length ({field.max_length})"
        if errors:
            raise ValidationError(errors)            
                
    def save(self, *args, **kwargs):
        if not self.batch:
            self.batch = self.generate_unique_batch()
        try:
            self.cocks = int(self.cocks) if self.cocks is not None else 0
            self.hens = int(self.hens) if self.hens is not None else 0
            self.butchered = int(self.butchered) if self.butchered is not None else 0
            self.sold = int(self.sold) if self.sold is not None else 0
            self.mortality = float(self.mortality) if self.mortality is not None else 0.0
            
            # Calculate current number
            self.current_number = self.cocks + self.hens - self.butchered - self.sold
            
            # Ensure current_number is valid
            if self.current_number < 0:
                raise ValidationError("Current number cannot be negative.")
            
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid input for numbers: {e}")
        self.clean()
        super(Breeders, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return '/breeders/{}'.format(self.batch)