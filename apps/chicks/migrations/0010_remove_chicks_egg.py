# Generated by Django 5.0.7 on 2024-08-30 06:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chicks', '0009_chicks_item'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chicks',
            name='egg',
        ),
    ]
