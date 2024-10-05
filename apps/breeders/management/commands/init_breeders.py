from django.core.management.base import BaseCommand
from apps.breeders.models import Breed, Breeders
import random

class Command(BaseCommand):
    help = "Create test data for Breed and Breeders models"

    def handle(self, *args, **kwargs):
        self.create_breeds()
        self.create_breeders()

    def create_breeds(self):
        breed_data = [
            {'code': 'BRD001', 'poultry_type': 'Chicken', 'breed': 'Rhode Island Red', 'purpose': 'Dual-purpose', 'eggs_year': 250, 'adult_weight': 3.9, 'description': 'A hardy breed known for good egg production.'},
            {'code': 'BRD002', 'poultry_type': 'Duck', 'breed': 'Pekin', 'purpose': 'Meat', 'eggs_year': 150, 'adult_weight': 3.6, 'description': 'Popular meat duck with a white plumage.'},
            {'code': 'BRD003', 'poultry_type': 'Chicken', 'breed': 'Leghorn', 'purpose': 'Egg-laying', 'eggs_year': 300, 'adult_weight': 2.5, 'description': 'Known for excellent egg production.'}
        ]
        
        for data in breed_data:
            if Breed.objects.filter(code=data['code']).exists():
                self.stdout.write(self.style.WARNING(f"Breed with code {data['code']} already exists."))
                continue
            breed = Breed(
                    code=data['code'],
                    poultry_type=data['poultry_type'],
                    breed=data['breed'],
                    purpose=data['purpose'],
                    eggs_year=data['eggs_year'],
                    adult_weight=data['adult_weight'],
                    description=data['description']
            )
            breed.save()
            self.stdout.write(self.style.SUCCESS(f"Created breed: {breed.code}"))

    def create_breeders(self):
        breeders_data = [
            {'batch': 'BRDR001', 'breed': 1, 'hens': 10, 'cocks': 2, 'mortality': 0.5, 'butchered': 1, 'sold': 0},
            {'batch': 'BRDR002', 'breed': 2, 'hens': 8, 'cocks': 3, 'mortality': 1.0, 'butchered': 0, 'sold': 2},
            {'batch': 'BRDR003', 'breed': 3, 'hens': 15, 'cocks': 1, 'mortality': 0.2, 'butchered': 0, 'sold': 3}
        ]

        for data in breeders_data:
            try:
                breed = Breed.objects.get(id=data['breed'])
                breeder, created = Breeders.objects.get_or_create(
                    batch=data['batch'],
                    defaults={
                        'breed': breed,
                        'hens': data['hens'],
                        'cocks': data['cocks'],
                        'mortality': data['mortality'],
                        'butchered': data['butchered'],
                        'sold': data['sold']
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created breeder: {breeder.batch}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Breeder with batch {breeder.batch} already exists."))
            except Breed.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Breed with id {data['breed']} does not exist"))
