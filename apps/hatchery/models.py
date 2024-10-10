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
import random
import string
from telelbirds import settings
from apps.breeders.models import Breeders
from apps.customer.models import Customer, Eggs
from apps.inventory.models import Item, ItemRequest
import uuid
from django.core.files import File
from io import BytesIO
import barcode
from barcode.writer import ImageWriter

class Hatchery(models.Model):
    """
    Hatchery Model
    """
    id = models.AutoField(primary_key=True)
    name=models.CharField(null=True,blank=True,max_length=50)
    photo = ProcessedImageField(upload_to='hatchery_photos',null=True,blank=True, processors=[ResizeToFit(1280)], format='JPEG', options={'quality': 70})
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
    totalcapacity=models.IntegerField(null=True,blank=True,max_length=50)    
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        db_table = "hatchery"
        verbose_name = 'Hatchery'
        verbose_name_plural = "Hatcheries"
        managed = True


    def __str__(self):
        return self.name

    def __int__(self):
        return self.id
    
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
        self.clean()
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return '/hatchery/{}'.format(self.name)


class Incubators(models.Model):
    """
    Incubators Model
    """
    id = models.AutoField(primary_key=True)
    hatchery=models.ForeignKey(Hatchery,
        related_name="incubators_hatchery", blank=True, null=True,
        on_delete=models.SET_NULL)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)
    incubatortype=models.CharField(null=True,blank=True,max_length=50)
    manufacturer=models.CharField(null=True,blank=True,max_length=50)
    model=models.CharField(null=True,blank=True,max_length=15)
    number = models.IntegerField(null=True, blank=True)
    year=models.CharField(null=True,blank=True,max_length=50)
    code=models.CharField(null=True,blank=True,max_length=50, unique=True)    
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        db_table = "incubators"
        verbose_name = 'Incubator'
        verbose_name_plural = "Incubators"
        managed = True

    def get_absolute_url(self):
        return '/incubator/{}'.format(self.code)
    
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
        self.clean()
        super(Incubators, self).save(*args, **kwargs)

    def generate_unique_code(self):
        while True:
            random_suffix = ''.join(random.choices(string.digits, k=4))
            unique_code = f'INC-{random_suffix}'
            if not Incubators.objects.filter(code=unique_code).exists():
                return unique_code

class IncubatorCapacity(models.Model):
    """
    IncubatorCapacity Model
    """
    id = models.AutoField(primary_key=True)
    incubator=models.ForeignKey(Incubators,
        related_name="incubatorcapacity_incubator", blank=True, null=True,
        on_delete=models.SET_NULL)
    breed=models.CharField(null=True,blank=True,max_length=50)
    capacity=models.IntegerField(null=True,blank=True,max_length=50)
    occupied=models.IntegerField(null=True,blank=True,max_length=15)
    available=models.IntegerField(null=True,blank=True,max_length=50)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        db_table = "incubator_capacity"
        verbose_name = 'IncubatorCapacity'
        verbose_name_plural = "IncubatorCapacity"
        managed = True  

    def save(self, *args, **kwargs):
        self.available = int(self.capacity) - int(self.occupied)
        super(IncubatorCapacity, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return '/incubator_capacity/{}'.format(self.id)


class EggSetting(models.Model):
    """
    EggSetting Model
    """
    id = models.AutoField(primary_key=True)
    settingcode=models.CharField(null=True,blank=True,max_length=50, unique=True)
    incubator=models.ForeignKey(Incubators,
        related_name="eggsetting_incubator", blank=True, null=True,
        on_delete=models.SET_NULL)
    customer=models.ForeignKey(Customer,
        related_name="eggsetting_customer", blank=True, null=True,
        on_delete=models.SET_NULL)
    breeders=models.ForeignKey(Breeders,
        related_name="eggsetting_breeders", blank=True, null=True,
        on_delete=models.SET_NULL)
    egg = models.ForeignKey(Eggs, on_delete=models.SET_NULL, null=True, blank=True)
    item_request = models.ForeignKey(ItemRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name="egg_setting")
    eggs=models.IntegerField(null=True,blank=True,max_length=50)
    is_approved = models.BooleanField(default=False, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        db_table = "eggsetting"
        verbose_name = 'EggSetting'
        verbose_name_plural = "EggSettings"
        managed = True

    def get_absolute_url(self):
        return '/egg_setting/{}'.format(self.settingcode)
    
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
        if not self.settingcode:
            self.settingcode = self.generate_unique_code()
        self.clean()
        super(EggSetting, self).save(*args, **kwargs)

    def generate_unique_code(self):
        while True:
            random_suffix = ''.join(random.choices(string.digits, k=4))
            unique_code = f'EG-STG-{random_suffix}'
            if not EggSetting.objects.filter(settingcode=unique_code).exists():
                return unique_code


class Incubation(models.Model):
    """
    Incubation Model
    """
    id = models.AutoField(primary_key=True)
    incubationcode=models.CharField(null=True,blank=True,max_length=50, unique=True)
    eggsetting=models.ForeignKey(EggSetting,
        related_name="incubation_eggsetting", blank=True, null=True,
        on_delete=models.SET_NULL)
    customer=models.ForeignKey(Customer,
        related_name="incubation_customer", blank=True, null=True,
        on_delete=models.SET_NULL)
    breeders=models.ForeignKey(Breeders,
        related_name="incubation_breeders", blank=True, null=True,
        on_delete=models.SET_NULL)
    eggs=models.IntegerField(null=True,blank=True,max_length=50)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        db_table = "incubation"
        verbose_name = 'Incubation'
        verbose_name_plural = "Incubations"
        managed = True

    def get_absolute_url(self):
        return '/incubation/{}'.format(self.incubationcode)
    
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
        if not self.incubationcode:
            self.incubationcode = self.generate_unique_incubation_code()
        self.clean()
        super().save(*args, **kwargs)

    def generate_unique_incubation_code(self):
        while True:
            random_suffix = ''.join(random.choices(string.digits, k=4))
            unique_code = f'INC-CODE-{random_suffix}'
            if not Incubation.objects.filter(incubationcode=unique_code).exists():
                return unique_code


class Candling(models.Model):
    """
    Candling Model
    """
    id = models.AutoField(primary_key=True)
    candlingcode=models.CharField(null=True,blank=True,max_length=50, unique=True)
    incubation=models.ForeignKey(Incubation,
        related_name="candling_incubation", blank=True, null=True,
        on_delete=models.SET_NULL)
    customer=models.ForeignKey(Customer,
        related_name="candling_customer", blank=True, null=True,
        on_delete=models.SET_NULL)
    breeders=models.ForeignKey(Breeders,
        related_name="candling_breeders", blank=True, null=True,
        on_delete=models.SET_NULL)
    eggs=models.IntegerField(null=True,blank=True,max_length=50)
    candled=models.BooleanField(null=True,blank=True,max_length=50)
    candled_date=models.DateTimeField(null=True,blank=True)
    spoilt_eggs=models.IntegerField(null=True,blank=True,max_length=50)
    fertile_eggs=models.IntegerField(null=True,blank=True,max_length=50)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        db_table = "Candling"
        verbose_name = 'Candling'
        verbose_name_plural = "Candling"
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
        if not self.candlingcode:
            self.candlingcode = self.generate_unique_candling_code()
        self.fertile_eggs = self.eggs - self.spoilt_eggs
        self.clean()
        super(Candling, self).save(*args, **kwargs)

    def generate_unique_candling_code(self):
        while True:
            random_suffix = ''.join(random.choices(string.digits, k=4))
            unique_code = f'CANDLE-{random_suffix}'
            if not Candling.objects.filter(candlingcode=unique_code).exists():
                return unique_code

    def get_absolute_url(self):
        return '/candling/{}'.format(self.candlingcode)

    def get_absolute_url(self):
        return '/candling/{}'.format(self.candlingcode)


class Hatching(models.Model):
    """
    Hatching Model
    """
    id = models.AutoField(primary_key=True)
    hatchingcode=models.CharField(null=True,blank=True,max_length=50, unique=True)
    candling=models.ForeignKey(Candling,
        related_name="hatching_candling", blank=True, null=True,
        on_delete=models.SET_NULL)
    customer=models.ForeignKey(Customer,
        related_name="hatching_customer", blank=True, null=True,
        on_delete=models.SET_NULL)
    breeders=models.ForeignKey(Breeders,
        related_name="hatching_breeders", blank=True, null=True,
        on_delete=models.SET_NULL)
    hatched=models.IntegerField(null=True,blank=True,max_length=50)
    deformed=models.IntegerField(null=True,blank=True,max_length=50)
    spoilt=models.IntegerField(null=True,blank=True,max_length=50)
    chicks_hatched=models.IntegerField(null=True,blank=True,max_length=50)
    notify_customer=models.BooleanField(null=True,blank=True,max_length=50)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        db_table = "Hatching"
        verbose_name = 'Hatching'
        verbose_name_plural = "Hatching"
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
        # Automatically calculate chicks hatched
        self.chicks_hatched = int(self.hatched) - int(self.deformed) - int(self.spoilt)
        
        # Generate a unique hatching code if it is not already set
        if not self.hatchingcode:
            self.hatchingcode = self.generate_unique_hatching_code()
        self.clean()   
        super(Hatching, self).save(*args, **kwargs)  # Ensure the correct class is used

    def generate_unique_hatching_code(self):
        while True:
            random_suffix = ''.join(random.choices(string.digits, k=4))
            unique_code = f'HTC-{random_suffix}'
            if not Hatching.objects.filter(hatchingcode=unique_code).exists():
                return unique_code

    def get_absolute_url(self):
        return '/hatching/{}'.format(self.hatchingcode)

    def get_absolute_url(self):
        return '/Hatching/{}'.format(self.hatchingcode)


class Holding(models.Model):
    """
    Holding Model
    """
    id = models.AutoField(primary_key=True)
    holdingcode=models.CharField(null=True,blank=True,max_length=50)
    hatching=models.ForeignKey(Hatching,
        related_name="holding_hatching", blank=True, null=True,
        on_delete=models.SET_NULL)
    customer=models.ForeignKey(Customer,
        related_name="holding_customer", blank=True, null=True,
        on_delete=models.SET_NULL)
    breeders=models.ForeignKey(Breeders,
        related_name="holding_breeders", blank=True, null=True,
        on_delete=models.SET_NULL)
    customer_delivery=models.BooleanField(null=True,blank=True,max_length=50)
    mode_delivery=models.CharField(null=True,blank=True,max_length=50)
    location=gismodels.PointField(
        srid=4326, 
        null=True, 
        spatial_index=True, 
        geography=True, 
        blank=True)  # Point
    distance=models.FloatField(null=True,blank=True,max_length=50)
    cost=models.FloatField(null=True,blank=True,max_length=50)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        db_table = "Holding"
        verbose_name = 'Holding'
        verbose_name_plural = "Holding"
        managed = True

    def save(self, *args, **kwargs):
        self.cost = self.distance #* self.location
        super(Holding, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return '/holding/{}'.format(self.holdingcode)

