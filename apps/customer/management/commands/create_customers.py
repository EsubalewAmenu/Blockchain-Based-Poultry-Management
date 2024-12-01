from django.core.management.base import BaseCommand
from apps.customer.models import Customer
import random

class Command(BaseCommand):
    help = "Create test data for Customer model"

    def handle(self, *args, **kwargs):
        self.create_customers()

    def create_customers(self):
        customer_data = [
            {'first_name': 'Henok', 'last_name': 'Alemu', 'email': 'henokalemu@gmail.com', 'phone': '+251900123456', 'address': 'Addis Ababa, Ethiopia', 'notification_sms': True, 'delivery': True, 'followup': True},
        ]

        for data in customer_data:
            customer, created = Customer.objects.get_or_create(
                email=data['email'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'phone': data['phone'],
                    'address': data['address'],
                    'notification_sms': data['notification_sms'],
                    'delivery': data['delivery'],
                    'followup': data['followup']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created customer: {customer.full_name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Customer with email {customer.email} already exists"))
