# Generated by Django 5.0.7 on 2024-08-26 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chicks', '0005_alter_chicks_chick_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chicks',
            name='batchnumber',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]