# Generated by Django 5.0.7 on 2024-10-15 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hatchery', '0010_alter_eggsetting_item_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='eggsetting',
            name='available_quantity',
            field=models.IntegerField(blank=True, max_length=50, null=True),
        ),
    ]
