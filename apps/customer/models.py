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


class Customer(models.Model):
    """
    Customer Model
    """
    id = models.AutoField(primary_key=True)
    first_name=models.CharField(null=True,blank=True,max_length=50)
    last_name=models.CharField(null=True,blank=True,max_length=50)
    full_name=models.CharField(null=True,blank=True,max_length=50)
    photo = ProcessedImageField(upload_to='customer_photos',null=True,blank=True, processors=[ResizeToFit(1280)], format='JPEG', options={'quality': 70})
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
    customertype=models.CharField(null=True,blank=True,max_length=50)
    notification_sms=models.BooleanField(null=True,blank=True,max_length=50)
    notification_sms=models.BooleanField(null=True,blank=True,max_length=50)
    delivery=models.BooleanField(null=True,blank=True,max_length=50)    
    followup=models.BooleanField(null=True,blank=True,max_length=50)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        db_table = "customers"
        verbose_name = 'Customer'
        verbose_name_plural = "Customers"
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
        existing_customer = Customer.objects.filter(full_name=self.full_name).exclude(id=self.id).first()

        if existing_customer and existing_customer.owner != self.owner:
            self.full_name = f"{self.first_name}_{self.last_name}_{random.randint(0, 1000)}"
            
        self.clean()
        super(Customer, self).save(*args, **kwargs)

    def __str__(self):
        return self.last_name + ", " + self.first_name
    
    def get_absolute_url(self):
        return '/customer/{}'.format(self.full_name)


class Eggs(models.Model):
    """
    Eggs Model
    """
    id = models.AutoField(primary_key=True)
    batchnumber = models.CharField(null=True,blank=True,max_length=50, unique=True)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True, choices=[['customer', 'customer'], ['farm', 'farm']], default='customer')
    customer=models.ForeignKey(Customer,
        related_name="eggs_customer", blank=True, null=True,
        on_delete=models.SET_NULL)
    chicks = models.CharField(blank=True, null=True, max_length=50)
    breed=models.ForeignKey(Breed,
        related_name="eggs_breed", blank=True, null=True,
        on_delete=models.SET_NULL)
    customercode = models.CharField(null=True,blank=True,max_length=50)
    photo = ProcessedImageField(upload_to='eggs_photos',null=True,blank=True, processors=[ResizeToFit(1280)], format='JPEG', options={'quality': 70})
    brought = models.IntegerField(null=True,blank=True)
    returned = models.IntegerField(null=True,blank=True)
    received=models.IntegerField(null=True,blank=True,max_length=50) 
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        db_table = "eggs"
        verbose_name = 'Egg'
        verbose_name_plural = "Eggs"
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
        self.received = int(self.brought) - int(self.returned)
        self.item.quantity=self.received
        self.item.save()
        self.clean()
        super(Eggs, self).save(*args, **kwargs)
        
    def generate_unique_batchnumber(self):
        while True:
            random_suffix = ''.join(random.choices(string.digits, k=4))
            unique_code = f'EG-{random_suffix}'
            if not Eggs.objects.filter(batchnumber=unique_code).exists():
                return unique_code

    def __str__(self):
        return self.batchnumber
    
    def get_absolute_url(self):
        return '/customer_eggs/{}'.format(self.batchnumber)


class CustomerRequest(models.Model):
    """
    CustomerRequest Model
    """
    id = models.AutoField(primary_key=True)
    requestcode=models.CharField(null=True,blank=True,max_length=50)
    eggs=models.ForeignKey(Eggs,
        related_name="customerrequest_eggs", blank=True, null=True,
        on_delete=models.SET_NULL) 
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        db_table = "CustomerRequests"
        verbose_name = 'CustomerRequest'
        verbose_name_plural = "CustomerRequests"
        managed = True
    
    def save(self, *args, **kwargs):
        prefix = "REQ-"
        unique_id = str(uuid.uuid4().hex[:8])
        self.requestcode = f"{prefix}{unique_id}"
        super(CustomerRequest, self).save(*args, **kwargs)
        
    def get_absolute_url(self):
        return '/customer_request/{}'.format(self.requestcode)