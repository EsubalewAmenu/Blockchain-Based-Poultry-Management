from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.gis.geos import Point
from .models import *

# Create your views here.

def hatchery_list(request):
    hatcheries = Hatchery.objects.all()
    paginator = Paginator(hatcheries, 10)  # Show 10 hatcheries per page
    
    page_number = request.GET.get('page')
    hatcheries = paginator.get_page(page_number)
    return render(request, 'pages/ecommerce/hatchery/list.html', {'hatcheries': hatcheries})


def hatchery_detail(request, name):
    hatchery = Hatchery.objects.get(name=name)
    if request.method == 'POST':
        # Update hatchery instance with the new data from the request
        hatchery.name = request.POST.get('name', hatchery.name)
        hatchery.email = request.POST.get('email', hatchery.email)
        hatchery.phone = request.POST.get('phone', hatchery.phone)
        hatchery.address = request.POST.get('address', hatchery.address)
        latitude_str = request.POST.get('latitude')
        longitude_str = request.POST.get('longitude')

        # Initialize latitude and longitude
        hatchery.latitude = hatchery.latitude
        hatchery.longitude = hatchery.longitude

        # Validate and convert latitude
        if latitude_str:
            try:
                hatchery.latitude = float(latitude_str)
            except ValueError:
                # Handle the case where conversion fails
                # You can log an error or set latitude to None
                hatchery.latitude = hatchery.latitude

        # Validate and convert longitude
        if longitude_str:
            try:
                hatchery.longitude = float(longitude_str)
            except ValueError:
                # Handle the case where conversion fails
                # You can log an error or set longitude to None
                hatchery.longitude = hatchery.longitude
        hatchery.totalcapacity = request.POST.get('totalcapacity', hatchery.totalcapacity)

        # Handle file upload
        if request.FILES.get('photo'):
            hatchery.photo = request.FILES['photo']

        # Save the updated hatchery instance
        hatchery.save()
        return redirect('hatchery_list')
    return render(request, 'pages/ecommerce/hatchery/details.html', {'hatchery': hatchery})


def hatchery_update(request, name):
    hatchery = Hatchery.objects.get(name=name)
    if request.method == 'POST':
        # Update hatchery instance with the new data from the request
        hatchery.name = request.POST.get('name', hatchery.name)
        hatchery.email = request.POST.get('email', hatchery.email)
        hatchery.phone = request.POST.get('phone', hatchery.phone)
        hatchery.address = request.POST.get('address', hatchery.address)
        latitude_str = request.POST.get('latitude')
        longitude_str = request.POST.get('longitude')

        # Initialize latitude and longitude
        hatchery.latitude = hatchery.latitude
        hatchery.longitude = hatchery.longitude

        # Validate and convert latitude
        if latitude_str:
            try:
                hatchery.latitude = float(latitude_str)
            except ValueError:
                # Handle the case where conversion fails
                # You can log an error or set latitude to None
                hatchery.latitude = hatchery.latitude

        # Validate and convert longitude
        if longitude_str:
            try:
                hatchery.longitude = float(longitude_str)
            except ValueError:
                # Handle the case where conversion fails
                # You can log an error or set longitude to None
                hatchery.longitude = hatchery.longitude
        hatchery.totalcapacity = request.POST.get('totalcapacity', hatchery.totalcapacity)

        # Handle file upload
        if request.FILES.get('photo'):
            hatchery.photo = request.FILES['photo']

        # Save the updated hatchery instance
        hatchery.save()
        return redirect('hatchery_list')
    return render(request, 'pages/ecommerce/hatchery/details.html', {'hatchery': hatchery})

def hatcher_create(request):
    if request.method == 'POST':
        name = request.POST['name']
        photo = request.FILES['photo']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        latitude_str = request.POST.get('latitude', None)
        longitude_str = request.POST.get('longitude', None)

        # Initialize latitude and longitude
        latitude = None
        longitude = None

        # Validate and convert latitude
        if latitude_str:
            try:
                latitude = float(latitude_str)
            except ValueError:
                # Handle the case where conversion fails
                # You can log an error or set latitude to None
                latitude = None

        # Validate and convert longitude
        if longitude_str:
            try:
                longitude = float(longitude_str)
            except ValueError:
                # Handle the case where conversion fails
                # You can log an error or set longitude to None
                longitude = None

        # Check if both latitude and longitude are valid before creating the Point
        if latitude is not None and longitude is not None:
            location = Point(longitude, latitude, srid=4326)  # Correct SRID to 4326
        else:
            # Handle the case where location data is incomplete
            location = None
        totalcapacity = request.POST['totalcapacity']

        hatchery = Hatchery(name=name, photo=photo, email=email, phone=phone, address=address, location=location, latitude=latitude, longitude=longitude, totalcapacity=totalcapacity)
        hatchery.save()
        return redirect('hatchery_list')
    else:
        return render(request, 'pages/ecommerce/hatchery/create.html')

@login_required
def hatchery_delete(request, name):
    hatchery = get_object_or_404(Hatchery, name=name)
    
    if request.method == 'POST':
        hatchery.delete()
        messages.success(request, 'Hatchery deleted successfully.')
        return redirect('hatchery_list')  # Redirect to the hatchery list view after deletion
    
    messages.error(request, 'Invalid request method.')
    return redirect('hatchery_list')
    
def incubator_list(request):
    incubators = Incubators.objects.all().select_related('hatchery') 
    paginator = Paginator(incubators, 10)
    
    page_number = request.GET.get('page')
    incubators = paginator.get_page(page_number)
    return render(request, 'pages/ecommerce/incubators/list.html', {'incubators': incubators})
    
def incubator_create(request):
    hatcheries = Hatchery.objects.all()
    
    if request.method == 'POST':
        hatchery = Hatchery.objects.get(id=request.POST['hatchery'])
        incubatortype = request.POST['incubatortype']
        manufacturer = request.POST['manufacturer']
        model = request.POST['model']
        year = request.POST['year']
        code = request.POST['code']
        
        incubator = Incubators(
            hatchery=hatchery,
            incubatortype=incubatortype,
            manufacturer=manufacturer,
            model=model,
            year=year,
            code=code
        )
        incubator.save()
        
        return redirect('incubator_list')
    
    return render(request, 'pages/ecommerce/incubators/create.html', {'hatcheries': hatcheries})

def incubator_detail(request, code):
    incubator = get_object_or_404(Incubators, code=code)
    if request.method == 'POST':
        # Update incubator instance with the new data from the request
        incubator.hatchery = Hatchery.objects.get(id=request.POST['hatchery'])
        incubator.incubatortype = request.POST['incubatortype']
        incubator.manufacturer = request.POST['manufacturer']
        incubator.model = request.POST['model']
        incubator.year = request.POST['year']
        incubator.code = request.POST['code']
        incubator.manufacturer_details = request.POST.get('manufacturer_details', '')
        
        # Save the updated incubator instance
        incubator.save()
        messages.success(request, 'Incubator updated successfully.')
        return redirect('incubator_detail', code=code)  # Redirect to the incubator detail page after saving
    
    return render(request, 'pages/ecommerce/incubators/details.html', {'incubator': incubator})

def incubator_update(request, code):
    incubator = get_object_or_404(Incubators, code=code)
    
    if request.method == 'POST':
        # Update incubator instance with the new data from the request
        incubator.hatchery = Hatchery.objects.get(id=request.POST['hatchery'])
        incubator.incubatortype = request.POST['incubatortype']
        incubator.manufacturer = request.POST['manufacturer']
        incubator.model = request.POST['model']
        incubator.year = request.POST['year']
        incubator.code = request.POST['code']
        incubator.manufacturer_details = request.POST.get('manufacturer_details', '')
        
        # Save the updated incubator instance
        incubator.save()
        messages.success(request, 'Incubator updated successfully.')
        return redirect('incubator_detail', code=code)  # Redirect to the incubator detail page after saving
    
    # Render the template with the incubator instance
    return render(request, 'pages/ecommerce/incubators/details.html', {'incubator': incubator})

def incubator_delete(request, code):
    incubator = get_object_or_404(Incubators, code=code)
    
    if request.method == 'POST':
        incubator.delete()
        messages.success(request, 'Incubator deleted successfully.')
        return redirect('incubator_list')
    
    return redirect('incubator_list')

def incubator_capacity_list(request):
    capacity_list = IncubatorCapacity.objects.all()
    paginator = Paginator(capacity_list, 10)  # Show 10 breeders per page
    
    page_number = request.GET.get('page')
    capacity_list = paginator.get_page(page_number)
    return render(request, 'pages/ecommerce/incubators/incubator_capacity/list.html', {'capacity_list': capacity_list})

@csrf_exempt
def incubator_capacity_create(request):
    incubators = Incubators.objects.all()
    
    if request.method == 'POST':
        try:
            incubator = Incubators.objects.get(id=request.POST['incubator'])
            breed = request.POST['breed']
            capacity = int(request.POST['capacity'])
            occupied = int(request.POST['occupied'])
            
            # Create a new IncubatorCapacity instance
            new_capacity = IncubatorCapacity(
                incubator=incubator,
                breed=breed,
                capacity=capacity,
                occupied=occupied
            )
            new_capacity.save()  # This will automatically calculate the available slots
            
            return redirect('incubator_capacity_list')  # Redirect to the list view after creation
        except Exception as e:
            print(f"Error creating incubator capacity: {e}")
            messages.error(request, "Error creating incubator capacity. Please try again.")
    
    return render(request, 'pages/ecommerce/incubators/incubator_capacity/create.html', {'incubators': incubators})

def incubator_capacity_details(request, id):
    capacity = get_object_or_404(IncubatorCapacity, id=id)
    incubators = Incubators.objects.all()
    
    if request.method == 'POST':
        incubator = Incubators.objects.get(id=request.POST['incubator'])
        breed = request.POST['breed']
        capacity_value = int(request.POST['capacity'])
        occupied_value = int(request.POST['occupied'])
        
        capacity.incubator = incubator
        capacity.breed = breed
        capacity.capacity = capacity_value
        capacity.occupied = occupied_value
        capacity.save()  
        
        messages.success(request, 'Incubator capacity updated successfully.')
        return redirect('incubator_capacity_list')  
    
    return render(request, 'pages/ecommerce/incubators/incubator_capacity/details.html', {
        'capacity': capacity,
        'incubators': incubators
    })
    
def incubator_capacity_update(request, id):
    capacity = get_object_or_404(IncubatorCapacity, id=id)
    incubators = Incubators.objects.all()
    
    if request.method == 'POST':
        incubator = Incubators.objects.get(id=request.POST['incubator'])
        breed = request.POST['breed']
        capacity_value = int(request.POST['capacity'])
        occupied_value = int(request.POST['occupied'])
        
        capacity.incubator = incubator
        capacity.breed = breed
        capacity.capacity = capacity_value
        capacity.occupied = occupied_value
        capacity.save()  
        
        messages.success(request, 'Incubator capacity updated successfully.')
        return redirect('incubator_capacity_list')  
    
    return render(request, 'pages/ecommerce/incubators/incubator_capacity/details.html', {
        'capacity': capacity,
        'incubators': incubators
    })
def incubator_capacity_delete(request, id):
    incubator_capacity = get_object_or_404(IncubatorCapacity, id=id)
    
    if request.method == 'POST':
        incubator_capacity.delete()
        messages.success(request, 'Incubator capacity deleted successfully.')
        return redirect('incubator_capacity_list')
    
    return redirect('incubator_capacity_list')