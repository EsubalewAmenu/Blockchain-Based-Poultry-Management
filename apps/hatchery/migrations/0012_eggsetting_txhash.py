# Generated by Django 5.0.7 on 2024-11-15 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hatchery', '0011_eggsetting_available_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='eggsetting',
            name='txHash',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
