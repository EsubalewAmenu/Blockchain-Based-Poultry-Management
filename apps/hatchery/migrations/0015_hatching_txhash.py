# Generated by Django 5.0.7 on 2024-11-16 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hatchery', '0014_candling_txhash'),
    ]

    operations = [
        migrations.AddField(
            model_name='hatching',
            name='txHash',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]