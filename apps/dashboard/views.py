from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

from apps.breeders.models import Breed


def dashboard(request):
    breeds = Breed.objects.all()

    poultry_types = breeds.values_list('poultry_type', flat=True).distinct()

    chart_data = {

        'chart_data': list(zip(poultry_types, [breeds.filter(poultry_type=poultry_type).count() for poultry_type in poultry_types])),

    }
    return render(request, 'pages/ecommerce/overview.html', {'chart_data': chart_data})
