# Generated by Django 5.0.7 on 2024-08-25 21:23

import imagekit.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chicks', '0004_chicks_chick_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chicks',
            name='chick_photo',
            field=imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to='chicks_photos'),
        ),
    ]
