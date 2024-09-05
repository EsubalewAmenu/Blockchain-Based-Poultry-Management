# Generated by Django 5.0.7 on 2024-08-28 07:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chicks', '0007_remove_chicks_egg_chicks_hatching_chicks_number'),
        ('customer', '0002_alter_customer_email_alter_eggs_batchnumber'),
    ]

    operations = [
        migrations.AddField(
            model_name='chicks',
            name='egg',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='customer.eggs'),
        ),
    ]