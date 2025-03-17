# Generated by Django 5.0.7 on 2025-03-17 07:39

import django.contrib.gis.db.models.fields
import django.db.models.deletion
import imagekit.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('breeders', '0005_breeders_policyid_breeders_txhash'),
        ('inventory', '0006_itemrequest_txhash'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('full_name', models.CharField(blank=True, max_length=50, null=True)),
                ('photo', imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to='vendor_photos')),
                ('email', models.EmailField(blank=True, max_length=50, null=True, unique=True)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('address', models.CharField(blank=True, max_length=50, null=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('vendortype', models.CharField(blank=True, max_length=50, null=True)),
                ('notification_sms', models.BooleanField(blank=True, max_length=50, null=True)),
                ('delivery', models.BooleanField(blank=True, max_length=50, null=True)),
                ('followup', models.BooleanField(blank=True, max_length=50, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'vendor',
                'verbose_name_plural': 'vendors',
                'db_table': 'vendors',
                'ordering': ['created'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Feeds',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('batchnumber', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('source', models.CharField(blank=True, choices=[('vendor', 'vendor'), ('farm', 'farm')], default='vendor', max_length=50, null=True)),
                ('chicks', models.CharField(blank=True, max_length=50, null=True)),
                ('vendorcode', models.CharField(blank=True, max_length=50, null=True)),
                ('photo', imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to='feeds_photos')),
                ('brought', models.IntegerField(blank=True, null=True)),
                ('returned', models.IntegerField(blank=True, null=True)),
                ('received', models.IntegerField(blank=True, max_length=50, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('breed', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='feeds_breed', to='breeders.breed')),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.item')),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='feeds_vendor', to='vendor.vendor')),
            ],
            options={
                'verbose_name': 'feed',
                'verbose_name_plural': 'feeds',
                'db_table': 'feeds',
                'ordering': ['created'],
                'managed': True,
            },
        ),
    ]
