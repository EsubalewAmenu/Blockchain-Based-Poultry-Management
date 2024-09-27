# Generated by Django 5.0.7 on 2024-08-26 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('breeders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='breed',
            name='code',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='breeders',
            name='batch',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
