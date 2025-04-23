from django.core.management.base import BaseCommand
from apps.vendor.models import Medicine

class Command(BaseCommand):
    help = "Seed the Medicine table with initial data"

    def handle(self, *args, **kwargs):
        medicine_data = [
            ("Tylosin", "Antibiotic"),
            ("Enrofloxacin", "Antibiotic"),
            ("Amoxicillin", "Antibiotic"),
            ("Newcastle Vaccine", "Vaccine"),
            ("Marek’s Disease Vaccine", "Vaccine"),
            ("Gumboro Vaccine", "Vaccine"),
            ("Vitamin A, D, E, K", "Vitamin & Mineral"),
            ("Electrolytes", "Vitamin & Mineral"),
            ("Calcium Supplements", "Vitamin & Mineral"),
            ("Albendazole", "Dewormer"),
            ("Levamisole", "Dewormer"),
            ("Amprolium", "Coccidiostat"),
            ("Toltrazuril", "Coccidiostat"),
            ("Nystatin", "Antifungal"),
            ("Metronidazole", "Antiprotozoal"),
            ("Meloxicam", "Pain Reliever"),
            ("Aspirin", "Pain Reliever"),
        ]

        medicines = [Medicine(name=name, category=category) for name, category in medicine_data]
        Medicine.objects.bulk_create(medicines, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS("Successfully seeded Medicine table!"))
