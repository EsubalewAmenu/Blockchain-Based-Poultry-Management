from django.db import models
import random
import string

# Create your models here.
class ItemType(models.Model):
    id = models.BigAutoField(unique=True, db_index=True, primary_key=True)
    code = models.CharField(max_length=50, blank=True, unique=True)
    type_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_item_type_code()
        
        super(ItemType, self).save(*args, **kwargs)

    def generate_unique_item_type_code(self):
        while True:
            random_suffix = ''.join(random.choices(string.digits, k=4))
            unique_code = f'IT-{random_suffix}'
            if not ItemType.objects.filter(code=unique_code).exists():
                return unique_code
    
class Item(models.Model):
    id = models.BigAutoField(unique=True, db_index=True, primary_key=True)
    code = models.CharField(max_length=50, blank=True, unique=True)
    item_type = models.ForeignKey(ItemType, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_item_code()
        
        super(Item, self).save(*args, **kwargs)

    def generate_unique_item_code(self):
        while True:
            random_suffix = ''.join(random.choices(string.digits, k=4))
            unique_code = f'I-{random_suffix}'
            if not Item.objects.filter(code=unique_code).exists():
                return unique_code 