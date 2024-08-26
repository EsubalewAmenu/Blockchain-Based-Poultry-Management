# Generated by Django 5.0.7 on 2024-08-13 10:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hatchery', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incubatorcapacity',
            name='incubator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='incubatorcapacity_incubator', to='hatchery.incubators'),
        ),
    ]
