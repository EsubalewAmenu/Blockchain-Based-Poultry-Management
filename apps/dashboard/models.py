from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.files import File
from apps.chicks.models import Chicks
from apps.customer.models import Eggs
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
import qrcode
import random
import string

class Tracker(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True, db_index=True)
    egg = models.OneToOneField(Eggs, on_delete=models.CASCADE, null=True, blank=True, related_name='egg_tracker')
    chick = models.OneToOneField(Chicks, on_delete=models.CASCADE, null=True, blank=True, related_name='chick_tracker')
    tracker_code = models.CharField(max_length=12, unique=True, editable=False)
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)
    qr_code_image = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    def generate_tracker_code(self):
        while True:
            random_suffix = ''.join(random.choices(string.digits, k=4))
            unique_code = f'TRK-{random_suffix}'
            if not Tracker.objects.filter(tracker_code=unique_code).exists():
                return unique_code

    def generate_pdf_url(self):
        """
        Generate the full URL that points to the PDF view for this tracker,
        using the current site's domain.
        """
        site = settings.SITE_URL
        base_url = reverse('tracker_public', kwargs={'tracker_code': self.tracker_code})
        full_url = f'{site}{base_url}'
        return full_url

    def generate_qr_code(self, tracker_public_url):
        """
        Generate a QR code that contains the URL to the PDF.
        """
        img = qrcode.make(tracker_public_url, box_size=5, border=0)

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        self.qr_code_image.save(f'{self.tracker_code}_qr.png', File(buffer), save=False)

    def save(self, *args, **kwargs):
        if not self.tracker_code:
            self.tracker_code = self.generate_tracker_code()

        tracker_public_url = self.generate_pdf_url()

        self.generate_qr_code(tracker_public_url)

        barcode_data = f"{self.tracker_code}"

        ean = barcode.get('code128', barcode_data, writer=ImageWriter())
        writer_options = {
            'write_text': False,
        }

        buffer = BytesIO()
        ean.write(buffer, options=writer_options)
        buffer.seek(0)

        self.barcode_image.save(f'{self.tracker_code}.png', File(buffer), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f'Tracker Code: {self.tracker_code}'
