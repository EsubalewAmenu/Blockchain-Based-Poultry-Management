from django.core.management.base import BaseCommand
from apps.hatchery.models import Hatchery
import random
import string

class Command(BaseCommand):
    help = "Create test data for Hatchery model"

    def handle(self, *args, **kwargs):
        self.create_hatchery()

    def create_hatchery(self):
        hatchery_data = [
            {
                'name': 'Sunrise Hatchery',
                'email': 'sunrise@example.com',
                'phone': '1234567890',
                'address': '123 Hatchery Rd',
                'latitude': 35.6895,
                'longitude': 139.6917,
                'total_capacity': 5000  # Ensure this matches the model field name
            },
            {
                'name': 'Moonlight Hatchery',
                'email': 'moonlight@example.com',
                'phone': '0987654321',
                'address': '456 Incubate St',
                'latitude': 34.0522,
                'longitude': -118.2437,
                'total_capacity': 4000  # Ensure this matches the model field name
            },
        ]

        for data in hatchery_data:
            if Hatchery.objects.filter(email=data['email']).exists():
                self.stdout.write(self.style.WARNING(f"Hatchery with email {data['email']} already exists."))
                continue
            hatchery, created = Hatchery.objects.get_or_create(
                name=data['name'],
                email=data['email'],
                phone=data['phone'],
                address=data['address'],
                totalcapacity=data['total_capacity']
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created hatchery: {hatchery.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Hatchery with name {hatchery.name} already exists"))
