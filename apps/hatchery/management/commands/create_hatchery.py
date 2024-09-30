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
                'totalcapacity': 5000
            },
            {
                'name': 'Moonlight Hatchery',
                'email': 'moonlight@example.com',
                'phone': '0987654321',
                'address': '456 Incubate St',
                'latitude': 34.0522,
                'longitude': -118.2437,
                'totalcapacity': 4000
            },
        ]

        for data in hatchery_data:
            hatchery, created = Hatchery.objects.get_or_create(
                name=data['name'],
                email=data['email'],
                phone=data['phone'],
                address=data['address'],
                latitude=data['latitude'],
                longitude=data['longitude'],
                totalcapacity=data['totalcapacity'],
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created hatchery: {hatchery.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Hatchery with name {hatchery.name} already exists"))
