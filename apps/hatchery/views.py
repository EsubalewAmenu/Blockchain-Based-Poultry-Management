from datetime import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.gis.geos import Point
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from weasyprint import HTML
from apps.accounts.validators import validate_email
from apps.breeders.models import *
from apps.chicks.models import Chicks
from apps.inventory.models import ItemType, Item
from apps.dashboard.models import Tracker
from .models import *

# Create your views here.
@login_required
def hatchery_list(request):
    hatcheries = Hatchery.objects.all()
    paginator = Paginator(hatcheries, 10)  # Show 10 hatcheries per page
    
    page_number = request.GET.get('page')
    hatcheries = paginator.get_page(page_number)
    return render(request, 'pages/poultry/hatchery/list.html', {'hatcheries': hatcheries})

@login_required
def hatchery_detail(request, name):
    hatchery = Hatchery.objects.get(name=name)
    if request.method == 'POST':
        # Update hatchery instance with the new data from the request
        hatchery.name = request.POST.get('name', hatchery.name)
        hatchery.email = request.POST.get('email', hatchery.email)
        hatchery.phone = request.POST.get('phone', hatchery.phone).replace(' ', '')
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
        allowed_image_types = ['image/jpeg', 'image/png']

        if request.FILES.get('photo'):
            if request.FILES.get('photo').content_type not in allowed_image_types:
                messages.error(request, "Invalid image format for front photo. Only JPEG or PNG is allowed.", extra_tags='danger')
                return redirect('hatchery_update', name=name)
        # Handle file upload
        if request.FILES.get('photo'):
            hatchery.photo = request.FILES['photo']

        # Save the updated hatchery instance
        hatchery.save()
        return redirect('hatchery_update', name=name)
    return render(request, 'pages/poultry/hatchery/details.html', {'hatchery': hatchery})

@login_required
def hatchery_update(request, name):
    hatchery = Hatchery.objects.get(name=name)
    if request.method == 'POST':
        # Update hatchery instance with the new data from the request
        hatchery.name = request.POST.get('name', hatchery.name)
        hatchery.email = request.POST.get('email', hatchery.email)
        hatchery.phone = request.POST.get('phone', hatchery.phone).replace(' ', '')
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
        allowed_image_types = ['image/jpeg', 'image/png']
        if request.FILES.get('photo'):
            if request.FILES.get('photo').content_type not in allowed_image_types:
                messages.error(request, "Invalid image format for front photo. Only JPEG or PNG is allowed.", extra_tags='danger')
                return redirect('hatchery_update', name=name)
        # Handle file upload
        if request.FILES.get('photo'):
            hatchery.photo = request.FILES['photo']

        # Save the updated hatchery instance
        hatchery.save()
        return redirect('hatchery_list')
    return render(request, 'pages/poultry/hatchery/details.html', {'hatchery': hatchery})

@login_required
def hatcher_create(request):
    if request.method == 'POST':
        name = request.POST['name']
        photo = request.FILES['photo']
        email = request.POST['email']
        phone = request.POST.get('phone').replace(' ', '')
        address = request.POST['address']
        latitude_str = request.POST.get('latitude', None)
        longitude_str = request.POST.get('longitude', None)
        allowed_image_types = ['image/jpeg', 'image/png']
        if Hatchery.objects.filter(email=email).exists():
            messages.error(request, "This email address is already registered.", extra_tags="danger")
            return redirect('hatchery_create')
        if email:
            if not validate_email(email):
                messages.error(request, "This email address does not exist.", extra_tags="danger")
                return redirect('hatchery_create')
        
            
        if request.FILES.get('photo'):
            if request.FILES.get('photo').content_type not in allowed_image_types:
                messages.error(request, "Invalid image format for front photo. Only JPEG or PNG is allowed.", extra_tags='danger')
                return redirect('hatchery_create')
        latitude = None
        longitude = None

        if latitude_str:
            try:
                latitude = float(latitude_str)
            except ValueError:
                
                latitude = None

        
        if longitude_str:
            try:
                longitude = float(longitude_str)
            except ValueError:
                longitude = None

        if latitude is not None and longitude is not None:
            location = Point(longitude, latitude, srid=4326)
        else:
            location = None
        totalcapacity = request.POST['totalcapacity']

        hatchery = Hatchery(name=name, photo=photo, email=email, phone=phone, address=address, location=location, latitude=latitude, longitude=longitude, totalcapacity=totalcapacity)
        hatchery.save()
        return redirect('hatchery_list')
    else:
        return render(request, 'pages/poultry/hatchery/create.html')

@login_required
def hatchery_delete(request, name):
    hatchery = get_object_or_404(Hatchery, name=name)
    
    if request.method == 'POST':
        hatchery.delete()
        messages.success(request, 'Hatchery deleted successfully.')
        return redirect('hatchery_list')  # Redirect to the hatchery list view after deletion
    
    messages.error(request, 'Invalid request method.')
    return redirect('hatchery_list')
  
@login_required  
def incubator_list(request):
    incubators = Incubators.objects.all().select_related('hatchery') 
    paginator = Paginator(incubators, 10)
    
    page_number = request.GET.get('page')
    incubators = paginator.get_page(page_number)
    return render(request, 'pages/poultry/incubators/list.html', {'incubators': incubators})
    
@login_required
def incubator_create(request):
    hatcheries = Hatchery.objects.all()
    items =Item.objects.filter(item_type__type_name='Incubator')
    item_data = None
    if 'item_data' in request.session:
        item_data = request.session['item_data']
    if request.method == 'POST':
        hatchery = Hatchery.objects.get(id=request.POST['hatchery'])
        incubatortype = request.POST['incubatortype']
        manufacturer = request.POST['manufacturer']
        model = request.POST['model']
        year = request.POST['year']
        item_id = request.POST['item']
        
        item = Item.objects.get(pk=item_id)
        if 'item_data' in request.session:
            item_data = request.session['item_data']
        incubator = Incubators(
            hatchery=hatchery,
            incubatortype=incubatortype,
            manufacturer=manufacturer,
            model=model,
            year=year,
            item=item
        )
        incubator.save()
        item.quantity = 1
        item.save()
        messages.success(request, "Incubator created successfully", extra_tags='success')
        request.session.pop('item_data')
        return redirect('incubator_list')
    
    return render(request, 'pages/poultry/incubators/create.html', {'hatcheries': hatcheries, 'items':items, 'item_data':item_data})

@login_required
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
    
    return render(request, 'pages/poultry/incubators/details.html', {'incubator': incubator})

@login_required
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
    return render(request, 'pages/poultry/incubators/details.html', {'incubator': incubator})

@login_required
def incubator_delete(request, code):
    incubator = get_object_or_404(Incubators, code=code)
    
    if request.method == 'POST':
        incubator.delete()
        incubator.item.delete()
        messages.success(request, 'Incubator deleted successfully.')
        return redirect('incubator_list')
    
    return redirect('incubator_list')

@login_required
def incubator_capacity_list(request):
    capacity_list = IncubatorCapacity.objects.all()
    paginator = Paginator(capacity_list, 10)  # Show 10 breeders per page
    
    page_number = request.GET.get('page')
    capacity_list = paginator.get_page(page_number)
    return render(request, 'pages/poultry/incubators/incubator_capacity/list.html', {'capacity_list': capacity_list})

@login_required
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
    
    return render(request, 'pages/poultry/incubators/incubator_capacity/create.html', {'incubators': incubators})

@login_required
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
    
    return render(request, 'pages/poultry/incubators/incubator_capacity/details.html', {
        'capacity': capacity,
        'incubators': incubators
    })
    
@login_required
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
    
    return render(request, 'pages/poultry/incubators/incubator_capacity/details.html', {
        'capacity': capacity,
        'incubators': incubators
    })
    
@login_required
def incubator_capacity_delete(request, id):
    incubator_capacity = get_object_or_404(IncubatorCapacity, id=id)
    
    if request.method == 'POST':
        incubator_capacity.delete()
        messages.success(request, 'Incubator capacity deleted successfully.')
        return redirect('incubator_capacity_list')
    
    return redirect('incubator_capacity_list')

#Egg Settings
@login_required
def egg_setting_list(request):
    egg_settings = EggSetting.objects.all()
    egg= Eggs.objects.all()
    paginator = Paginator(egg_settings, 10)
    
    page_number = request.GET.get('page')
    egg_settings = paginator.get_page(page_number)
    return render(request, 'pages/poultry/hatchery/egg_setting/list.html', {'egg_settings': egg_settings, 'egg':egg})

@login_required
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
    return render(request, 'pages/poultry/hatchery/egg_setting/details.html', {
        'egg_setting': egg_setting,
        'incubators': incubators,
        'customers': customers,
        'breeders': breeders
    })

@login_required
def egg_setting_create(request):
    
    if request.method == 'POST':
        incubator_id = request.POST.get('incubator')
        breeders_id = request.POST.get('breeders')
        item_request_item_id = request.POST.get('item_request_item')
        item_request_quantity = request.POST.get('item_request_quantity')
        item_request_item = get_object_or_404(Item, id=item_request_item_id)
        
        egg = Eggs.objects.filter(item=item_request_item).first()
        if int(item_request_quantity)>egg.received:
            messages.error(request, 'Not enough eggs available in the selected egg type.', extra_tags='danger')
            return redirect('egg_setting_create')

        incubator = get_object_or_404(Incubators, pk=incubator_id)
        breeders = get_object_or_404(Breeders, pk=breeders_id)
        
        item_request = ItemRequest(item=item_request_item, quantity=item_request_quantity, requested_by=request.user)
        item_request.save()

        egg_setting = EggSetting(
            incubator=incubator,
            breeders=breeders,
            item_request = item_request,
            egg = egg,
            eggs = item_request_quantity,
        )
        egg_setting.save()
        messages.success(request, 'Egg Setting set successfully.', extra_tags='success')
        return redirect('egg_setting_list')

    incubators = Incubators.objects.all()
    customers = Customer.objects.all()
    breeders = Breeders.objects.all()
    eggs = Eggs.objects.all()
    items = Item.objects.filter(item_type__type_name="Egg")

    # Get all eggs that are not in the egg_settings
    
    
    
    return render(request, 'pages/poultry/hatchery/egg_setting/create.html', {
        'incubators': incubators,
        'customers': customers,
        'breeders': breeders,
        'egg':eggs,
        'items': items,
    })

@login_required
def egg_setting_update(request, settingcode):
    egg_setting = get_object_or_404(EggSetting, settingcode=settingcode)

    if request.method == 'POST':
        if egg_setting.approved:
            messages.error(request, "Egg setting is approved can't be updated.", extra_tags="danger")
            return redirect('egg_setting_detail', settingcode=egg_setting.settingcode)
        
        egg_setting.settingcode = request.POST.get('settingcode', egg_setting.settingcode)
        egg_setting.incubator = get_object_or_404(Incubators, id=request.POST.get('incubator'))
        egg_setting.customer = get_object_or_404(Customer, id=request.POST.get('customer'))
        egg_setting.breeders = get_object_or_404(Breeders, id=request.POST.get('breeders'))
        egg_setting.eggs = request.POST.get('eggs', egg_setting.eggs)
        
        if egg_setting.eggs > egg_setting.item_request.quantity:
            egg_setting.item_request.quantity = egg_setting.eggs
            egg_setting.item_request.save()
        egg_setting.save()
        messages.success(request, "Egg setting updated successfully", extra_tags="success")
        return redirect('egg_setting_detail', settingcode=egg_setting.settingcode)

    incubators = Incubators.objects.all()
    customers = Customer.objects.all()
    breeders = Breeders.objects.all()
    return render(request, 'pages/poultry/hatchery/egg_setting/details.html', {
        'egg_setting': egg_setting,
        'incubators': incubators,
        'customers': customers,
        'breeders': breeders
    })

@login_required
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
    return render(request, 'pages/poultry/hatchery/incubation/list.html', context)

## Detail View    
@login_required
def incubation_detail(request, incubationcode):
    incubation = get_object_or_404(Incubation, incubationcode=incubationcode)

    if request.method == 'POST':
        # Update the incubation instance with new data
        incubation.eggsetting = EggSetting.objects.get(id=request.POST.get('eggsetting'))
        # incubation.customer = Customer.objects.get(id=request.POST.get('customer'))
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
    return render(request, 'pages/poultry/hatchery/incubation/details.html', context)

## Create View
@login_required
def incubation_create(request):
    if request.method == 'POST':
        eggsetting_id = request.POST.get('eggsetting')
        eggs = request.POST.get('eggs')
        eggsetting=EggSetting.objects.get(id=eggsetting_id)
        incubation = Incubation(
            eggsetting=eggsetting,
            breeders=eggsetting.breeders,
            eggs=eggs
        )
        
        if int(eggs) > int(eggsetting.eggs):
            messages.error(request, 'Not enough eggs available in the selected egg setting.', extra_tags='danger')
            return redirect('incubation_create')
        incubation.save()
        return redirect('incubation_list')

    egg_settings = EggSetting.objects.filter(is_approved=True)
    customers = Customer.objects.all()
    breeders = Breeders.objects.all()

    context = {
        'egg_settings': egg_settings,
        'customers': customers,
        'breeders': breeders,
    }

    return render(request, 'pages/poultry/hatchery/incubation/create.html', context)

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
    return render(request, 'pages/poultry/hatchery/incubation/details.html', context)

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
    return render(request, 'pages/poultry/hatchery/candling/list.html', context)

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
    return render(request, 'pages/poultry/hatchery/candling/details.html', context)

@login_required
def candling_create(request):
    """
    Create a new Candling record.
    """
    
    if request.method == 'POST':
        incubation=Incubation.objects.get(id=request.POST.get('incubation'))
        candled_date=request.POST.get('candled_date')
        if candled_date in ['', ""]:
            candled_date = datetime.datetime.now().date()
        candling = Candling(
            incubation=incubation,
            customer=incubation.customer,
            breeders=incubation.breeders,
            eggs=incubation.eggs,
            candled=request.POST.get('candled') == 'on',  # Convert checkbox to boolean
            candled_date=candled_date,
            spoilt_eggs=int(request.POST.get('spoilt_eggs')),
        )
        # Automatically calculate fertile eggs before saving
        candling.save()
        egg=Eggs.objects.get(id=incubation.eggsetting.egg.id)
        return redirect('candling_list') 

    context = {
        'incubations': Incubation.objects.filter(eggsetting__is_approved=True),
        'customers': Customer.objects.all(),
        'breeders': Breeders.objects.all(),
    }
    return render(request, 'pages/poultry/hatchery/candling/create.html', context)

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
    return render(request, 'pages/poultry/hatchery/candling/delete.html', context)


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
    return render(request, 'pages/poultry/hatchery/hatching/list.html', context)

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
    return render(request, 'pages/poultry/hatchery/hatching/details.html', context)

@login_required
def hatching_create(request):
    """
    Create a new Hatching record.
    """
    if request.method == 'POST':
        candling=Candling.objects.get(id=request.POST.get('candling'))
        
        # hatched = int(request.POST.get('hatched'))
        deformed = int(request.POST.get('deformed'))
        spoilt = int(request.POST.get('spoilt'))

        total_count = candling.fertile_eggs + deformed + spoilt
        if total_count > candling.eggs:
            messages.error(request, 'Hatched, deformed, or spoilt cannot exceed the total eggs.')
            return redirect('hatching_create')
        
        hatching = Hatching(
            candling=candling,
            customer=None,
            breeders=candling.breeders,
            hatched=candling.fertile_eggs,
            deformed=deformed,
            spoilt=spoilt,
        )
        
        hatching.save()
        item_type = ItemType.objects.get_or_create(type_name="Chicks")
        item = Item(item_type=item_type[0])
        item.quantity = int(hatching.chicks_hatched)
        item.save()
        from datetime import datetime
        chick = Chicks(item=item, source='hatching', breed=hatching.breeders.breed, age=datetime.now().date(), hatching=hatching, number=hatching.chicks_hatched)
        chick.save()
        return redirect('hatching_list')

    context = {
        'candlings': Candling.objects.all(),
        'customers': Customer.objects.all(),
        'breeders': Breeders.objects.all(),
    }
    return render(request, 'pages/poultry/hatchery/hatching/create.html', context)

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
    return render(request, 'pages/poultry/hatchery/hatching/delete.html', context)
@login_required
def egg_tracker_list(request):
    eggs=Eggs.objects.all()

    return render(request, 'pages/poultry/tracker_list.html', {
        'eggs': eggs
    })

@login_required
def tracker_list_view(request):
    tracker_type = request.GET.get('type', 'egg')  # Default to 'egg'
    
    egg_trackers = []
    chick_trackers = []

    if tracker_type == 'egg':
        egg_trackers = Tracker.objects.filter(egg__isnull=False).select_related('egg').all()
    elif tracker_type == 'chick':
        chick_trackers = Tracker.objects.filter(chick__isnull=False).select_related('chick').all()

    return render(request, 'pages/poultry/tracker-list.html', {
        'egg_trackers': egg_trackers,
        'chick_trackers': chick_trackers,
        'tracker_type': tracker_type,
    })

    
@login_required
def tracker_details_view(request, tracker_code):
    tracker = get_object_or_404(Tracker, tracker_code=tracker_code)
    tracker_type = 'egg' if tracker.egg else 'chick'
    egg_setting_id = request.GET.get('egg_setting_id')  # Capture the egg setting ID from the query param
    incubation_id = request.GET.get('incubation_id')  # Capture the incubation ID from the query param

    if tracker_type == 'egg':
        egg = tracker.egg
        egg_settings = EggSetting.objects.filter(egg=egg)  # Get all egg settings for this egg
        egg_setting = egg_settings.filter(id=egg_setting_id).first() if egg_setting_id else egg_settings.first()
        incubations = Incubation.objects.filter(eggsetting=egg_setting) if egg_setting else None
        incubation = incubations.filter(id=incubation_id).first() if incubation_id else incubations.first() if incubations else None
        candling = Candling.objects.filter(incubation=incubation).first() if incubation else None
        hatching = Hatching.objects.filter(candling=candling).first() if candling else None
        chicks = Chicks.objects.filter(hatching=hatching) if hatching else []

        return render(request, 'pages/poultry/tracker-details.html', {
            'tracker_type': 'egg',
            'egg': egg,
            'tracker': tracker,
            'egg_setting': egg_setting,
            'egg_settings': egg_settings,  # Pass all egg settings for dropdown in the template
            'incubations': incubations,  # Pass all incubations for dropdown in the template
            'incubation': incubation,
            'candling': candling,
            'hatching': hatching,
            'chicks': chicks,
        })

    elif tracker_type == 'chick':
        chick = tracker.chick
        egg = Eggs.objects.filter(chicks=chick.batchnumber).first()  # Get the associated egg for the chick
        egg_settings = EggSetting.objects.filter(egg=egg)  # Get all egg settings for the associated egg
        egg_setting = egg_settings.filter(id=egg_setting_id).first() if egg_setting_id else egg_settings.first()
        incubations = Incubation.objects.filter(eggsetting=egg_setting) if egg_setting else None
        incubation = incubations.filter(id=incubation_id).first() if incubation_id else incubations.first() if incubations else None
        candling = Candling.objects.filter(incubation=incubation).first() if incubation else None
        hatching = Hatching.objects.filter(candling=candling).first() if candling else None
        chicks = Chicks.objects.filter(hatching=hatching) if hatching else []

        return render(request, 'pages/poultry/tracker-details.html', {
            'tracker_type': 'chick',
            'chick': chick,
            'tracker': tracker,
            'egg': egg,
            'egg_setting': egg_setting,
            'egg_settings': egg_settings,  # Pass all egg settings for dropdown in the template
            'incubations': incubations,  # Pass all incubations for dropdown in the template
            'incubation': incubation,
            'candling': candling,
            'hatching': hatching,
            'chicks': chicks,
        })


        
def tracker_public_view(request, tracker_code):
    tracker = get_object_or_404(Tracker, tracker_code=tracker_code)
    tracker_type = 'egg' if tracker.egg else 'chick'
    egg_setting_id = request.GET.get('egg_setting_id')  # Capture the egg setting ID from the query param
    incubation_id = request.GET.get('incubation_id')  # Capture the incubation ID from the query param

    if tracker_type == 'egg':
        egg = tracker.egg
        egg_settings = EggSetting.objects.filter(egg=egg)  # Get all egg settings for this egg
        egg_setting = egg_settings.filter(id=egg_setting_id).first() if egg_setting_id else egg_settings.first()
        incubations = Incubation.objects.filter(eggsetting=egg_setting) if egg_setting else None
        incubation = incubations.filter(id=incubation_id).first() if incubation_id else incubations.first() if incubations else None
        candling = Candling.objects.filter(incubation=incubation).first() if incubation else None
        hatching = Hatching.objects.filter(candling=candling).first() if candling else None
        chicks = Chicks.objects.filter(hatching=hatching) if hatching else []

        return render(request, 'pages/poultry/tracker-details-public.html', {
            'tracker_type': 'egg',
            'egg': egg,
            'tracker': tracker,
            'egg_setting': egg_setting,
            'egg_settings': egg_settings,
            'incubations': incubations, 
            'incubation': incubation,
            'candling': candling,
            'hatching': hatching,
            'chicks': chicks,
        })

    elif tracker_type == 'chick':
        chick = tracker.chick
        egg = Eggs.objects.filter(chicks=chick.batchnumber).first()
        egg_settings = EggSetting.objects.filter(egg=egg) 
        egg_setting = egg_settings.filter(id=egg_setting_id).first() if egg_setting_id else egg_settings.first()
        incubations = Incubation.objects.filter(eggsetting=egg_setting) if egg_setting else None
        incubation = incubations.filter(id=incubation_id).first() if incubation_id else incubations.first() if incubations else None
        candling = Candling.objects.filter(incubation=incubation).first() if incubation else None
        hatching = Hatching.objects.filter(candling=candling).first() if candling else None
        chicks = Chicks.objects.filter(hatching=hatching) if hatching else []

        return render(request, 'pages/poultry/tracker-details-public.html', {
            'tracker_type': 'chick',
            'chick': chick,
            'tracker': tracker,
            'egg': egg,
            'egg_setting': egg_setting,
            'egg_settings': egg_settings,
            'incubations': incubations,
            'incubation': incubation,
            'candling': candling,
            'hatching': hatching,
            'chicks': chicks,
        })


def tracker_barcode_image_view(request, tracker_code):
    tracker = get_object_or_404(Tracker, tracker_code=tracker_code)

    if tracker.barcode_image:
        with open(tracker.barcode_image.path, 'rb') as f:
            return HttpResponse(f.read(), content_type='image/png')
    else:
        raise Http404("Barcode image not found.")
    
def tracker_qrcode_image_view(request, tracker_code):
    tracker = get_object_or_404(Tracker, tracker_code=tracker_code)

    if tracker.qr_code_image:
        with open(tracker.qr_code_image.path, 'rb') as f:
            return HttpResponse(f.read(), content_type='image/png')
    else:
        raise Http404("Qrcode image not found.")
