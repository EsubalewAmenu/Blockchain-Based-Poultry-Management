# views.py
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.gis.geos import Point
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import EggsForm
from apps.chicks.models import Chicks
from apps.accounts.validators import validate_email

@login_required
def customer_list(request):
    customers = Customer.objects.all()
    paginator = Paginator(customers, 10)
    
    page_number = request.GET.get('page')
    customers = paginator.get_page(page_number)
    return render(request, 'pages/pages/customer/list.html', {'customers': customers})

@login_required
def customer_detail(request, full_name):
    customer = get_object_or_404(Customer, full_name=full_name)
    return render(request, 'pages/pages/customer/details.html', {'customer': customer})

@login_required
def customer_create(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone').replace(' ', '')
        address = request.POST.get('address')
        latitude_str = request.POST.get('latitude', None)
        longitude_str = request.POST.get('longitude', None)

        # Initialize latitude and longitude
        latitude = None
        longitude = None
        if email:
            if not validate_email(email):
                messages.error(request, "This email address does not exist.", extra_tags="danger")
                return redirect('customer_create')
        notification_sms = request.POST.get('notification_sms') == 'on'
        delivery = request.POST.get('delivery') == 'on'
        followup = request.POST.get('followup') == 'on'
        allowed_image_types = ['image/jpeg', 'image/png']  # Allowed image types

        if request.FILES.get('photo'):
            if request.FILES.get('photo').content_type not in allowed_image_types:
                messages.error(request, "Invalid image format for front photo. Only JPEG or PNG is allowed.", extra_tags='danger')
                return redirect('customer_create')
        photo = request.FILES.get('photo')

        customer = Customer(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            latitude=latitude,
            longitude=longitude,
            notification_sms=notification_sms,
            delivery=delivery,
            followup=followup,
            photo=photo
        )
        customer.save()
        messages.success(request, "Customer created successfully", extra_tags="success")
        return redirect('customer_list') 
    else:
        return render(request, 'pages/pages/customer/create.html')

@login_required
def customer_update(request, full_name):
    customer = get_object_or_404(Customer, full_name=full_name)
    if request.method == 'POST':
        # Retrieve data from the form
        customer.first_name = request.POST.get('first_name')
        customer.last_name = request.POST.get('last_name')
        customer.email = request.POST.get('email')
        customer.phone = request.POST.get('phone').replace(' ', '')
        customer.address = request.POST.get('address')
        customer.latitude = request.POST.get('latitude')
        customer.longitude = request.POST.get('longitude')
        customer.notification_sms = request.POST.get('notification_sms') == 'on'
        customer.delivery = request.POST.get('delivery') == 'on'
        customer.followup = request.POST.get('followup') == 'on'
        
        # Handle file upload
        photo = request.FILES.get('photo')
        if photo:
            customer.photo = photo

        customer.save()
        messages.success(request, "Customer Updated Successfully", extra_tags="success")
        return redirect('customer_list')
    else:
        return render(request, 'pages/pages/customer/details.html', {'customer': customer})
 
@login_required    
def customer_update_notifications(request, full_name):
    customer = get_object_or_404(Customer, full_name=full_name)

    if request.method == 'POST':
        customer.notification_sms = 'notification_sms' in request.POST
        customer.delivery = 'delivery' in request.POST
        customer.followup = 'followup' in request.POST

        customer.save() 
        messages.success(request, "Customer Notification Settings Updated Successfully", extra_tags="success")
        return redirect('customer_detail', full_name=customer.full_name)

    return render(request, 'customer_detail.html', {'customer': customer})

@login_required
def customer_delete(request, full_name):
    customer = get_object_or_404(Customer, full_name=full_name)
    if request.method == 'POST':
        customer.delete()
        return redirect('customer_list')
    else:
        return render(request, 'pages/pages/customer/details.html', {'customer': customer})
    
# Eggs

# List all eggs
# List all eggs
@login_required
def eggs_list(request):
    eggs = Eggs.objects.all()
    items = Item.objects.all()
    paginator = Paginator(eggs, 10)  # Show 10 eggs per page
    
    page_number = request.GET.get('page')
    eggs = paginator.get_page(page_number)
    return render(request, 'pages/pages/customer/eggs/list.html', {'eggs': eggs, 'items':items})

# Detail view for a specific egg
@login_required
def eggs_detail(request, batch_number):
    egg = get_object_or_404(Eggs, batchnumber=batch_number)
    egg = get_object_or_404(Eggs, batchnumber=batch_number)
    customers = Customer.objects.all()
    breeds = Breed.objects.all()
    chicks = Chicks.objects.all()  # Get all chicks for selection

    if request.method == 'POST':
        egg.batchnumber = request.POST.get('batchnumber', egg.batchnumber)
        customer_id = request.POST.get('customer')
        breed_id = request.POST.get('breed')
        chick_id = request.POST.get('chick')  # Get selected chick ID

        # Update foreign keys only if they are provided
        if customer_id:
            egg.customer_id = customer_id
        if breed_id:
            egg.breed_id = breed_id
        if chick_id:
            egg.chick_id = chick_id  # Update the chick association

        egg.brought = request.POST.get('brought', egg.brought)
        egg.returned = request.POST.get('returned', egg.returned)
        allowed_image_types = ['image/jpeg', 'image/png']  # Allowed image types

        if request.FILES.get('photo'):
            if request.FILES.get('photo').content_type not in allowed_image_types:
                messages.error(request, "Invalid image format for front photo. Only JPEG or PNG is allowed.", extra_tags='danger')
                return redirect('eggs_detail', batch_number=batch_number)
        # Handle photo upload
        if 'photo' in request.FILES:
            egg.photo = request.FILES['photo']

        egg.save()
        return redirect('eggs_update', batch_number=egg.batchnumber)

    return render(request, 'pages/pages/customer/eggs/details.html', {
        'egg': egg,
        'customers': customers,
        'breeds': breeds,
        'chicks': chicks
    })

# Create a new egg
@login_required
def eggs_create(request):
    customers = Customer.objects.all()
    breeds = Breed.objects.all()
    items = Item.objects.filter(item_type__type_name='Egg')
    chicks = Chicks.objects.all()  # Get all chicks for selection
    item_data = None
    if 'item_data' in request.session:
        item_data = request.session['item_data']
    
    if request.method == 'POST':
        item_id = request.POST.get('item')
        customer_id = request.POST.get('customer')
        chicks_batch = request.POST.get('chick')
        breed_id = request.POST.get('breed')
        photo = request.FILES.get('photo')
        brought = request.POST.get('brought')
        returned = request.POST.get('returned')
        item = Item.objects.get(pk=item_id)
        received = int(brought) - int(returned)
        allowed_image_types = ['image/jpeg', 'image/png']  # Allowed image types

        if request.FILES.get('photo'):
            if request.FILES.get('photo').content_type not in allowed_image_types:
                messages.error(request, "Invalid image format for front photo. Only JPEG or PNG is allowed.", extra_tags='danger')
                return redirect('eggs_create')
        customer = None
        if customer_id:
            customer = get_object_or_404(Customer, id=customer_id)
        batch = None
        if chicks_batch:
            chicks = get_object_or_404(Chicks, batchnumber=chicks_batch)
            batch = chicks.batchnumber
            
           
        if 'item_data' in request.session:
            item_data = request.session['item_data']
        
        # Create and save the egg
        egg = Eggs(
            item=item,
            customer=customer,
            chicks=batch,
            breed_id=breed_id,
            photo=photo,
            brought=brought,
            returned=returned,
            received=received
        )
        egg.save()
        item.quantity=received
        item.save()
        messages.success(request, "Egg Created Successfully", extra_tags="success")
        return redirect('eggs_list')

    return render(request, 'pages/pages/customer/eggs/create.html', {'customers': customers, 'breeds': breeds, 'chicks': chicks, 'items':items, 'item_data':item_data})

# Update an existing egg
@login_required
def eggs_update(request, batch_number):
    egg = get_object_or_404(Eggs, batchnumber=batch_number)
    customers = Customer.objects.all()
    breeds = Breed.objects.all()
    chicks = Chicks.objects.all()  # Get all chicks for selection

    if request.method == 'POST':
        egg.batchnumber = request.POST.get('batchnumber', egg.batchnumber)
        customer_id = request.POST.get('customer')
        breed_id = request.POST.get('breed')
        chick_id = request.POST.get('chick')  # Get selected chick ID
        allowed_image_types = ['image/jpeg', 'image/png']  # Allowed image types

        if request.FILES.get('photo'):
            if request.FILES.get('photo').content_type not in allowed_image_types:
                messages.error(request, "Invalid image format for front photo. Only JPEG or PNG is allowed.", extra_tags='danger')
                return redirect('eggs_update', batch_number=batch_number)
        # Update foreign keys only if they are provided
        if customer_id:
            egg.customer_id = customer_id
        if breed_id:
            egg.breed_id = breed_id
        if chick_id:
            egg.chick_id = chick_id  # Update the chick association

        egg.brought = request.POST.get('brought', egg.brought)
        egg.returned = request.POST.get('returned', egg.returned)

        # Handle photo upload
        if 'photo' in request.FILES:
            egg.photo = request.FILES['photo']

        egg.save()
        messages.success(request, "Egg Updated Successfully", extra_tags="success")
        return redirect('eggs_update', batch_number=egg.batchnumber)

    return render(request, 'pages/pages/customer/eggs/details.html', {
        'egg': egg,
        'customers': customers,
        'breeds': breeds,
        'chicks': chicks
    })

# Delete an egg
@login_required
def eggs_delete(request, batch_number):
    egg = get_object_or_404(Eggs, batchnumber=batch_number)
    if request.method == 'POST':
        egg.delete()
        egg.item.delete()
        messages.success(request, "Egg Deleted Successfully", extra_tags="success")
        return redirect('eggs_list')  
    return render(request, 'pages/pages/customer/eggs/delete.html', {'egg': egg})

# Customer Request
@login_required
def customer_request_list(request):
    customer_requests = CustomerRequest.objects.all()
    paginator = Paginator(customer_requests, 10)  # Paginate the requests
    page_number = request.GET.get('page')
    customer_requests = paginator.get_page(page_number)
    return render(request, 'pages/pages/customer/customer_requests/list.html', {'customer_requests': customer_requests})

def customer_request_detail(request, requestcode):
    customer_request = get_object_or_404(CustomerRequest, requestcode=requestcode)
    return render(request, 'pages/pages/customer/customer_requests/details.html', {'customer_request': customer_request})

def customer_request_create(request):
    if request.method == 'POST':
        eggs_id = request.POST.get('eggs')
        eggs_instance = get_object_or_404(Eggs, id=eggs_id) if eggs_id else None

        customer_request = CustomerRequest(eggs=eggs_instance)
        customer_request.save()
        return redirect('customer_request_list')

    eggs = Eggs.objects.all()
    return render(request, 'pages/pages/customer/customer_requests/create.html', {'eggs': eggs})

def customer_request_update(request, requestcode):
    customer_request = get_object_or_404(CustomerRequest, requestcode=requestcode)
    if request.method == 'POST':
        eggs_id = request.POST.get('eggs')  # Get the new eggs ID
        customer_request.eggs = get_object_or_404(Eggs, id=eggs_id) if eggs_id else customer_request.eggs

        customer_request.save()  # Save the updated instance
        return redirect('customer_request_detail', requestcode=customer_request.requestcode)

    eggs = Eggs.objects.all()  # Retrieve all eggs for the dropdown
    return render(request, 'pages/pages/customer/customer_requests/details.html', {'customer_request': customer_request, 'eggs': eggs})

def customer_request_delete(request, requestcode):
    customer_request = get_object_or_404(CustomerRequest, requestcode=requestcode)
    if request.method == 'POST':
        customer_request.delete()  # Delete the instance
        return redirect('customer_request_list')  # Redirect to the list view
    return render(request, 'pages/pages/customer/customer_requests/details.html', {'customer_request': customer_request})