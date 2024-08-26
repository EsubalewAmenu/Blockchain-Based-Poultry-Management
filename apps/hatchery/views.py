from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.gis.geos import Point
from apps.breeders.models import *
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
        capacity = request.POST['capacity']
        
        incubator = Incubators(
            hatchery=hatchery,
            incubatortype=incubatortype,
            manufacturer=manufacturer,
            model=model,
            year=year,
            code=code
        )
        incubator.save()
        incubator_capacity = IncubatorCapacity(
            incubator=incubator,
            capacity=capacity
        )
        
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

#Egg Settings
def egg_setting_list(request):
    egg_settings = EggSetting.objects.all()
    paginator = Paginator(egg_settings, 10)
    
    page_number = request.GET.get('page')
    egg_settings = paginator.get_page(page_number)
    return render(request, 'pages/ecommerce/hatchery/egg_setting/list.html', {'egg_settings': egg_settings})

def egg_setting_detail(request, settingcode):
    egg_setting = get_object_or_404(EggSetting, settingcode=settingcode)

    if request.method == 'POST':
        egg_setting.settingcode = request.POST.get('settingcode', egg_setting.settingcode)
        egg_setting.incubator = get_object_or_404(Incubators, id=request.POST.get('incubator'))
        egg_setting.customer = get_object_or_404(Customer, id=request.POST.get('customer'))
        egg_setting.breeders = get_object_or_404(Breeders, id=request.POST.get('breeders'))
        egg_setting.eggs = request.POST.get('eggs', egg_setting.eggs)
        egg_setting.save()
        return redirect('egg_setting_detail', settingcode=egg_setting.settingcode)

    incubators = Incubators.objects.all()
    customers = Customer.objects.all()
    breeders = Breeders.objects.all()
    return render(request, 'pages/ecommerce/hatchery/egg_setting/details.html', {
        'egg_setting': egg_setting,
        'incubators': incubators,
        'customers': customers,
        'breeders': breeders
    })

def egg_setting_create(request):
    if request.method == 'POST':
        settingcode = request.POST.get('settingcode')
        incubator_id = request.POST.get('incubator')
        customer_id = request.POST.get('customer')
        breeders_id = request.POST.get('breeders')
        eggs = request.POST.get('eggs')

        incubator = get_object_or_404(Incubators, pk=incubator_id)
        customer = get_object_or_404(Customer, pk=customer_id)
        breeders = get_object_or_404(Breeders, pk=breeders_id)
        

        egg_setting = EggSetting(
            settingcode=settingcode,
            incubator=incubator,
            customer=customer,
            breeders=breeders,
            eggs=eggs
        )
        egg_setting.save()
        return redirect('egg_setting_list')

    incubators = Incubators.objects.all()
    customers = Customer.objects.all()
    breeders = Breeders.objects.all()
    return render(request, 'pages/ecommerce/hatchery/egg_setting/create.html', {
        'incubators': incubators,
        'customers': customers,
        'breeders': breeders
    })

def egg_setting_update(request, settingcode):
    egg_setting = get_object_or_404(EggSetting, settingcode=settingcode)

    if request.method == 'POST':
        egg_setting.settingcode = request.POST.get('settingcode', egg_setting.settingcode)
        egg_setting.incubator = get_object_or_404(Incubators, id=request.POST.get('incubator'))
        egg_setting.customer = get_object_or_404(Customer, id=request.POST.get('customer'))
        egg_setting.breeders = get_object_or_404(Breeders, id=request.POST.get('breeders'))
        egg_setting.eggs = request.POST.get('eggs', egg_setting.eggs)
        egg_setting.save()
        return redirect('egg_setting_detail', settingcode=egg_setting.settingcode)

    incubators = Incubators.objects.all()
    customers = Customer.objects.all()
    breeders = Breeders.objects.all()
    return render(request, 'pages/ecommerce/hatchery/egg_setting/details.html', {
        'egg_setting': egg_setting,
        'incubators': incubators,
        'customers': customers,
        'breeders': breeders
    })

def egg_setting_delete(request, settingcode):
    egg_setting = get_object_or_404(EggSetting, settingcode=settingcode)
    if request.method == 'POST':
        egg_setting.delete()
        return redirect('egg_setting_list')
    return render(request, 'egg_settings/egg_setting_confirm_delete.html', {'egg_setting': egg_setting})


@login_required
def incubation_list(request):
    incubations = Incubation.objects.all()
    paginator = Paginator(incubations, 10)
    
    page_number = request.GET.get('page')
    incubations = paginator.get_page(page_number)
    context = {
        'incubations': incubations,
    }
    return render(request, 'pages/ecommerce/hatchery/incubation/list.html', context)

## Detail View    
@login_required
def incubation_detail(request, incubationcode):
    incubation = get_object_or_404(Incubation, incubationcode=incubationcode)

    if request.method == 'POST':
        # Update the incubation instance with new data
        incubation.eggsetting = EggSetting.objects.get(id=request.POST.get('eggsetting'))
        incubation.customer = Customer.objects.get(id=request.POST.get('customer'))
        incubation.breeders = Breeders.objects.get(id=request.POST.get('breeders'))
        incubation.eggs = request.POST.get('eggs')
        incubation.save()  # Save the updated instance
        return redirect(incubation.get_absolute_url())  # Redirect to the updated detail view

    context = {
        'incubation': incubation,
        'egg_settings': EggSetting.objects.all(),  # Pass all egg settings for the dropdown
        'customers': Customer.objects.all(),        # Pass all customers for the dropdown
        'breeders': Breeders.objects.all(),         # Pass all breeders for the dropdown
    }
    return render(request, 'pages/ecommerce/hatchery/incubation/details.html', context)

## Create View
@login_required
def incubation_create(request):
    if request.method == 'POST':
        eggsetting_id = request.POST.get('eggsetting')
        customer_id = request.POST.get('customer')
        breeders_id = request.POST.get('breeders')
        eggs = request.POST.get('eggs')

        incubation = Incubation(
            eggsetting=EggSetting.objects.get(id=eggsetting_id),
            customer=Customer.objects.get(id=customer_id),
            breeders=Breeders.objects.get(id=breeders_id),
            eggs=eggs
        )
        incubation.save()
        return redirect('incubation_list')

    egg_settings = EggSetting.objects.all()
    customers = Customer.objects.all()
    breeders = Breeders.objects.all()

    context = {
        'egg_settings': egg_settings,
        'customers': customers,
        'breeders': breeders,
    }

    return render(request, 'pages/ecommerce/hatchery/incubation/create.html', context)

## Update View
@login_required
def incubation_update(request, incubationcode):
    incubation = get_object_or_404(Incubation, incubationcode=incubationcode)

    if request.method == 'POST':
        incubation.eggsetting = EggSetting.objects.get(id=request.POST.get('eggsetting'))
        incubation.customer = Customer.objects.get(id=request.POST.get('customer'))
        incubation.breeders = Breeders.objects.get(id=request.POST.get('breeders'))
        incubation.eggs = request.POST.get('eggs')
        incubation.save()
        return redirect(incubation.get_absolute_url())

    context = {
        'incubation': incubation,
        'egg_settings': EggSetting.objects.all(),
        'customers': Customer.objects.all(),
        'breeders': Breeders.objects.all(),
    }
    return render(request, 'pages/ecommerce/hatchery/incubation/details.html', context)

## Delete View
@login_required
def incubation_delete(request, incubationcode):
    incubation = get_object_or_404(Incubation, incubationcode=incubationcode)

    if request.method == 'POST':
        incubation.delete()
        return redirect('incubation_list')  # Redirect to the list view

    context = {
        'incubation': incubation,
    }
    return render(request, 'incubation/delete.html', context)

@login_required
def candling_list(request):
    """
    List all Candling records with pagination.
    """
    candlings = Candling.objects.all().order_by('-created')  # Order by created date
    paginator = Paginator(candlings, 10)  # Show 10 candlings per page
    page_number = request.GET.get('page')
    candlings = paginator.get_page(page_number)
    
    context = {
        'candlings': candlings,
    }
    return render(request, 'pages/ecommerce/hatchery/candling/list.html', context)

@login_required
def candling_detail(request, candlingcode):
    """
    View for a single Candling record with update functionality.
    """
    candling = get_object_or_404(Candling, candlingcode=candlingcode)

    if request.method == 'POST':
        # Update the candling instance with new data
        candling.incubation = Incubation.objects.get(id=request.POST.get('incubation'))
        candling.customer = Customer.objects.get(id=request.POST.get('customer'))
        candling.breeders = Breeders.objects.get(id=request.POST.get('breeders'))
        candling.eggs = int(request.POST.get('eggs'))
        candling.candled = request.POST.get('candled') == 'on'  # Convert checkbox to boolean
        candling.candled_date = request.POST.get('candled_date')
        candling.spoilt_eggs = int(request.POST.get('spoilt_eggs'))

        # Automatically calculate fertile eggs before saving
        candling.fertile_eggs = int(candling.eggs) - int(candling.spoilt_eggs)
        candling.save()
        return redirect('candling_detail', candlingcode=candling.candlingcode)  # Redirect to the updated detail view

    context = {
        'candling': candling,
        'incubations': Incubation.objects.all(),
        'customers': Customer.objects.all(),
        'breeders': Breeders.objects.all(),
    }
    return render(request, 'pages/ecommerce/hatchery/candling/details.html', context)

@login_required
def candling_create(request):
    """
    Create a new Candling record.
    """
    if request.method == 'POST':
        candling = Candling(
            incubation=Incubation.objects.get(id=request.POST.get('incubation')),
            customer=Customer.objects.get(id=request.POST.get('customer')),
            breeders=Breeders.objects.get(id=request.POST.get('breeders')),
            eggs=int(request.POST.get('eggs')),
            candled=request.POST.get('candled') == 'on',  # Convert checkbox to boolean
            candled_date=request.POST.get('candled_date'),
            spoilt_eggs=int(request.POST.get('spoilt_eggs')),
        )
        # Automatically calculate fertile eggs before saving
        candling.save()
        return redirect('candling_list')  # Redirect to the list view

    context = {
        'incubations': Incubation.objects.all(),
        'customers': Customer.objects.all(),
        'breeders': Breeders.objects.all(),
    }
    return render(request, 'pages/ecommerce/hatchery/candling/create.html', context)

@login_required
def candling_delete(request, candlingcode):
    """
    Delete a Candling record.
    """
    candling = get_object_or_404(Candling, candlingcode=candlingcode)

    if request.method == 'POST':
        candling.delete()
        return redirect('candling_list')  # Redirect to the list view

    context = {
        'candling': candling,
    }
    return render(request, 'pages/ecommerce/hatchery/candling/delete.html', context)


@login_required
def hatching_list(request):
    """
    List all Hatching records with pagination.
    """
    hatchings = Hatching.objects.all().order_by('-created')
    paginator = Paginator(hatchings, 10)
    page_number = request.GET.get('page')
    hatchings = paginator.get_page(page_number)
    
    context = {
        'hatchings': hatchings,
    }
    return render(request, 'pages/ecommerce/hatchery/hatching/list.html', context)

@login_required
def hatching_detail(request, hatchingcode):
    """
    View for a single Hatching record with update functionality.
    """
    hatching = get_object_or_404(Hatching, hatchingcode=hatchingcode)

    if request.method == 'POST':
        hatching.candling = Candling.objects.get(id=request.POST.get('candling'))
        hatching.customer = Customer.objects.get(id=request.POST.get('customer'))
        hatching.breeders = Breeders.objects.get(id=request.POST.get('breeders'))
        hatching.hatched = request.POST.get('hatched')
        hatching.deformed = request.POST.get('deformed')
        hatching.spoilt = request.POST.get('spoilt')
        hatching.notify_customer = request.POST.get('notify_customer') == 'on'

        hatching.chicks_hatched = hatching.hatched - hatching.deformed
        hatching.save()
        return redirect('hatching_detail', hatchingcode=hatching.hatchingcode)

    context = {
        'hatching': hatching,
        'candlings': Candling.objects.all(),
        'customers': Customer.objects.all(),
        'breeders': Breeders.objects.all(),
    }
    return render(request, 'pages/ecommerce/hatchery/hatching/details.html', context)

@login_required
def hatching_create(request):
    """
    Create a new Hatching record.
    """
    if request.method == 'POST':
        hatching = Hatching(
            candling=Candling.objects.get(id=request.POST.get('candling')),
            customer=Customer.objects.get(id=request.POST.get('customer')),
            breeders=Breeders.objects.get(id=request.POST.get('breeders')),
            hatched=int(request.POST.get('hatched')),
            deformed=int(request.POST.get('deformed')),
            spoilt=int(request.POST.get('spoilt')),
            notify_customer=request.POST.get('notify_customer') == 'on',
        )
        hatching.save()
        return redirect('hatching_list')

    context = {
        'candlings': Candling.objects.all(),
        'customers': Customer.objects.all(),
        'breeders': Breeders.objects.all(),
    }
    return render(request, 'pages/ecommerce/hatchery/hatching/create.html', context)

@login_required
def hatching_delete(request, hatchingcode):
    """
    Delete a Hatching record.
    """
    hatching = get_object_or_404(Hatching, hatchingcode=hatchingcode)

    if request.method == 'POST':
        hatching.delete()
        return redirect('hatching_list')

    context = {
        'hatching': hatching,
    }
    return render(request, 'pages/ecommerce/hatchery/hatching/delete.html', context)