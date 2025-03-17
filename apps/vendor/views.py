# views.py
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.gis.geos import Point
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

# from apps.hatchery.models import FeedSetting
from apps.inventory.models import ItemRequest
from .models import *
# from .forms import FeedsForm
from apps.chicks.models import Chicks
from apps.accounts.validators import validate_email
from apps.dashboard.utils import encrypt_data, decrypt_data, split_string
import requests
import os

@login_required
def vendor_list(request):
    vendors = Vendor.objects.all()
    paginator = Paginator(vendors, 10)
    
    page_number = request.GET.get('page')
    vendors = paginator.get_page(page_number)
    return render(request, 'pages/pages/vendor/list.html', {'vendors': vendors})

@login_required
def vendor_detail(request, full_name):
    vendor = get_object_or_404(Vendor, full_name=full_name)
    return render(request, 'pages/pages/vendor/details.html', {'vendor': vendor})

@login_required
def vendor_create(request):
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
        
        if Vendor.objects.filter(email=email).exists():
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
            messages.error(request, "Creating vendor failed: Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/pages/vendor/create.html', {'errors': errors})
        
        try:
            vendor = Vendor(
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
            vendor.save()
            messages.success(request, "vendor created successfully", extra_tags="success")
        except Exception as e:
            messages.error(request, f"Creating vendor failed: {str(e)}", extra_tags='danger')
            return render(request, 'pages/pages/vendor/create.html', {'errors': errors})
        return redirect('vendor_list') 
    else:
        return render(request, 'pages/pages/vendor/create.html')

@login_required
def vendor_update(request, full_name):
    vendor = get_object_or_404(Vendor, full_name=full_name)
    errors = {}
    if request.method == 'POST':
        # Retrieve data from the form
        vendor.first_name = request.POST.get('first_name')
        vendor.last_name = request.POST.get('last_name')
        vendor.email = request.POST.get('email')
        vendor.phone = request.POST.get('phone').replace(' ', '')
        vendor.address = request.POST.get('address')
        vendor.notification_sms = request.POST.get('notification_sms') == 'on'
        vendor.delivery = request.POST.get('delivery') == 'on'
        vendor.followup = request.POST.get('followup') == 'on'
        
        # Handle file upload
        photo = request.FILES.get('photo')
        allowed_image_types = ['image/jpeg', 'image/png']
        
        
            
        if request.POST.get('email'):
            if Vendor.objects.filter(email=request.POST.get('email')).exclude(full_name=full_name).exists():
                errors['email'] = "This email address is already registered."
            if not validate_email(request.POST.get('email')):
                errors['email'] = "This email address is not valid."
                
        if photo:
            if request.FILES.get('photo').content_type not in allowed_image_types:
                errors['photo'] = "Invalid image format for front photo. Only JPEG or PNG is allowed."
            vendor.photo = photo
            
        if errors:
            messages.error(request, "Updating vendor failed: Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/pages/vendor/details.html', {'vendor': vendor, 'errors': errors})
        try:
            vendor.save()
        except Exception as e:
            messages.error(request, f"Updating vendor failed: {str(e)}", extra_tags='danger')
            return render(request, 'pages/pages/vendor/details.html', {'vendor': vendor, 'errors': errors})
        messages.success(request, "vendor Updated Successfully", extra_tags="success")
        return redirect('vendor_list')
    else:
        return render(request, 'pages/pages/vendor/details.html', {'vendor': vendor})
 
@login_required    
def vendor_update_notifications(request, full_name):
    vendor = get_object_or_404(vendor, full_name=full_name)

    if request.method == 'POST':
        vendor.notification_sms = 'notification_sms' in request.POST
        vendor.delivery = 'delivery' in request.POST
        vendor.followup = 'followup' in request.POST

        vendor.save() 
        messages.success(request, "vendor Notification Settings Updated Successfully", extra_tags="success")
        return redirect('vendor_detail', full_name=vendor.full_name)

    return render(request, 'vendor_detail.html', {'vendor': vendor})

@login_required
def vendor_delete(request, full_name):
    vendor = get_object_or_404(vendor, full_name=full_name)
    if request.method == 'POST':
        if feeds.objects.filter(vendor=vendor).exists() or Chicks.objects.filter(vendor=vendor).exists():
            messages.error(request, "Cannot delete vendor associated with feeds or chicks.", extra_tags='danger')
            return redirect('vendor_detail', full_name=vendor.full_name)
        vendor.delete()
        return redirect('vendor_list')
    else:
        return render(request, 'pages/pages/vendor/details.html', {'vendor': vendor})
    
# feeds

# List all feeds
@login_required
def feeds_list(request):
    feeds = feeds.objects.all().order_by('-created')
    items = Item.objects.all()
    paginator = Paginator(feeds, 10)  # Show 10 feeds per page
    
    page_number = request.GET.get('page')
    feeds = paginator.get_page(page_number)
    return render(request, 'pages/pages/vendor/feeds/list.html', {'feeds': feeds, 'items':items})

# Detail view for a specific feed
@login_required
def feeds_detail(request, batch_number):
    feed = get_object_or_404(feeds, batchnumber=batch_number)
    vendors = vendor.objects.all()
    breeds = Breed.objects.all()
    chicks = Chicks.objects.all()  # Get all chicks for selection
    errors={}
    if request.method == 'POST':
        feed.batchnumber = request.POST.get('batchnumber', feed.batchnumber)
        vendor_id = request.POST.get('vendor')
        breed_id = request.POST.get('breed')
        chick_id = request.POST.get('chick')  # Get selected chick ID
        allowed_image_types = ['image/jpeg', 'image/png']  # Allowed image types

        if request.FILES.get('photo'):
            if request.FILES.get('photo').content_type not in allowed_image_types:
                errors['photo'] = "Invalid image format for front photo. Only JPEG or PNG is allowed."
            else:
                feed.photo = request.FILES['photo']
                
        # Update foreign keys only if they are provided
        if vendor_id:
            feed.vendor_id = vendor_id
        if breed_id:
            feed.breed_id = breed_id
        if chick_id:
            feed.chick_id = chick_id  # Update the chick association

        feed.brought = request.POST.get('brought', feed.brought)
        feed.returned = request.POST.get('returned', feed.returned)
        
        if request.POST.get('brought') and request.POST.get('returned'):
            if int(request.POST.get('returned')) > int(request.POST.get('brought')):
                errors['returned'] = "* Returned number cannot be greater than brought number."
                
        if request.POST.get('returned') and int(request.POST.get('returned')) > int(feed.brought):
            errors['returned'] = "* Returned number cannot be greater than brought number."
            
        if errors:
            messages.error(request, "Updating feed failed: Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/pages/vendor/feeds/details.html', {
                'feed': feed,
                'vendors': vendors,
                'breeds': breeds,
                'chicks': chicks,
                'errors': errors
            })
        try:    
            feed.save()
            messages.success(request, "feed Updated Successfully", extra_tags="success")
        except Exception as e:
            messages.error(request, "Error updating feed: " + str(e), extra_tags='danger')
            
        return redirect('feeds_update', batch_number=feed.batchnumber)

    return render(request, 'pages/pages/vendor/feeds/details.html', {
        'feed': feed,
        'vendors': vendors,
        'breeds': breeds,
        'chicks': chicks
    })

# Create a new feed
@login_required
def feeds_create(request):
    vendors = vendor.objects.all()
    breeds = Breed.objects.all()
    items = Item.objects.filter(item_type__type_name='feed')
    chicks = Chicks.objects.all()  # Get all chicks for selection
    item_data = None
    errors = {}
    if 'item_data' in request.session:
        item_data = request.session['item_data']
    
    if request.method == 'POST':
        item_id = request.POST.get('item')
        vendor_id = request.POST.get('vendor')
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
            elif source == 'vendor' and not vendor_id:
                errors['vendor'] = "* This field is required"

        if request.FILES.get('photo'):
            if request.FILES.get('photo').content_type not in allowed_image_types:
                errors['photo'] = "Invalid image format for front photo. Only JPEG or PNG is allowed."
                
        vendor = None
        if vendor_id:
            vendor = get_object_or_404(vendor, id=vendor_id)
        batch = None
        if chicks_batch:
            chicks = get_object_or_404(Chicks, batchnumber=chicks_batch)
            batch = chicks.batchnumber
            
        if errors:
            messages.error(request, "Creating feed failed: Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/pages/vendor/feeds/create.html', {'vendors': vendors, 'breeds': breeds, 'chicks': chicks, 'items': items, 'item_data': item_data, 'errors': errors})
               
        if 'item_data' in request.session:
            item_data = request.session['item_data']
        
        # Create and save the feed
        try:
            feed = feeds(
                item=item,
                vendor=vendor,
                chicks=batch,
                source =source,
                breed_id=breed_id,
                photo=photo,
                brought=brought,
                returned=returned)
                
            is_minted = mint_feed_item(item, vendor, chicks, source , breed_id, photo, brought, returned)
            
            if is_minted:
                feed.save()
                
                messages.success(request, "feed Created Successfully", extra_tags="success")
        except Exception as e:
            messages.error(request, "Error creating feed: " + str(e), extra_tags='danger')
            
        if 'item_data' in request.session:
            request.session.pop('item_data')
        return redirect('feeds_list')

    return render(request, 'pages/pages/vendor/feeds/create.html', {'vendors': vendors, 'breeds': breeds, 'chicks': chicks, 'items':items, 'item_data':item_data})

def mint_feed_item(item, vendor, chicks, source, breed_id, photo, brought, returned):


        try:
            if source == 'farm':
                name_or_chicks = chicks.batchnumber
            elif source == 'vendor':
                name_or_chicks = vendor.full_name

            breed = Breed.objects.get(pk=breed_id)

            api_data = {
                    "tokenName": item.code,
                    "blockfrostKey": os.getenv('blockfrostKey'),
                    "secretSeed": os.getenv('secretSeed'),
                    "cborHex": os.getenv('cborHex')
                }
                
            if os.getenv('data_encryption', 'False') == 'True':
                offchain_data = {
                    "item_type": split_string(encrypt_data(item.item_type.type_name), "item_type"),
                    "source": split_string(encrypt_data(source), "source"),
                    "vendor": split_string(encrypt_data(name_or_chicks), "vendor"),
                    "breed": split_string(encrypt_data(breed.code), "breed"),
                    "breed_type": split_string(encrypt_data(breed.breed), "breed_type"),
                    "brought": split_string(encrypt_data(brought), "brought"),
                    "returned": split_string(encrypt_data(returned), "returned"),
                    "received": split_string(encrypt_data(str(int(brought) - int(returned))), "received"),
                }
                api_data['metadata'] = offchain_data
            else:
                api_data['metadata'] = {
                    "item_type": item.item_type.type_name,
                    "source": source,
                    "vendor": name_or_chicks,
                    "breed": breed.code,
                    "breed_type": breed.breed,
                    "brought": int(brought),
                    "returned": int(returned),
                    "received": int(brought) - int(returned)
                }

            response = requests.post(os.getenv('OFFCHAIN_BASE_URL')+'mint', json=api_data, verify=False)
            response_data = response.json()

            if response.status_code == 200 and 'status' in response_data:
                print(response_data)
                item.txHash = response_data['txHash']
                item.policyId = response_data['policyId']
                item.save()
                return True
            else:
                return False
        
        except requests.exceptions.RequestException as e:
            return False
        

# Update an existing feed
@login_required
def feeds_update(request, batch_number):
    feed = get_object_or_404(feeds, batchnumber=batch_number)
    vendors = vendor.objects.all()
    breeds = Breed.objects.all()
    chicks = Chicks.objects.all()  # Get all chicks for selection
    errors={}
    if request.method == 'POST':
        feed.batchnumber = request.POST.get('batchnumber', feed.batchnumber)
        vendor_id = request.POST.get('vendor')
        breed_id = request.POST.get('breed')
        chick_id = request.POST.get('chick')  # Get selected chick ID
        allowed_image_types = ['image/jpeg', 'image/png']  # Allowed image types

        if request.FILES.get('photo'):
            if request.FILES.get('photo').content_type not in allowed_image_types:
                errors['photo'] = "Invalid image format for front photo. Only JPEG or PNG is allowed."
            else:
                feed.photo = request.FILES['photo']
                
        # Update foreign keys only if they are provided
        if vendor_id:
            feed.vendor_id = vendor_id
        if breed_id:
            feed.breed_id = breed_id
        if chick_id:
            feed.chick_id = chick_id  # Update the chick association

        feed.brought = request.POST.get('brought', feed.brought)
        feed.returned = request.POST.get('returned', feed.returned)
        
        if request.POST.get('brought') and request.POST.get('returned'):
            if int(request.POST.get('returned')) > int(request.POST.get('brought')):
                errors['returned'] = "* Returned number cannot be greater than brought number."
                
        if request.POST.get('returned') and int(request.POST.get('returned')) > int(feed.brought):
            errors['returned'] = "* Returned number cannot be greater than brought number."
            
        if errors:
            messages.error(request, "Updating feed failed: Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/pages/vendor/feeds/details.html', {
                'feed': feed,
                'vendors': vendors,
                'breeds': breeds,
                'chicks': chicks,
                'errors': errors
            })
        try:    
            feed.save()
            messages.success(request, "feed Updated Successfully", extra_tags="success")
        except Exception as e:
            messages.error(request, "Error updating feed: " + str(e), extra_tags='danger')
            
        return redirect('feeds_update', batch_number=feed.batchnumber)

    return render(request, 'pages/pages/vendor/feeds/details.html', {
        'feed': feed,
        'vendors': vendors,
        'breeds': breeds,
        'chicks': chicks
    })

# Delete an feed
@login_required
def feeds_delete(request, batch_number):
    feed = get_object_or_404(feeds, batchnumber=batch_number)
    if request.method == 'POST':
        if ItemRequest.objects.filter(item=feed.item).exists():
            messages.error(request, "Cannot delete feed because it has associated item requests.", extra_tags='danger')
            return redirect('feeds_list', batch_number=feed.batchnumber)
        if feedSetting.objects.filter(feed=feed).exists():
            messages.error(request, "Cannot delete feed because it has associated feed settings.", extra_tags='danger')
            return redirect('feeds_list', batch_number=feed.batchnumber)
        feed.delete()
        feed.item.delete()
        messages.success(request, "feed Deleted Successfully", extra_tags="success")
        return redirect('feeds_list')  
    return render(request, 'pages/pages/vendor/feeds/delete.html', {'feed': feed})

# vendor Request
@login_required
def vendor_request_list(request):
    vendor_requests = vendorRequest.objects.all()
    paginator = Paginator(vendor_requests, 10)  # Paginate the requests
    page_number = request.GET.get('page')
    vendor_requests = paginator.get_page(page_number)
    return render(request, 'pages/pages/vendor/vendor_requests/list.html', {'vendor_requests': vendor_requests})

def vendor_request_detail(request, requestcode):
    vendor_request = get_object_or_404(vendorRequest, requestcode=requestcode)
    return render(request, 'pages/pages/vendor/vendor_requests/details.html', {'vendor_request': vendor_request})

def vendor_request_create(request):
    if request.method == 'POST':
        feeds_id = request.POST.get('feeds')
        feeds_instance = get_object_or_404(feeds, id=feeds_id) if feeds_id else None

        vendor_request = vendorRequest(feeds=feeds_instance)
        vendor_request.save()
        return redirect('vendor_request_list')

    feeds = feeds.objects.all()
    return render(request, 'pages/pages/vendor/vendor_requests/create.html', {'feeds': feeds})

def vendor_request_update(request, requestcode):
    vendor_request = get_object_or_404(vendorRequest, requestcode=requestcode)
    if request.method == 'POST':
        feeds_id = request.POST.get('feeds')  # Get the new feeds ID
        vendor_request.feeds = get_object_or_404(feeds, id=feeds_id) if feeds_id else vendor_request.feeds

        vendor_request.save()  # Save the updated instance
        return redirect('vendor_request_detail', requestcode=vendor_request.requestcode)

    feeds = feeds.objects.all()  # Retrieve all feeds for the dropdown
    return render(request, 'pages/pages/vendor/vendor_requests/details.html', {'vendor_request': vendor_request, 'feeds': feeds})

def vendor_request_delete(request, requestcode):
    vendor_request = get_object_or_404(vendorRequest, requestcode=requestcode)
    if request.method == 'POST':
        vendor_request.delete()  # Delete the instance
        return redirect('vendor_request_list')  # Redirect to the list view
    return render(request, 'pages/pages/vendor/vendor_requests/details.html', {'vendor_request': vendor_request})