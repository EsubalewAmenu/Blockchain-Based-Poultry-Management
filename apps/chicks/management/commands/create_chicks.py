from django.core.management.base import BaseCommand
from apps.breeders.models import Breed
from apps.inventory.models import Item
from apps.chicks.models import Chicks
from apps.customer.models import Customer
import random
import string

class Command(BaseCommand):
    help = "Create test data for Chicks model with seeded customer"

    def handle(self, *args, **kwargs):
        self.create_chicks()

    def create_chicks(self):
        customer = Customer.objects.first()
        if not customer:
            self.stdout.write(self.style.ERROR("No customer found. Seed customers first."))
            return

        breed = Breed.objects.first()
        if not breed:
            self.stdout.write(self.style.ERROR("No breed found. Seed breeds first."))
            return

        item = Item.objects.filter(item_type__type_name='Chicks').first()
        if not item:
            self.stdout.write(self.style.ERROR("No item found. Seed items first."))
            return

        chicks_data = [
            {'batchnumber':'CHK-001', 'number': 150, 'description': 'Healthy batch of chicks', 'age': '2024-09-01'},
            {'batchnumber':'CHK-002', 'number': 120, 'description': 'Mixed breed chicks', 'age': '2024-09-05'},
        ]

        for data in chicks_data:
            if Chicks.objects.filter(batchnumber=data['batchnumber']).exists():
                self.stdout.write(self.style.WARNING(f"Chick batch with batch number {data['batchnumber']} already exists."))
                continue
            chick= Chicks(
                batchnumber=data['batchnumber'],
                source='customer',
                customer=customer,
                breed=breed,
                item=item,
                number=data['number'],
                description=data['description'],
                age=data['age'],
            )
            item.quantity = data['number']
            item.save()
            chick.save()
            self.stdout.write(self.style.SUCCESS(f"Created chick batch: {chick.batchnumber}"))