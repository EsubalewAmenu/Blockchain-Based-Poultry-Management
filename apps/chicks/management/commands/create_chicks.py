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
            {'number': 150, 'description': 'Healthy batch of chicks', 'age': '2024-09-01'},
            {'number': 120, 'description': 'Mixed breed chicks', 'age': '2024-09-05'},
        ]

        for data in chicks_data:
            chick = Chicks(
                source='customer',
                customer=customer,
                breed=breed,
                item=item,
                number=data['number'],
                description=data['description'],
                age=data['age'],
            )
            chick.batchnumber = self.generate_unique_batchnumber()
            item.quantity = data['number']
            item.save()
            chick.save()

            self.stdout.write(self.style.SUCCESS(f"Created chick batch: {chick.batchnumber}"))

    def generate_unique_batchnumber(self):
        while True:
            random_suffix = ''.join(random.choices(string.digits, k=4))
            unique_code = f'CHK-{random_suffix}'
            if not Chicks.objects.filter(batchnumber=unique_code).exists():
                return unique_code