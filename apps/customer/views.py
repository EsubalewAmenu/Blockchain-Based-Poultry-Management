# views.py
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.gis.geos import Point
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from apps.hatchery.models import EggSetting
from apps.inventory.models import ItemRequest
from .models import *
from .forms import EggsForm
from apps.chicks.models import Chicks
from apps.accounts.validators import validate_email
import requests
import os

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
    errors = {}
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone').replace(' ', '')
        address = request.POST.get('address')
        photo = request.FILES.get('photo', None)
        required_fields = ['first_name','last_name', 'email', 'phone']
        
        for field in required_fields:
            if not request.POST.get(field):
                errors[field] = "* This field is required"
        
        if Customer.objects.filter(email=email).exists():
            errors['email'] = "This email address is already registered."
            
        if email:
            if not validate_email(email):
                errors['email'] = "This email address is not valid."
                
            
        notification_sms = request.POST.get('notification_sms') == 'on'
        delivery = request.POST.get('delivery') == 'on'
        followup = request.POST.get('followup') == 'on'
        allowed_image_types = ['image/jpeg', 'image/png']

        if request.FILES.get('photo'):
            if request.FILES.get('photo').content_type not in allowed_image_types:
                errors['photo'] = "Invalid image format for front photo. Only JPEG or PNG is allowed."
        

        if errors:
            messages.error(request, "Creating customer failed: Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/pages/customer/create.html', {'errors': errors})
        
        try:
            customer = Customer(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address=address,
                notification_sms=notification_sms,
                delivery=delivery,
                followup=followup,
                photo=photo
            )
            customer.save()
            messages.success(request, "Customer created successfully", extra_tags="success")
        except Exception as e:
            messages.error(request, f"Creating customer failed: {str(e)}", extra_tags='danger')
            return render(request, 'pages/pages/customer/create.html', {'errors': errors})
        return redirect('customer_list') 
    else:
        return render(request, 'pages/pages/customer/create.html')

@login_required
def customer_update(request, full_name):
    customer = get_object_or_404(Customer, full_name=full_name)
    errors = {}
    if request.method == 'POST':
        # Retrieve data from the form
        customer.first_name = request.POST.get('first_name')
        customer.last_name = request.POST.get('last_name')
        customer.email = request.POST.get('email')
        customer.phone = request.POST.get('phone').replace(' ', '')
        customer.address = request.POST.get('address')
        customer.notification_sms = request.POST.get('notification_sms') == 'on'
        customer.delivery = request.POST.get('delivery') == 'on'
        customer.followup = request.POST.get('followup') == 'on'
        
        # Handle file upload
        photo = request.FILES.get('photo')
        allowed_image_types = ['image/jpeg', 'image/png']
        
        
            
        if request.POST.get('email'):
            if Customer.objects.filter(email=request.POST.get('email')).exclude(full_name=full_name).exists():
                errors['email'] = "This email address is already registered."
            if not validate_email(request.POST.get('email')):
                errors['email'] = "This email address is not valid."
                
        if photo:
            if request.FILES.get('photo').content_type not in allowed_image_types:
                errors['photo'] = "Invalid image format for front photo. Only JPEG or PNG is allowed."
            customer.photo = photo
            
        if errors:
            messages.error(request, "Updating customer failed: Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/pages/customer/details.html', {'customer': customer, 'errors': errors})
        try:
            customer.save()
        except Exception as e:
            messages.error(request, f"Updating customer failed: {str(e)}", extra_tags='danger')
            return render(request, 'pages/pages/customer/details.html', {'customer': customer, 'errors': errors})
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
        if Eggs.objects.filter(customer=customer).exists() or Chicks.objects.filter(customer=customer).exists():
            messages.error(request, "Cannot delete customer associated with eggs or chicks.", extra_tags='danger')
            return redirect('customer_detail', full_name=customer.full_name)
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
    customers = Customer.objects.all()
    breeds = Breed.objects.all()
    chicks = Chicks.objects.all()  # Get all chicks for selection
    errors={}
    if request.method == 'POST':
        egg.batchnumber = request.POST.get('batchnumber', egg.batchnumber)
        customer_id = request.POST.get('customer')
        breed_id = request.POST.get('breed')
        chick_id = request.POST.get('chick')  # Get selected chick ID
        allowed_image_types = ['image/jpeg', 'image/png']  # Allowed image types

        if request.FILES.get('photo'):
            if request.FILES.get('photo').content_type not in allowed_image_types:
                errors['photo'] = "Invalid image format for front photo. Only JPEG or PNG is allowed."
            else:
                egg.photo = request.FILES['photo']
                
        # Update foreign keys only if they are provided
        if customer_id:
            egg.customer_id = customer_id
        if breed_id:
            egg.breed_id = breed_id
        if chick_id:
            egg.chick_id = chick_id  # Update the chick association

        egg.brought = request.POST.get('brought', egg.brought)
        egg.returned = request.POST.get('returned', egg.returned)
        
        if request.POST.get('brought') and request.POST.get('returned'):
            if int(request.POST.get('returned')) > int(request.POST.get('brought')):
                errors['returned'] = "* Returned number cannot be greater than brought number."
                
        if request.POST.get('returned') and int(request.POST.get('returned')) > int(egg.brought):
            errors['returned'] = "* Returned number cannot be greater than brought number."
            
        if errors:
            messages.error(request, "Updating egg failed: Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/pages/customer/eggs/details.html', {
                'egg': egg,
                'customers': customers,
                'breeds': breeds,
                'chicks': chicks,
                'errors': errors
            })
        try:    
            egg.save()
            messages.success(request, "Egg Updated Successfully", extra_tags="success")
        except Exception as e:
            messages.error(request, "Error updating egg: " + str(e), extra_tags='danger')
            
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
    errors = {}
    if 'item_data' in request.session:
        item_data = request.session['item_data']
    
    if request.method == 'POST':
        item_id = request.POST.get('item')
        customer_id = request.POST.get('customer')
        chicks_batch = request.POST.get('chick')
        source = request.POST.get('source')
        breed_id = request.POST.get('breed')
        photo = request.FILES.get('photo')
        brought = request.POST.get('brought')
        returned = request.POST.get('returned', 0)
        item = Item.objects.get(pk=item_id)
        allowed_image_types = ['image/jpeg', 'image/png']
        
        required_fields = ['item', 'breed', 'brought', 'source']
        for field in required_fields:
            if not request.POST.get(field):
                errors[field] = "* This field is required."
        if brought:
            if int(brought) <= 0:
                errors['brought'] = "* Please enter a positive number."
                
        if brought and returned and int(returned) > int(brought):
            errors['returned'] = "* Returned number cannot be greater than brought number."
            
        if not brought and returned and int(returned) >0:
            errors['returned'] = "* Returned number cannot be provided without brought number."
                
        if source:
            if source == 'farm' and not chicks_batch:
                errors['chick'] = "* This field is required"
            elif source == 'customer' and not customer_id:
                errors['customer'] = "* This field is required"

        if request.FILES.get('photo'):
            if request.FILES.get('photo').content_type not in allowed_image_types:
                errors['photo'] = "Invalid image format for front photo. Only JPEG or PNG is allowed."
                
        customer = None
        if customer_id:
            customer = get_object_or_404(Customer, id=customer_id)
        batch = None
        if chicks_batch:
            chicks = get_object_or_404(Chicks, batchnumber=chicks_batch)
            batch = chicks.batchnumber
            
        if errors:
            messages.error(request, "Creating egg failed: Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/pages/customer/eggs/create.html', {'customers': customers, 'breeds': breeds, 'chicks': chicks, 'items': items, 'item_data': item_data, 'errors': errors})
               
        if 'item_data' in request.session:
            item_data = request.session['item_data']
        
        # Create and save the egg
        try:
            egg = Eggs(
                item=item,
                customer=customer,
                chicks=batch,
                source =source,
                breed_id=breed_id,
                photo=photo,
                brought=brought,
                returned=returned)
                
            is_minted = mint_egg_item(item, customer, chicks, source , breed_id, photo, brought, returned)
            
            if is_minted:
                egg.save()
                
                messages.success(request, "Egg Created Successfully", extra_tags="success")
        except Exception as e:
            messages.error(request, "Error creating egg: " + str(e), extra_tags='danger')
            
        if 'item_data' in request.session:
            request.session.pop('item_data')
        return redirect('eggs_list')

    return render(request, 'pages/pages/customer/eggs/create.html', {'customers': customers, 'breeds': breeds, 'chicks': chicks, 'items':items, 'item_data':item_data})

def mint_egg_item(item, customer, chicks, source, breed_id, photo, brought, returned):


        try:
            if source == 'farm':
                name_or_chicks = chicks.batchnumber
            elif source == 'customer':
                name_or_chicks = customer.full_name


            api_data = {
                    "tokenName": item.code,
                    "metadata": {
                        "item_type": item.item_type.type_name,
                        "source": source,
                        source: name_or_chicks,
                        "breed": breed_id,
                        "brought": int(brought),
                        "returned": int(returned),
                        "received": int(brought) - int(returned)
                        },
                    "blockfrostKey": os.getenv('blockfrostKey'),
                    "secretSeed": os.getenv('secretSeed'),
                    "cborHex": os.getenv('cborHex')
                }

            response = requests.post(os.getenv('OFFCHAIN_BASE_URL')+'mint', json=api_data)
            response_data = response.json()

            if response.status_code == 200 and 'status' in response_data:
                print(response_data)
                item.txHash = response_data['txHash']
                item.policyId = response_data['policyId']
                item.save()
                return True
            else:
                return JsonResponse({'error': 'Unexpected API response'}, status=400)
        
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return JsonResponse({'error': 'Failed to communicate with the external API'}, status=500)
        

# Update an existing egg
@login_required
def eggs_update(request, batch_number):
    egg = get_object_or_404(Eggs, batchnumber=batch_number)
    customers = Customer.objects.all()
    breeds = Breed.objects.all()
    chicks = Chicks.objects.all()  # Get all chicks for selection
    errors={}
    if request.method == 'POST':
        egg.batchnumber = request.POST.get('batchnumber', egg.batchnumber)
        customer_id = request.POST.get('customer')
        breed_id = request.POST.get('breed')
        chick_id = request.POST.get('chick')  # Get selected chick ID
        allowed_image_types = ['image/jpeg', 'image/png']  # Allowed image types

        if request.FILES.get('photo'):
            if request.FILES.get('photo').content_type not in allowed_image_types:
                errors['photo'] = "Invalid image format for front photo. Only JPEG or PNG is allowed."
            else:
                egg.photo = request.FILES['photo']
                
        # Update foreign keys only if they are provided
        if customer_id:
            egg.customer_id = customer_id
        if breed_id:
            egg.breed_id = breed_id
        if chick_id:
            egg.chick_id = chick_id  # Update the chick association

        egg.brought = request.POST.get('brought', egg.brought)
        egg.returned = request.POST.get('returned', egg.returned)
        
        if request.POST.get('brought') and request.POST.get('returned'):
            if int(request.POST.get('returned')) > int(request.POST.get('brought')):
                errors['returned'] = "* Returned number cannot be greater than brought number."
                
        if request.POST.get('returned') and int(request.POST.get('returned')) > int(egg.brought):
            errors['returned'] = "* Returned number cannot be greater than brought number."
            
        if errors:
            messages.error(request, "Updating egg failed: Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/pages/customer/eggs/details.html', {
                'egg': egg,
                'customers': customers,
                'breeds': breeds,
                'chicks': chicks,
                'errors': errors
            })
        try:    
            egg.save()
            messages.success(request, "Egg Updated Successfully", extra_tags="success")
        except Exception as e:
            messages.error(request, "Error updating egg: " + str(e), extra_tags='danger')
            
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
        if ItemRequest.objects.filter(item=egg.item).exists():
            messages.error(request, "Cannot delete egg because it has associated item requests.", extra_tags='danger')
            return redirect('eggs_list', batch_number=egg.batchnumber)
        if EggSetting.objects.filter(egg=egg).exists():
            messages.error(request, "Cannot delete egg because it has associated egg settings.", extra_tags='danger')
            return redirect('eggs_list', batch_number=egg.batchnumber)
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