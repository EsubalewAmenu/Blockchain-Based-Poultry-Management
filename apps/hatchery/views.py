from datetime import datetime, timezone
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
    errors = {}
    if request.method == 'POST':
        hatchery.name = request.POST.get('name', hatchery.name)
        hatchery.email = request.POST.get('email', hatchery.email)
        hatchery.phone = request.POST.get('phone', hatchery.phone).replace(' ', '')
        hatchery.address = request.POST.get('address', hatchery.address)
        hatchery.totalcapacity = request.POST.get('totalcapacity', hatchery.totalcapacity)
        allowed_image_types = ['image/jpeg', 'image/png']

        if request.POST.get('email'):
            if not validate_email(request.POST.get('email')):
                errors['email'] = "This email address is not valid."
                
            elif Hatchery.objects.filter(email=request.POST.get('email')).exists():
                errors['email'] = "This Email Address already exists"
        
        if hatchery.email:
            if not validate_email(hatchery.email):
               errors['email'] = "This email address is not valid."
                       
        if request.POST.get('totalcapacity') and int(request.POST.get('totalcapacity')) < 0:
            errors['total_capacity'] = "Total capacity cannot less than zero."
                
        if request.FILES.get('photo'):
            if request.FILES.get('photo').content_type not in allowed_image_types:
                errors['photo'] = "Invalid image format for front photo. Only JPEG or PNG is allowed."
        
        if errors:
            messages.error(request, "Updating hatchery failed: Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/hatchery/details.html', {'hatchery': hatchery, 'errors': errors})
        
        if request.FILES.get('photo'):
            hatchery.photo = request.FILES['photo']
        try:
            hatchery.save()
        except Exception as e:
            messages.error(request, f'Error updating hatchery: {str(e)}', extra_tags='danger')
        return redirect('hatchery_update', name=name)
    return render(request, 'pages/poultry/hatchery/details.html', {'hatchery': hatchery})

@login_required
def hatchery_update(request, name):
    hatchery = Hatchery.objects.get(name=name)
    errors = {}
    if request.method == 'POST':
        hatchery.name = request.POST.get('name', hatchery.name)
        hatchery.email = request.POST.get('email', hatchery.email)
        hatchery.phone = request.POST.get('phone', hatchery.phone).replace(' ', '')
        hatchery.address = request.POST.get('address', hatchery.address)
        hatchery.totalcapacity = request.POST.get('totalcapacity', hatchery.totalcapacity)
        allowed_image_types = ['image/jpeg', 'image/png']

        if request.POST.get('email'):
            if not validate_email(request.POST.get('email')):
                errors['email'] = "This email address is not valid."
                
            elif Hatchery.objects.filter(email=request.POST.get('email')).exists():
                errors['email'] = "This Email Address already exists"
        
        if hatchery.email:
            if not validate_email(hatchery.email):
               errors['email'] = "This email address is not valid."
                       
        if request.POST.get('totalcapacity') and int(request.POST.get('totalcapacity')) < 0:
            errors['total_capacity'] = "Total capacity cannot less than zero."
                
        if request.FILES.get('photo'):
            if request.FILES.get('photo').content_type not in allowed_image_types:
                errors['photo'] = "Invalid image format for front photo. Only JPEG or PNG is allowed."
        
        if errors:
            messages.error(request, "Updating hatchery failed: Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/hatchery/details.html', {'hatchery': hatchery, 'errors': errors})
        
        if request.FILES.get('photo'):
            hatchery.photo = request.FILES['photo']
        try:
            hatchery.save()
        except Exception as e:
            messages.error(request, f'Error updating hatchery: {str(e)}', extra_tags='danger')
        return redirect('hatchery_update', name=name)
    return render(request, 'pages/poultry/hatchery/details.html', {'hatchery': hatchery})

@login_required
def hatcher_create(request):
    errors = {}
    if request.method == 'POST':
        name = request.POST['name']
        photo = request.FILES.get('photo', None)
        email = request.POST['email']
        phone = request.POST.get('phone').replace(' ', '')
        totalcapacity = request.POST['totalcapacity']
        address = request.POST['address']
        allowed_image_types = ['image/jpeg', 'image/png']
        required_fields = ['email', 'phone', 'name', 'total_capacity']
        
        for field in required_fields:
            if not request.POST.get(field):
                errors[field] = "* This field is required"
        
        if Hatchery.objects.filter(name=name).exists():
            errors['name'] = f"Hatchery with name '{name}' already exists."
        
        if Hatchery.objects.filter(email=email).exists():
            errors['email'] = f"Hatcher with email '{email}' already exists"
            
        if email:
            if not validate_email(email):
                errors['email'] = f"Email '{email}' is not valid"
                
        
        if totalcapacity and int(totalcapacity) < 0:
            errors['totalcapacity'] = f"Total capacity should be a valid number"
                
        if request.FILES.get('photo'):
            if request.FILES.get('photo').content_type not in allowed_image_types:
                errors['photo'] = "Invalid image format for front photo. Only JPEG or PNG is allowed."
                
        if errors:
            messages.error(request, "Error creating hatchery, Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/hatchery/create.html', {'errors': errors})
                
        try:
            hatchery = Hatchery(name=name, photo=photo, email=email, phone=phone, address=address, totalcapacity=totalcapacity)
            hatchery.save()
            messages.success(request, "Hatchery Created Successfully", extra_tags='success')
        except Exception as e:
            messages.error(request, f"Error creating hatchery: {str(e)}", extra_tags='danger')
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
        if 'item_data' in request.session:
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
    errors={}
    if request.method == 'POST':
        if egg_setting.is_approved:
            messages.success(request, "Egg Setting request is already approved ", extra_tags='danger')
            return redirect('egg_setting_detail', settingcode=egg_setting.settingcode)
        egg_setting.settingcode = request.POST.get('settingcode', egg_setting.settingcode)
        egg_setting.incubator = get_object_or_404(Incubators, id=request.POST.get('incubator'))
        egg_setting.breeders = get_object_or_404(Breeders, id=request.POST.get('breeders'))
        if request.POST.get('eggs'):
            if egg_setting.eggs == int(request.POST.get('eggs')):
                pass
            elif egg_setting.item_request.item.quantity < int(request.POST.get('eggs')):
                errors['eggs'] = "Insufficient quantity of eggs available for the slected egg type."
                
            egg_setting.eggs = int(request.POST.get('eggs'))
            egg_setting.item_request.quantity = int(request.POST.get('eggs'))
            egg_setting.item_request.save()
        else:
            egg_setting.eggs = egg_setting.eggs
            
        if errors:
            messages.error(request, "Updating egg setting failed: Please double-check your entries and try again.", extra_tags="danger")
            return render(request, 'pages/poultry/hatchery/egg_setting/details.html', {
                'egg_setting': egg_setting,
                'errors': errors,
                'incubators': Incubators.objects.all(),
                'customers': Customer.objects.all(),
                'breeders': Breeders.objects.all()
            })
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
    errors = {}
    if request.method == 'POST':
        incubator_id = request.POST.get('incubator')
        breeders_id = request.POST.get('breeders')
        item_request_item_id = request.POST.get('item_request_item')
        item_request_quantity = request.POST.get('item_request_quantity')
        
        required_fields = ['incubator', 'breeders', 'item_request_item', 'item_request_quantity']
        for field in required_fields:
            if not request.POST.get(field):
                errors[field] = "* This Field is required"
                
        if item_request_item_id:
            item_request_item = get_object_or_404(Item, id=item_request_item_id)
            egg = Eggs.objects.filter(item=item_request_item).first()
        
            if item_request_quantity and int(item_request_quantity)> egg.received:
                errors['item_request_quantity'] = "Insufficient quantity of eggs available for the slected egg type."
         
        if incubator_id:
            incubator = get_object_or_404(Incubators, pk=incubator_id)

        if breeders_id:    
            breeders = get_object_or_404(Breeders, pk=breeders_id)
            
        if errors:
            messages.error(request, "Error creating egg setting, Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/hatchery/egg_setting/create.html', {
                'errors': errors,
                'incubators': Incubators.objects.all(),
                'customers': Customer.objects.all(),
                'breeders': Breeders.objects.all(),
                'egg': Eggs.objects.all(),
                'items': Item.objects.filter(item_type__type_name="Egg"),
            })
        
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
    errors={}
    if request.method == 'POST':
        if egg_setting.is_approved:
            messages.success(request, "Egg Setting request is already approved ", extra_tags='danger')
            return redirect('egg_setting_detail', settingcode=egg_setting.settingcode)
        egg_setting.settingcode = request.POST.get('settingcode', egg_setting.settingcode)
        egg_setting.incubator = get_object_or_404(Incubators, id=request.POST.get('incubator'))
        egg_setting.breeders = get_object_or_404(Breeders, id=request.POST.get('breeders'))
        if request.POST.get('eggs'):
            if egg_setting.eggs == int(request.POST.get('eggs')):
                pass
            elif egg_setting.item_request.item.quantity < int(request.POST.get('eggs')):
                errors['eggs'] = "Insufficient quantity of eggs available for the slected egg type."
                
            egg_setting.eggs = int(request.POST.get('eggs'))
            egg_setting.item_request.quantity = int(request.POST.get('eggs'))
            egg_setting.item_request.save()
        else:
            egg_setting.eggs = egg_setting.eggs
            
        if errors:
            messages.error(request, "Updating egg setting failed: Please double-check your entries and try again.")
            return render(request, 'pages/poultry/hatchery/egg_setting/details.html', {
                'egg_setting': egg_setting,
                'errors': errors,
                'incubators': Incubators.objects.all(),
                'customers': Customer.objects.all(),
                'breeders': Breeders.objects.all()
            })
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
def egg_setting_delete(request, settingcode):
    egg_setting = get_object_or_404(EggSetting, settingcode=settingcode)
    if request.method == 'POST':
        if Incubation.objects.filter(eggsetting=egg_setting.id).exists():
            messages.error(request, "Cannot delete Incubation associated with existing Egg Setting.", extra_tags='danger')
            return redirect('egg_setting_list')
        egg_setting.delete()
        messages.success(request, 'Egg Setting deleted successfully.', extra_tags='success')
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
    errors = {}
    if request.method == 'POST':
        incubation.eggsetting = EggSetting.objects.get(id=request.POST.get('eggsetting'))
        incubation.breeders = Breeders.objects.get(id=request.POST.get('breeders'))
        incubation.eggs = request.POST.get('eggs')
        
        if request.POST.get('eggs') and int(request.POST.get('eggs')) > incubation.eggsetting.eggs:
            errors['eggs'] = "Insufficient quantity of eggs available for the slected egg setting."
            
        if errors:
            messages.error(request, "Updating incubation failed: Please double-check your entries and try again.")
            return render(request, 'pages/poultry/hatchery/incubation/details.html', {
                'incubation': incubation,
                'errors': errors,
                'egg_settings': EggSetting.objects.all(),
                'customers': Customer.objects.all(),
                'breeders': Breeders.objects.all()
            })
        
        incubation.save()
        messages.success(request, "Incubation updated successfully.", extra_tags='success')
        return redirect(incubation.get_absolute_url())

    context = {
        'incubation': incubation,
        'egg_settings': EggSetting.objects.all(),
        'customers': Customer.objects.all(),
        'breeders': Breeders.objects.all(),
    }
    return render(request, 'pages/poultry/hatchery/incubation/details.html', context)

## Create View
@login_required
def incubation_create(request):
    errors = {}
    egg_settings = EggSetting.objects.filter(is_approved=True)
    customers = Customer.objects.all()
    breeders = Breeders.objects.all()
    if request.method == 'POST':
        eggsetting_id = request.POST.get('eggsetting')
        eggs = request.POST.get('eggs')
        
        
        required_fields = ['eggsetting', 'eggs']
        for field in required_fields:
            if not request.POST.get(field):
                errors[field] = '* This field is required.'
                
        if eggsetting_id:
            eggsetting=EggSetting.objects.get(id=eggsetting_id) 
            if eggs and int(eggs) > int(eggsetting.eggs):
                errors['eggs'] = "Insufficient quantity of eggs available for the slected egg setting."
        
        context = {
            'egg_settings': egg_settings,
            'customers': customers,
            'breeders': breeders,
            'errors':errors
        }    
        if errors:
            messages.error(request, "Creating incubation failed: Please double-check your entries and try again.")
            return render(request, 'pages/poultry/hatchery/incubation/create.html', context)
        
        eggsetting=EggSetting.objects.get(id=eggsetting_id)   
        incubation = Incubation(
            eggsetting=eggsetting,
            breeders=eggsetting.breeders,
            eggs=eggs
        )
        incubation.save()
        messages.success(request, "Incubation saved successfully", extra_tags='success')
        return redirect('incubation_list')

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
    errors = {}
    if request.method == 'POST':
        incubation.eggsetting = EggSetting.objects.get(id=request.POST.get('eggsetting'))
        incubation.breeders = Breeders.objects.get(id=request.POST.get('breeders'))
        incubation.eggs = request.POST.get('eggs')
        
        if request.POST.get('eggs') and int(request.POST.get('eggs')) > incubation.eggsetting.eggs:
            errors['eggs'] = "Insufficient quantity of eggs available for the slected egg setting."
            
        if errors:
            messages.error(request, "Updating incubation failed: Please double-check your entries and try again.")
            return render(request, 'pages/poultry/hatchery/incubation/details.html', {
                'incubation': incubation,
                'errors': errors,
                'egg_settings': EggSetting.objects.all(),
                'customers': Customer.objects.all(),
                'breeders': Breeders.objects.all()
            })
        
        incubation.save()
        messages.success(request, "Incubation updated successfully.", extra_tags='success')
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
        if Candling.objects.filter(incubation=incubation.id).exists():
            messages.error(request, "Cannot delete incubation with existing candling records.")
            return redirect(incubation.get_absolute_url())
        incubation.delete()
        messages.success(request, "Incubation deleted successfully.", extra_tags='success')
        return redirect('incubation_list')

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
    errors = {}

    if request.method == 'POST':
        # Retrieve and validate input data
        incubation_id = request.POST.get('incubation')
        breeders_id = request.POST.get('breeders')
        eggs = request.POST.get('eggs')
        candled = request.POST.get('candled') == 'on'
        candled_date = request.POST.get('candled_date')
        spoilt_eggs = request.POST.get('spoilt_eggs')

        try:
            # Validate and assign values
            candling.incubation = get_object_or_404(Incubation, id=incubation_id)
            candling.breeders = get_object_or_404(Breeders, id=breeders_id)
            candling.eggs = int(eggs)
            candling.candled = candled
            candling.candled_date = datetime.datetime.strptime(candled_date, '%Y-%m-%d').date()
            candling.spoilt_eggs = int(spoilt_eggs)

            # Check if spoilt_eggs is not greater than the total eggs
            if int(spoilt_eggs) > candling.incubation.eggs:
                errors['spoilt_eggs'] = "Spoilt eggs quantity cannot exceed the available eggs in the selected incubation."
                
            if candled_date and datetime.datetime.strptime(candled_date, "%Y-%m-%d").date() > datetime.datetime.now().date():
                errors['candled_date'] = "Candled date cannot be in the future."

        except ValueError:
            errors['eggs'] = "Please enter valid numbers for eggs and spoilt eggs."
        except Incubation.DoesNotExist:
            errors['incubation'] = "Selected incubation does not exist."
        except Breeders.DoesNotExist:
            errors['breeders'] = "Selected breeders do not exist."

        if errors:
            messages.error(request, "Updating candling failed: Please double-check your entries and try again.", extra_tags="danger")
            return render(request, 'pages/poultry/hatchery/candling/details.html', {
                'candling': candling,
                'errors': errors,
                'incubations': Incubation.objects.all(),
                'customers': Customer.objects.all(),
                'breeders': Breeders.objects.all()
            })
            
        # Automatically calculate fertile eggs before saving
        candling.fertile_eggs = candling.eggs - candling.spoilt_eggs
        candling.save()

        messages.success(request, 'Candling record updated successfully.', extra_tags="success")
        return redirect('candling_detail', candlingcode=candling.candlingcode)

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
    errors={}
    if request.method == 'POST':
        
        incubation_id = request.POST.get('incubation')
        if not incubation_id:
            errors['incubation'] = '* This Field is required'
            
        spoilt_eggs = request.POST.get('spoilt_eggs', 0)
        if spoilt_eggs and int(spoilt_eggs) < 0:
            errors['spoilt_eggs'] = '* This Field must be a valid number'
            
        if incubation_id and spoilt_eggs and int(spoilt_eggs) > Incubation.objects.get(id=incubation_id).eggs:
            errors['spoilt_eggs'] = "* Spoilt eggs quantity cannot exceed the available eggs in the selected incubation."
            
        # Get the candled date or use today's date if not provided
        candled_date = request.POST.get('candled_date') or datetime.datetime.now().date()
        
        if incubation_id and Candling.objects.filter(incubation=incubation_id).exists():
            errors['incubation'] = 'Selected incubation is already candled'
            
        if errors:
            messages.error(request, "Creating candling failed: Please double-check your entries and try again.", extra_tags="danger")
            context = {
                'incubations': Incubation.objects.filter(eggsetting__is_approved=True).exclude(candling_incubation__isnull=False),
                'customers': Customer.objects.all(),
                'breeders': Breeders.objects.all(),
                "errors": errors,
                'today': datetime.datetime.now().date().strftime('%Y-%m-%d'),
            }
            return render(request, 'pages/poultry/hatchery/candling/create.html', context=context)
        
        

        incubation = get_object_or_404(Incubation, id=incubation_id)
        try:    
            # Create the Candling object
            candling = Candling(
                incubation=incubation,
                customer=incubation.customer,
                breeders=incubation.breeders,
                eggs=incubation.eggs,
                candled=True,
                candled_date=candled_date,
                spoilt_eggs=int(spoilt_eggs),  # Default to 0 if not provided
            )
            
            # Save the Candling record
            candling.save()

            # Fetch the associated Eggs object (ensuring the record exists)
            egg = get_object_or_404(Eggs, id=incubation.eggsetting.egg.id)
            
            messages.success(request, 'Candling record created successfully.', extra_tags="success")
            return redirect('candling_list')

        except (ValueError, TypeError) as e:
            messages.error(request, f"An error occurred: {e}")
        except Incubation.DoesNotExist:
            messages.error(request, "The specified incubation does not exist.", extra_tags="danger")
        except Eggs.DoesNotExist:
            messages.error(request, "The related eggs record does not exist.", extra_tags="danger")
    
    # Prepare the context for the GET request or in case of errors
    context = {
        'incubations': Incubation.objects.filter(eggsetting__is_approved=True).exclude(candling_incubation__isnull=False),
        'customers': Customer.objects.all(),
        'breeders': Breeders.objects.all(),
        'today': datetime.datetime.now().date().strftime('%Y-%m-%d'),
    }
    return render(request, 'pages/poultry/hatchery/candling/create.html', context)

@login_required
def candling_delete(request, candlingcode):
    """
    Delete a Candling record.
    """
    candling = get_object_or_404(Candling, candlingcode=candlingcode)

    if request.method == 'POST':
        if Hatching.objects.filter(candling=candling.id).exists():
            messages.error(request, "Cannot delete a candling record that is associated with a hatching record.")
            return redirect('candling_detail', candlingcode=candlingcode)
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
        candling=request.POST.get('candling')
        breeders = request.POST.get('breeders')
        if candling:
            hatching.candling = get_object_or_404(Candling, id=candling)
        if breeders:
            hatching.breeders = get_object_or_404(Breeders, id=breeders)
        hatching.hatched = request.POST.get('hatched')
        hatching.deformed = request.POST.get('deformed')
        hatching.spoilt = request.POST.get('spoilt')
        hatching.notify_customer = request.POST.get('notify_customer') == 'on'

        try:
            hatching.save()
            messages.success(request, 'Hatching record updated successfully.', extra_tags='success')
        except Exception as e:
            messages.error(request, f"Error Updating Hatching: {e}", extra_tags='danger')
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
    errors = {}
    if request.method == 'POST':
        candling_id=request.POST.get('candling')
        deformed = request.POST.get('deformed', 0)
        spoilt = request.POST.get('spoilt', 0)
        
        if not candling_id:
            errors['candling'] = "* This Field is required."
        if candling_id:
            candling = Candling.objects.get(id=candling_id)
            total_count = int(deformed) + int(spoilt)
            if deformed and int(deformed) > candling.fertile_eggs:
                errors['deformed'] = "Deformed eggs quantity value cannot exceed the amount of fertile eggs."
            if spoilt and int(spoilt) > candling.fertile_eggs:
                errors['spoilt'] = "Spoilt eggs quantity value cannot exceed the amount of fertile eggs."
                
            if total_count > candling.fertile_eggs:
                errors['deformed'] = "Total deformed and spoilt eggs count value cannot exceed the amount of fertile eggs."
                errors['spoilt'] = "Total deformed and spoilt eggs count value cannot exceed the amount of fertile eggs."
            
        if errors:
            messages.error(request, "Creating hatching failed: Please double-check your entries and try again.", extra_tags="danger")
            context = {
                'candlings': Candling.objects.exclude(hatching_candling__isnull=False),
                'customers': Customer.objects.all(),
                'breeders': Breeders.objects.all(),
                'errors': errors,
            }
            return render(request, 'pages/poultry/hatchery/hatching/create.html', context=context)
        try:
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
            messages.success(request, 'Hatching record created successfully.', extra_tags="success")
        except Exception as e:
            messages.error(request, f"Creating hatching failed: {str(e)}.", extra_tags="danger")
        return redirect('hatching_list')

    context = {
        'candlings': Candling.objects.exclude(hatching_candling__isnull=False),
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
