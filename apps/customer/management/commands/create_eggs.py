from django.core.management.base import BaseCommand
from apps.inventory.models import Item
from apps.breeders.models import Breed
from apps.customer.models import Customer, Eggs
import random
import string

class Command(BaseCommand):
    help = "Create test data for Eggs model with seeded customer"

    def handle(self, *args, **kwargs):
        self.create_eggs()

    def create_eggs(self):
        # Sample test data
        customer = Customer.objects.first()
        if not customer:
            self.stdout.write(self.style.ERROR("No customer found. Seed customers first."))
            return

        breed = Breed.objects.first()
        if not breed:
            self.stdout.write(self.style.ERROR("No breed found. Seed breeds first."))
            return

        item = Item.objects.filter(item_type__type_name='Egg').first()
        if not item:
            self.stdout.write(self.style.ERROR("No item found. Seed items first."))
            return

        eggs_data = [
            {'source': 'customer', 'brought': 100, 'returned': 5, 'received': 95},
        ]

        for data in eggs_data:
            egg = Eggs(
                source=data['source'],
                customer=customer if data['source'] == 'customer' else None,
                breed=breed,
                item=item,
                brought=data['brought'],
                returned=data['returned'],
                received=data['received'],
            )
            egg.batchnumber = self.generate_unique_batchnumber()
            item.quantity = data['received']
            item.save()
            egg.save()

            self.stdout.write(self.style.SUCCESS(f"Created egg batch: {egg.batchnumber}"))

    def generate_unique_batchnumber(self):
        while True:
            random_suffix = ''.join(random.choices(string.digits, k=4))
            unique_code = f'EG-{random_suffix}'
            if not Eggs.objects.filter(batchnumber=unique_code).exists():
                return unique_code
