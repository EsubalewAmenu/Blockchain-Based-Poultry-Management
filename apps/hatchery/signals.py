from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.chicks.models import Chicks
from apps.customer.models import Eggs
from apps.dashboard.models import Tracker
from .models import EggSetting, Incubation, Hatching


@receiver(post_save, sender=EggSetting)
def create_user_settings(sender, instance, created, **kwargs):
    if instance.is_approved:
        incubation = Incubation.objects.create(eggsetting=instance, breeders=instance.breeders, customer=instance.customer, eggs=instance.eggs)
        incubation.save()
        instance.egg.received -= int(instance.eggs)
        instance.egg.save()
        instance.egg.item.quantity -= int(instance.eggs)
        instance.egg.item.save()
    else:
        pass
    
@receiver(post_save, sender=Chicks)
def create_chick_tracker(sender, instance, created, **kwargs):
    if created:
        tracker = Tracker.objects.create(chick=instance)
        tracker.save()
        
@receiver(post_save, sender=Eggs)
def create_egg_tracker(sender, instance, created, **kwargs):
    if created:
        tracker = Tracker.objects.create(egg=instance)
        tracker.save()