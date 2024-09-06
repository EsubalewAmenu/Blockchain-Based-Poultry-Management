from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.chicks.models import Chicks
from .models import EggSetting, Incubation, Hatching


@receiver(post_save, sender=EggSetting)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        incubation = Incubation.objects.create(eggsetting=instance, breeders=instance.breeders, customer=instance.customer, eggs=instance.eggs)
        incubation.save()
        instance.egg.received -= int(instance.eggs)
        instance.egg.save()
        instance.egg.item.quantity -= int(instance.eggs)
        instance.egg.item.save()
        
# @receiver(post_save, sender=Hatching)
# def create_chicks(sender, instance, created, **kwargs):
#     if created:
#         chick = Chicks.objects.create(breed=instance.breeders.breed, source="hatching", hatching=instance, number=instance.chicks_hatched)
#         chick.save()