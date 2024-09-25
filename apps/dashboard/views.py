from django.shortcuts import render
from django.db.models import Count
from apps.customer.models import Customer
from apps.breeders.models import Breed, Breeders
from apps.chicks.models import Chicks
from apps.inventory.models import Item, ItemRequest
from datetime import datetime, timedelta
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
import random

def generate_random_color(base_hex):
    # Convert base hex to RGB
    base_r = int(base_hex[1:3], 16)
    base_g = int(base_hex[3:5], 16)
    base_b = int(base_hex[5:7], 16)
    
    # Generate random brightness adjustment
    brightness_adjustment = random.randint(-50, 50)
    
    # Adjust brightness of each color channel
    r = max(0, min(255, base_r + brightness_adjustment))
    g = max(0, min(255, base_g + brightness_adjustment))
    b = max(0, min(255, base_b + brightness_adjustment))
    
    # Convert adjusted RGB to hex
    hex_r = "{:02X}".format(int(r))
    hex_g = "{:02X}".format(int(g))
    hex_b = "{:02X}".format(int(b))
    
    return "#" + hex_r + hex_g + hex_b

def dashboard(request):
    current_datetime = datetime.now()
    end_date = timezone.now()
    year = int(request.GET.get('graph_year', end_date.year))
    breeds = Breed.objects.all()
    customer = Customer.objects.all()
    chicks = Chicks.objects.all()

    chart_data = chicks.values('breed__breed').annotate(count=Count('id')).order_by('breed__breed')

    labels = [data['breed__breed'] for data in chart_data]
    counts = [data['count'] for data in chart_data]

    colors = [generate_random_color("#52796f") for _ in labels]

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
        
    all_months = [datetime(year, month, 1) for month in range(1, 13)]
    item_labels = [month.strftime('%B') for month in all_months]
    item_data_values = [0] * 12
    
    item_data = Item.objects.annotate(
        month=TruncMonth('created_at')
    ).filter(created_at__year=year).values('month').annotate(count=Count('id')).order_by('month')
    
    for item in item_data:
        month_index = item['month'].month - 1
        item_data_values[month_index] = item['count']
        
    item_type_data = Item.objects.values('item_type__type_name').annotate(count=Count('id')).order_by('item_type__type_name')
    
    item_type_labels = [data['item_type__type_name'] for data in item_type_data]
    item_type_counts = [data['count'] for data in item_type_data]
    
    approved_requests = ItemRequest.objects.filter(is_approved=True)[:6]

    return render(request, 'pages/poultry/overview.html', {
        'chart_data': chart_data,
        'breeders_by_breed': breeders_by_breed,
        'breeds_count': breeds.count(),
        'customer_count': customer.count(),
        'chicks_count': chicks.count(),
        'total_item_graph_data': {
            'labels': item_labels,
            'data': item_data_values
        },
        'item_type_labels': item_type_labels,
        'item_type_counts': item_type_counts,
        'approved_requests': approved_requests,
    })