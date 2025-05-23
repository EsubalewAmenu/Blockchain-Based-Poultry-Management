# Generated by Django 5.0.7 on 2025-03-18 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feeds',
            name='breed',
        ),
        migrations.RemoveField(
            model_name='feeds',
            name='chicks',
        ),
        migrations.RemoveField(
            model_name='feeds',
            name='source',
        ),
        migrations.AddField(
            model_name='feeds',
            name='feedtype',
            field=models.CharField(blank=True, choices=[('Starter', 'Starter'), ('Grower', 'Grower'), ('Finisher', 'Finisher'), ('Layer', 'Layer'), ('Breeder', 'Breeder'), ('Medicated', 'Medicated'), ('Organic_Natural', 'Organic_Natural'), ('Scratch', 'Scratch')], default='Layer', max_length=50, null=True),
        ),
    ]
