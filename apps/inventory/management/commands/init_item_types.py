from typing import Any
from django.core.management.base import BaseCommand
from apps.inventory.models import ItemType, Item


class Command(BaseCommand):
    help = 'Create basic item types with specified details'
    
    def handle(self, *args: Any, **options: Any):
        item_types = [{"type_name":"Chicks"}, {"type_name":"Egg"}, {"type_name":"Incubator"}]
        
        for item_type in item_types:
            if ItemType.objects.filter(type_name=item_type['type_name']).exists():
                self.stdout.write(self.style.WARNING("Item Type Already Exists"))
                continue
            item_type_obj = ItemType.objects.create(**item_type)
            item_type_obj.save()
            self.stdout.write(self.style.SUCCESS(f"Item Type {item_type_obj.type_name} Created Successfully"))
            
        items_data = [
            {'item_type_name': 'Chicks'},
            {'item_type_name': 'Egg'},
            {'item_type_name': 'Incubator'},
        ]

        # for data in items_data:
        #     item_type = ItemType.objects.get(type_name=data['item_type_name'])
        #     if Item.objects.filter(item_type=item_type).exists():
        #         self.stdout.write(self.style.WARNING(f"Item Already Exists for type {item_type.type_name}"))
        #         continue
        #     item = Item.objects.create(
        #         item_type=item_type
        #     )
        #     item.save()
        #     self.stdout.write(self.style.SUCCESS(f"Item Created Successfully for type {item_type.type_name}"))
            