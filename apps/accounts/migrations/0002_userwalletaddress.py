# Generated by Django 5.0.7 on 2024-09-24 07:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserWalletAddress',
            fields=[
                ('id', models.BigAutoField(db_index=True, primary_key=True, serialize=False, unique=True)),
                ('address', models.CharField(max_length=255)),
                ('provider', models.CharField(blank=True, max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='wallet_address', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'User Wallet Addresses',
            },
        ),
    ]
