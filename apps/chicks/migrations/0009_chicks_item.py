# Generated by Django 5.0.7 on 2024-08-30 00:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chicks', '0008_chicks_egg'),
        ('inventory', '0002_itemtype_related_object'),
    ]

    operations = [
        migrations.AddField(
            model_name='chicks',
            name='item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.item'),
        ),
    ]
