# Generated by Django 5.0.7 on 2025-03-18 07:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0002_remove_feeds_breed_remove_feeds_chicks_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feeds',
            name='vendorcode',
        ),
    ]
