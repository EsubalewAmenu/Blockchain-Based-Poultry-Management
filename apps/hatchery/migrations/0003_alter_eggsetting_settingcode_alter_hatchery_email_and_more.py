# Generated by Django 5.0.7 on 2024-08-26 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hatchery', '0002_alter_incubatorcapacity_incubator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eggsetting',
            name='settingcode',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='hatchery',
            name='email',
            field=models.EmailField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='incubators',
            name='code',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]