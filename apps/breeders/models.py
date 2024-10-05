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
from django.utils.safestring import mark_safe
from django.template.defaultfilters import truncatechars, slugify  # or truncatewords
from django.contrib.gis.db import models as gismodels

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit

from telelbirds import settings


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

    def save(self, *args, **kwargs):
        cocks = int(self.cocks) if self.cocks else 0
        hens = int(self.hens) if self.hens else 0
        butchered = int(self.butchered) if self.butchered else 0
        sold = int(self.sold) if self.sold else 0
        mortality = float(self.mortality) if self.mortality else 0.0

        # Calculate current_number based on the validated values
        self.current_number = cocks + hens - butchered - sold - mortality
        super(Breeders, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return '/breeders/{}'.format(self.batch)