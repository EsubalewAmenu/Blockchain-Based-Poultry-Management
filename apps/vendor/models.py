# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2020:  TelelBirds
#
#
#########################################################################
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
from apps.breeders.models import Breeders, Breed
from apps.inventory.models import Item
import uuid
import random
import string


class Vendor(models.Model):
    """
    Vendor Model
    """
    id = models.AutoField(primary_key=True)
    first_name=models.CharField(null=True,blank=True,max_length=50)
    last_name=models.CharField(null=True,blank=True,max_length=50)
    full_name=models.CharField(null=True,blank=True,max_length=50)
    photo = ProcessedImageField(upload_to='vendor_photos',null=True,blank=True, processors=[ResizeToFit(1280)], format='JPEG', options={'quality': 70})
    email=models.EmailField(null=True,blank=True,max_length=50, unique=True)
    phone=models.CharField(null=True,blank=True,max_length=15)
    address=models.CharField(null=True,blank=True,max_length=50)
    location=gismodels.PointField(
        srid=4326, 
        null=True, 
        spatial_index=True, 
        geography=True, 
        blank=True)  # Point
    latitude = models.FloatField(null=True,blank=True)
    longitude = models.FloatField(null=True,blank=True)
    vendortype=models.CharField(null=True,blank=True,max_length=50)
    notification_sms=models.BooleanField(null=True,blank=True,max_length=50)
    notification_sms=models.BooleanField(null=True,blank=True,max_length=50)
    delivery=models.BooleanField(null=True,blank=True,max_length=50)    
    followup=models.BooleanField(null=True,blank=True,max_length=50)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        db_table = "vendors"
        verbose_name = 'vendor'
        verbose_name_plural = "vendors"
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
        self.full_name = self.first_name + " " + self.last_name
        existing_vendor = Vendor.objects.filter(full_name=self.full_name).exclude(id=self.id).first()

        if existing_vendor and existing_vendor.owner != self.owner:
            self.full_name = f"{self.first_name}_{self.last_name}_{random.randint(0, 1000)}"
            
        self.clean()
        super(Vendor, self).save(*args, **kwargs)

    def __str__(self):
        return self.last_name + ", " + self.first_name
    
    def get_absolute_url(self):
        return '/vendor/{}'.format(self.full_name)


class Feeds(models.Model):
    """
    feeds Model
    """
    id = models.AutoField(primary_key=True)
    batchnumber = models.CharField(null=True,blank=True,max_length=50, unique=True)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)
    vendor=models.ForeignKey(Vendor,
        related_name="feeds_vendor", blank=True, null=True,
        on_delete=models.SET_NULL)
    feedtype = models.CharField(max_length=50, null=True, blank=True, choices=[['Starter', 'Starter'], ['Grower', 'Grower'], ['Finisher', 'Finisher'], ['Layer', 'Layer'], ['Breeder', 'Breeder'], ['Medicated', 'Medicated'], ['Organic_Natural', 'Organic_Natural'], ['Scratch', 'Scratch']], default='Layer')
    photo = ProcessedImageField(upload_to='feeds_photos',null=True,blank=True, processors=[ResizeToFit(1280)], format='JPEG', options={'quality': 70})
    brought = models.IntegerField(null=True,blank=True)
    returned = models.IntegerField(null=True,blank=True)
    received=models.IntegerField(null=True,blank=True,max_length=50) 
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        db_table = "feeds"
        verbose_name = 'feed'
        verbose_name_plural = "feeds"
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
        if not self.batchnumber:
            self.batchnumber = self.generate_unique_batchnumber()
        if not self.received:
            self.received = int(self.brought) - int(self.returned)
        self.item.quantity=self.received
        self.item.save()
        self.clean()
        super(Feeds, self).save(*args, **kwargs)
        
    def generate_unique_batchnumber(self):
        while True:
            random_suffix = ''.join(random.choices(string.digits, k=5))
            unique_code = f'FD-{random_suffix}'
            if not Feeds.objects.filter(batchnumber=unique_code).exists():
                return unique_code

    def __str__(self):
        return self.batchnumber
    
    def get_absolute_url(self):
        return '/vendor_feeds/{}'.format(self.batchnumber)


class Medicine(models.Model):
    MEDICINE_CATEGORIES = [
        ('Antibiotic', 'Antibiotic'),
        ('Vaccine', 'Vaccine'),
        ('Vitamin & Mineral', 'Vitamin & Mineral'),
        ('Dewormer', 'Dewormer'),
        ('Coccidiostat', 'Coccidiostat'),
        ('Antifungal', 'Antifungal'),
        ('Antiprotozoal', 'Antiprotozoal'),
        ('Pain Reliever', 'Pain Reliever'),
        ('Other', 'Other'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=50, choices=MEDICINE_CATEGORIES)

    def __str__(self):
        return f"{self.name} - {self.category}"


class MedicineInventory(models.Model):
    """
    Medicines Model
    """
    id = models.AutoField(primary_key=True)
    batchnumber = models.CharField(null=True,blank=True,max_length=50, unique=True)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)
    vendor=models.ForeignKey(Vendor,
        related_name="medicines_vendor", blank=True, null=True,
        on_delete=models.SET_NULL)


    UNITS = [
        ('ml', 'Milliliters'),
        ('mg', 'Milligrams'),
        ('tablet', 'Tablet'),
        ('g', 'Grams'),
        ('dose', 'Dose'),
    ]

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    stock_quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=20, choices=UNITS)
    expiry_date = models.DateField()
    purchase_date = models.DateField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


    photo = ProcessedImageField(upload_to='medicines_photos',null=True,blank=True, processors=[ResizeToFit(1280)], format='JPEG', options={'quality': 70}) 
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        db_table = "medicines"
        verbose_name = 'medicine'
        verbose_name_plural = "medicines"
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
        if not self.batchnumber:
            self.batchnumber = self.generate_unique_batchnumber()
        self.item.save()
        self.clean()
        super(MedicineInventory, self).save(*args, **kwargs)
        
    def generate_unique_batchnumber(self):
        while True:
            random_suffix = ''.join(random.choices(string.digits, k=5))
            unique_code = f'MI-{random_suffix}'
            if not MedicineInventory.objects.filter(batchnumber=unique_code).exists():
                return unique_code

    def __str__(self):
        return self.batchnumber
    
    def get_absolute_url(self):
        return '/medicine_inventory/{}'.format(self.batchnumber)

    def is_expired(self):
        return self.expiry_date < timezone.now().date()


# class vendorRequest(models.Model):
#     """
#     vendorRequest Model
#     """
#     id = models.AutoField(primary_key=True)
#     requestcode=models.CharField(null=True,blank=True,max_length=50)
#     feeds=models.ForeignKey(feeds,
#         related_name="vendorrequest_feeds", blank=True, null=True,
#         on_delete=models.SET_NULL) 
#     created = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['created']
#         db_table = "vendorRequests"
#         verbose_name = 'vendorRequest'
#         verbose_name_plural = "vendorRequests"
#         managed = True
    
#     def save(self, *args, **kwargs):
#         prefix = "REQ-"
#         unique_id = str(uuid.uuid4().hex[:8])
#         self.requestcode = f"{prefix}{unique_id}"
#         super(vendorRequest, self).save(*args, **kwargs)
        
#     def get_absolute_url(self):
#         return '/vendor_request/{}'.format(self.requestcode)