# Generated by Django 5.0.7 on 2024-08-30 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_itemtype_related_object'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='itemtype',
            name='related_object',
        ),
        migrations.AddField(
            model_name='item',
            name='quantity',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
