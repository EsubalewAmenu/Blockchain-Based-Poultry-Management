# Generated by Django 5.0.7 on 2024-11-16 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_item_policyid_item_txhash'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemrequest',
            name='txHash',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]