from django.db import models
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.core.files import File
from apps.chicks.models import Chicks
from apps.customer.models import Eggs
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
import random
import string

class Tracker(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True, db_index=True)
    egg = models.OneToOneField(Eggs, on_delete=models.CASCADE, null=True, blank=True, related_name='egg_tracker')
    chick = models.OneToOneField(Chicks, on_delete=models.CASCADE, null=True, blank=True, related_name='chick_tracker')
    tracker_code = models.CharField(max_length=12, unique=True, editable=False)
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)

    def generate_tracker_code(self):
        while True:
            random_suffix = ''.join(random.choices(string.digits, k=4))
            unique_code = f'TRK-{random_suffix}'
            if not Tracker.objects.filter(tracker_code=unique_code).exists():
                return unique_code

    def generate_pdf_url(self, request):
        """
        Generate the full URL that points to the PDF view for this tracker,
        using the current site's domain.
        """
        site = get_current_site(request)
        base_url = reverse('tracker_pdf', kwargs={'tracker_code': self.tracker_code})
        full_url = f'{site.scheme}://{site.domain}{base_url}'  # Create the full URL
        return full_url

    def generate_barcode_data(self, request):
        """
        Generate the URL that points to the PDF view, encoded into the barcode.
        The request is needed to obtain the current site.
        """
        return self.generate_pdf_url(request)

    def save(self, *args, **kwargs):
        if not self.tracker_code:
            self.tracker_code = self.generate_tracker_code()

        
        ean = barcode.get('code128', self.tracker_code, writer=ImageWriter())

        buffer = BytesIO()
        ean.write(buffer)
        buffer.seek(0)

        self.barcode_image.save(f'{self.tracker_code}.png', File(buffer), save=False)

        super().save(*args, **kwargs)


    def __str__(self):
        return f'Tracker Code: {self.tracker_code}'
