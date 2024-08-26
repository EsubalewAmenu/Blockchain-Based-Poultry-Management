from django.shortcuts import render
from django.db.models import Count
from apps.customer.models import Customer
from apps.breeders.models import Breed, Breeders
from apps.chicks.models import Chicks
import random

def generate_random_color():
    """Generate a random hex color."""
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def dashboard(request):
    breeds = Breed.objects.all()
    customer = Customer.objects.all()
    chicks = Chicks.objects.all()

    # Aggregate data for the pie chart
    chart_data = chicks.values('breed__breed').annotate(count=Count('id')).order_by('breed__breed')

    # Prepare data for the chart
    labels = [data['breed__breed'] for data in chart_data]
    counts = [data['count'] for data in chart_data]

    # Generate random colors for each breed
    colors = [generate_random_color() for _ in labels]

    chart_data = {
        'labels': labels,
        'counts': counts,
        'colors': colors,  # Pass colors to the context
        'chart_data': zip(labels, counts)  # For rendering badges
    }
    
    breeders_by_breed = {}
    for breed in breeds:
        breeders = Breeders.objects.filter(breed=breed)
        breeders_by_breed[breed.breed] = breeders

    return render(request, 'pages/ecommerce/overview.html', {
        'chart_data': chart_data,
        'breeders_by_breed': breeders_by_breed,
        'breeds_count': breeds.count(),
        'customer_count': customer.count(),
        'chicks_count': chicks.count(),
    })