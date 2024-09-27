from typing import Any
from django.core.management.base import BaseCommand
from apps.inventory.models import ItemType


class Command(BaseCommand):
    help = 'Create basic item types with specified details'
    
    def handle(self, *args: Any, **options: Any):
        item_types = [{"type_name":"Chick"}, {"type_name":"Egg"}, {"type_name":"Incubator"}]
        
        for item_type in item_types:
            if ItemType.objects.filter(type_name=item_type['type_name']).exists():
                self.stdout.write(self.style.WARNING("Item Type Already Exists"))
                continue
            item_type_obj = ItemType.objects.create(**item_type)
            item_type_obj.save()
            self.stdout.write(self.style.SUCCESS(f"Item Type {item_type_obj.type_name} Created Successfully"))
            