from datetime import datetime, timezone
from apps.dashboard.utils import encrypt_data, decrypt_data, split_string
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
from apps.chicks.views import mint_chicks_item
from apps.inventory.models import ItemType, Item
from apps.dashboard.models import Tracker
from django.http import JsonResponse
from .models import *
import requests
import time
import os

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
        required_fields = ['email', 'phone', 'name', 'totalcapacity']
        
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
            print("Error: %s" % errors)
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
    incubators = Incubators.objects.all().select_related('hatchery').order_by('-created')
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
        manufacturer_details = request.POST['manufacturer_details']
        
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

        item.quantity = 1
        is_minted = mint_incubators_item(hatchery, incubatortype, manufacturer, model, year, manufacturer_details, item)
        
        if is_minted:
            incubator.save()
            item.save()
        messages.success(request, "Incubator created successfully", extra_tags='success')
        if 'item_data' in request.session:
            request.session.pop('item_data')
        return redirect('incubator_list')
    
    return render(request, 'pages/poultry/incubators/create.html', {'hatcheries': hatcheries, 'items':items, 'item_data':item_data})


def mint_incubators_item(hatchery, incubatortype, manufacturer, model, year, manufacturer_details, item):
        try:

            api_data = {
                    "tokenName": item.code,
                    "blockfrostKey": os.getenv('blockfrostKey'),
                    "secretSeed": os.getenv('secretSeed'),
                    "cborHex": os.getenv('cborHex')
                }


            if os.getenv('data_encryption', 'False') == 'True':
                offchain_data = {
                    "item_type": split_string(encrypt_data(item.item_type.type_name), "item_type"),
                    "hatchery_name": split_string(encrypt_data(hatchery.name), "hatchery_name"),
                    "incubatortype": split_string(encrypt_data(incubatortype), "incubatortype"),
                    "manufacturer": split_string(encrypt_data(manufacturer), "manufacturer"),
                    "model": split_string(encrypt_data(model), "model"),
                    "year": split_string(encrypt_data(year), "year"),
                    "manufacturer_details": split_string(encrypt_data(manufacturer_details), "manufacturer_details"),
                }
                api_data['metadata'] = offchain_data
            else:
                api_data['metadata'] = {
                        "item_type": item.item_type.type_name,
                        "hatchery_name": hatchery.name,
                        "incubatortype": incubatortype,
                        "manufacturer": manufacturer,
                        "model": model,
                        "year": year,
                        "manufacturer_details": manufacturer_details
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
                return JsonResponse({'error': 'Unexpected API response'}, status=400)
        
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return JsonResponse({'error': 'Failed to communicate with the external API'}, status=500)
        
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
def feeding_list(request):
    feedings = Feedings.objects.all().order_by('-created')
    for feeding in feedings:
        feeding.chick = Chicks.objects.filter(id=feeding.chicks).first()

    paginator = Paginator(feedings, 10)
    
    page_number = request.GET.get('page')
    feedings = paginator.get_page(page_number)
    return render(request, 'pages/poultry/feeding/list.html', {'feedings': feedings})
    

def feedsetting_detail_api(request, feedsetting_id):
    feed_setting = FeedSetting.objects.filter(pk=feedsetting_id)
    if feed_setting:
        return render(request, 'pages/poultry/tracking/feedsetting_detail.html', {'feed_settings': feed_setting})
    return HttpResponse('<p>No Detail found.</p>')

def feed_detail_api(request, feed_id):
    feed = Feeds.objects.filter(pk=feed_id).first()
    feed_setting = FeedSetting.objects.filter(feed=feed)
    if feed_setting:
        return render(request, 'pages/poultry/tracking/feedsetting_detail.html', {'feed_settings': feed_setting})
    return HttpResponse('<p>No Detail found.</p>')


def chick_feeding_detail_api(request, chick_id):
    items = Feedings.objects.filter(chicks=chick_id)
    if items:
        for item in items:
            item.chick = Chicks.objects.filter(pk=item.chicks).first()

        return render(request, 'pages/poultry/tracking/feedings_detail.html', {'items': items})
    return HttpResponse('<p>No Detail found.</p>')

def chick_feed_uses_detail_api(request, feed_setting_id):
    feed_setting = FeedSetting.objects.filter(pk = feed_setting_id).first()
    items = Feedings.objects.filter(feedsetting=feed_setting)

    if items:
        return render(request, 'pages/poultry/tracking/feedings_detail.html', {'items': items})
    return HttpResponse('<p>No Detail found.</p>')

def chick_medications_detail_api(request, chick_id):
    items = Medications.objects.filter(chicks=chick_id)
    if items:
        return render(request, 'pages/poultry/tracking/medications_detail.html', {'items': items})
    return HttpResponse('<p>No Detail found.</p>')

def chick_medication_uses_detail_api(request, medicine_setting_id):
    medicine_setting = MedicineSetting.objects.filter(pk=medicine_setting_id).first()
    items = Medications.objects.filter(medicinesetting=medicine_setting)
    if items:
        return render(request, 'pages/poultry/tracking/medications_detail.html', {'items': items})
    return HttpResponse('<p>No Detail found.</p>')

def medicinesetting_detail_api(request, medicinesetting_id):
    medicine_setting = MedicineSetting.objects.filter(pk=medicinesetting_id)
    if medicine_setting:
        return render(request, 'pages/poultry/tracking/medicinesetting_detail.html', {'medicine_settings': medicine_setting})
    return HttpResponse('<p>No Detail found.</p>')

def medicinesettings_detail_api(request, medicine_id):
    medicine_inventory = MedicineInventory.objects.filter(pk=medicine_id).first()

    medicine_settings = MedicineSetting.objects.filter(medicine=medicine_inventory)
    if medicine_settings:
        return render(request, 'pages/poultry/tracking/medicinesetting_detail.html', {'medicine_settings': medicine_settings})
    return HttpResponse('<p>No Detail found.</p>')

def chick_hatching_detail_api(request, hatching_id):
    hatching = Hatching.objects.filter(pk=hatching_id).first()
    if hatching:
        return render(request, 'pages/poultry/tracking/hatching_detail.html', {'hatching': hatching})
    return HttpResponse('<p>No Hatching detail found.</p>')

@login_required  
def medication_list(request):
    medications = Medications.objects.all().order_by('-created')
    for medication in medications:
        medication.chick = Chicks.objects.filter(id=medication.chicks).first()

    paginator = Paginator(medications, 10)
    
    page_number = request.GET.get('page')
    medications = paginator.get_page(page_number)
    return render(request, 'pages/poultry/medication/list.html', {'medications': medications})
    
@login_required
def medication_create(request):
    item_data = None

    if 'item_data' in request.session:
        item_data = request.session['item_data']

    if request.method == 'POST':
        errors = {}
        required_fields = ['chick_item', 'medicinesetting', 'medication_quantity']
        for field in required_fields:
            if not request.POST.get(field):
                errors[field] = "* This Field is required"

        if errors:
            messages.error(request, "Error creating medication data, Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/medication/create.html', {
                'errors': errors,
                'medicinesettings':  MedicineSetting.objects.filter(is_approved=True, available_quantity__gte=1),
                'chick_items': Chicks.objects.all().order_by('-created'),
            })

        chick_item = get_object_or_404(Chicks, pk=request.POST['chick_item'])
        medicinesetting = get_object_or_404(MedicineSetting, pk=request.POST['medicinesetting'])   
        medication_quantity = request.POST.get('medication_quantity')

        if medication_quantity and int(medication_quantity) > medicinesetting.available_quantity:
            errors['medication_quantity'] = "Insufficient quantity of medicines available for the slected medicine setting."
            return render(request, 'pages/poultry/medication/create.html', {
                'errors': errors,
                'medicinesettings':  MedicineSetting.objects.filter(is_approved=True, available_quantity__gte=1),
                'chick_items': Chicks.objects.all().order_by('-created'),
            })


        medication = Medications(
            chicks=chick_item.pk,
            medicinesetting=medicinesetting,
            quantity=medication_quantity,
        )

        medication.save()

        is_medication_recorded = register_medication_history(medication, medicinesetting, chick_item, medication_quantity)
        
        if is_medication_recorded:
            medicinesetting.available_quantity = medicinesetting.available_quantity - int(medication_quantity)
            medicinesetting.save()
            messages.success(request, "Medication created successfully", extra_tags='success')
            return redirect('medication_list')


        else:
            medication.delete()

            messages.error(request, "Error recording medication, Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/medication/create.html', {
                'medicinesettings': MedicineSetting.objects.filter(is_approved=True, available_quantity__gte=1),
                'chick_items':Chicks.objects.all().order_by('-created'),
                'item_data':item_data})

    

    medicinesettings = MedicineSetting.objects.filter(is_approved=True, available_quantity__gte=1)
    chick_items =Chicks.objects.all().order_by('-created')
    return render(request, 'pages/poultry/medication/create.html', {'medicinesettings': medicinesettings, 'chick_items':chick_items, 'item_data':item_data})

def register_medication_history(medication, medicinesetting, chick, medication_quantity):
        try:

            api_data = {
                    "tokenName": medicinesetting.medicine.item.code,
                    "policyId": medicinesetting.medicine.item.policyId,
                    "code": medication.medicationcode,
                    "blockfrostKey": os.getenv('blockfrostKey'),
                    "secretSeed": os.getenv('secretSeed'),
                    "cborHex": os.getenv('cborHex')
                }

            if os.getenv('data_encryption', 'False') == 'True':
                offchain_data = {
                    "type": split_string(encrypt_data("Medication"), "medicationtype"),
                    "medicationcode": split_string(encrypt_data(medication.medicationcode), "medicationcode"),
                    "medicine_batch": split_string(encrypt_data(medicinesetting.medicine.batchnumber), "medicine_batch"),
                    "item_code": split_string(encrypt_data(medicinesetting.medicine.item.code), "item_code"),
                    "chicks_batchnumber": split_string(encrypt_data(chick.batchnumber), "chicks_batchnumber"),
                    "medication_quantity": split_string(encrypt_data(medication_quantity), "medication_quantity"),
                }
                api_data['metadata'] = offchain_data
            else:
                api_data['metadata'] = {
                        "type": "Medication",
                        "medicationcode": medication.medicationcode,
                        "medicine_batch": medicinesetting.medicine.batchnumber,
                        "item_code": medicinesetting.medicine.item.code,
                        "chicks_batchnumber": chick.batchnumber,
                        "medication_quantity": medication_quantity,
                        }

            response = requests.post(os.getenv('OFFCHAIN_BASE_URL')+'history', json=api_data, verify=False)
            response_data = response.json()
                        
            if response.status_code == 200 and 'status' in response_data:
                medication.txHash = response_data['txHash']
                medication.save()
                return True
            else:
                return False
        
        except requests.exceptions.RequestException as e:
            return False
        
@login_required
def medication_detail(request, code):
    medication = get_object_or_404(Medications, medicationcode=code)
    
    medication.chick = Chicks.objects.filter(id=medication.chicks).first()

    if request.method == 'POST':
        # Update medication instance with the new data from the request
        medication.medication = Medication.objects.get(id=request.POST['medication'])
        medication.medicationtype = request.POST['medicationtype']
        medication.manufacturer = request.POST['manufacturer']
        medication.model = request.POST['model']
        medication.year = request.POST['year']
        medication.code = request.POST['code']
        medication.manufacturer_details = request.POST.get('manufacturer_details', '')
        
        # Save the updated medication instance
        medication.save()
        messages.success(request, 'medication updated successfully.')
        return redirect('medication_detail', code=code)  # Redirect to the medication detail page after saving
    
    return render(request, 'pages/poultry/medication/details.html', {'medication': medication})

@login_required
def medication_update(request, code):
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
def medication_delete(request, code):
    incubator = get_object_or_404(Incubators, code=code)
    
    if request.method == 'POST':
        incubator.delete()
        incubator.item.delete()
        messages.success(request, 'Incubator deleted successfully.')
        return redirect('incubator_list')
    
    return redirect('incubator_list')

@login_required
def feeding_create(request):
    item_data = None

    if 'item_data' in request.session:
        item_data = request.session['item_data']

    if request.method == 'POST':
        errors = {}
        required_fields = ['chick_item', 'feedsetting', 'feed_quantity']
        for field in required_fields:
            if not request.POST.get(field):
                errors[field] = "* This Field is required"

        if errors:
            messages.error(request, "Error creating feeding data, Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/feeding/create.html', {
                'errors': errors,
                'feedsettings':  FeedSetting.objects.filter(is_approved=True, available_quantity__gte=1),
                'chick_items': Chicks.objects.all().order_by('-created'),
            })

        chick_item = get_object_or_404(Chicks, pk=request.POST['chick_item'])
        feedsetting = get_object_or_404(FeedSetting, pk=request.POST['feedsetting'])   
        feed_quantity = request.POST.get('feed_quantity')

        if feed_quantity and int(feed_quantity) > feedsetting.available_quantity:
            errors['feed_quantity'] = "Insufficient quantity of feeds available for the slected feedsetting."


        feeding = Feedings(
            chicks=chick_item.pk,
            feedsetting=feedsetting,
            quantity=feed_quantity,
        )

        feeding.save()

        is_feeding_recorded = register_feeding_history(feeding, feedsetting, chick_item, feed_quantity)
        
        if is_feeding_recorded:
            feedsetting.available_quantity = feedsetting.available_quantity - int(feed_quantity)
            feedsetting.save()
            messages.success(request, "Feeding created successfully", extra_tags='success')

        else:
            feeding.delete()

            messages.error(request, "Error recording feeding, Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/feeding/create.html', {
                'feedsettings': FeedSetting.objects.filter(is_approved=True, available_quantity__gte=1),
                'chick_items':Chicks.objects.all().order_by('-created'),
                'item_data':item_data})
            


        return redirect('feeding_list')
    

    feedsettings = FeedSetting.objects.filter(is_approved=True, available_quantity__gte=1)
    chick_items = Chicks.objects.all().order_by('-created')
    return render(request, 'pages/poultry/feeding/create.html', {'feedsettings': feedsettings, 'chick_items':chick_items, 'item_data':item_data})

def register_feeding_history(feeding, feedsetting, chick, feed_quantity):
        try:

            api_data = {
                    "tokenName": feedsetting.feed.item.code,
                    "policyId": feedsetting.feed.item.policyId,
                    "code": feeding.feedingcode,
                    "blockfrostKey": os.getenv('blockfrostKey'),
                    "secretSeed": os.getenv('secretSeed'),
                    "cborHex": os.getenv('cborHex')
                }

            if os.getenv('data_encryption', 'False') == 'True':
                offchain_data = {
                    "type": split_string(encrypt_data("Feeding"), "feedingtype"),
                    "feedingcode": split_string(encrypt_data(feeding.feedingcode), "feedingcode"),
                    "feed_batch": split_string(encrypt_data(feedsetting.feed.batchnumber), "feed_batch"),
                    "item_code": split_string(encrypt_data(feedsetting.feed.item.code), "item_code"),
                    "chicks_batchnumber": split_string(encrypt_data(chick.batchnumber), "chicks_batchnumber"),
                    "feed_quantity": split_string(encrypt_data(feed_quantity), "feed_quantity"),
                }
                api_data['metadata'] = offchain_data
            else:
                api_data['metadata'] = {
                        "type": "Feeding",
                        "feedingcode": feeding.feedingcode,
                        "feed_batch": feedsetting.feed.batchnumber,
                        "item_code": feedsetting.feed.item.code,
                        "chicks_batchnumber": chick.batchnumber,
                        "feed_quantity": feed_quantity,
                        }

            response = requests.post(os.getenv('OFFCHAIN_BASE_URL')+'history', json=api_data, verify=False)
            response_data = response.json()
                        
            if response.status_code == 200 and 'status' in response_data:
                feeding.txHash = response_data['txHash']
                feeding.save()
                return True
            else:
                return False
        
        except requests.exceptions.RequestException as e:
            return False
        
@login_required
def feeding_detail(request, code):
    feeding = get_object_or_404(Feedings, feedingcode=code)
    
    feeding.chick = Chicks.objects.filter(id=feeding.chicks).first()

    if request.method == 'POST':
        # Update feeding instance with the new data from the request
        feeding.Feeding = Feeding.objects.get(id=request.POST['Feeding'])
        feeding.feedingtype = request.POST['feedingtype']
        feeding.manufacturer = request.POST['manufacturer']
        feeding.model = request.POST['model']
        feeding.year = request.POST['year']
        feeding.code = request.POST['code']
        feeding.manufacturer_details = request.POST.get('manufacturer_details', '')
        
        # Save the updated feeding instance
        feeding.save()
        messages.success(request, 'Feeding updated successfully.')
        return redirect('feeding_detail', code=code)  # Redirect to the feeding detail page after saving
    
    return render(request, 'pages/poultry/feeding/details.html', {'feeding': feeding})

@login_required
def feeding_update(request, code):
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
def feeding_delete(request, code):
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
    egg_settings = EggSetting.objects.all().order_by('-created')
    egg= Eggs.objects.all()
    paginator = Paginator(egg_settings, 10)
    
    page_number = request.GET.get('page')
    egg_settings = paginator.get_page(page_number)
    return render(request, 'pages/poultry/hatchery/egg_setting/list.html', {'egg_settings': egg_settings, 'egg':egg})

#Feed Settings
@login_required
def feed_setting_list(request):
    feed_settings = FeedSetting.objects.all().order_by('-created')
    feed= Feeds.objects.all()
    paginator = Paginator(feed_settings, 10)
    
    page_number = request.GET.get('page')
    feed_settings = paginator.get_page(page_number)
    return render(request, 'pages/poultry/hatchery/feed_setting/list.html', {'feed_settings': feed_settings, 'feed':feed})

#medicine Settings
@login_required
def medicine_setting_list(request):
    medicine_settings = MedicineSetting.objects.all().order_by('-created')
    medicineinventories= MedicineInventory.objects.all()
    paginator = Paginator(medicine_settings, 10)
    
    page_number = request.GET.get('page')
    medicine_settings = paginator.get_page(page_number)
    return render(request, 'pages/poultry/hatchery/medicine_setting/list.html', {'medicine_settings': medicine_settings, 'medicineinventories':medicineinventories})

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

def eggsetting_detail_api(request, egg_id):
    # egg_settings = EggSetting.objects.filter(egg=egg_id).first()
    egg_settings = EggSetting.objects.filter(egg=egg_id)
    if egg_settings:
        return render(request, 'pages/poultry/tracking/eggsetting_detail.html', {'egg_settings': egg_settings})
    return HttpResponse('<p>No Egg Setting found.</p>')

@login_required
def feed_setting_detail(request, settingcode):
    feed_setting = get_object_or_404(FeedSetting, settingcode=settingcode)
    errors={}
    if request.method == 'POST':
        if feed_setting.is_approved:
            messages.success(request, "feed Setting request is already approved ", extra_tags='danger')
            return redirect('feed_setting_detail', settingcode=feed_setting.settingcode)
        feed_setting.settingcode = request.POST.get('settingcode', feed_setting.settingcode)
        feed_setting.incubator = get_object_or_404(Incubators, id=request.POST.get('incubator'))
        feed_setting.breeders = get_object_or_404(Breeders, id=request.POST.get('breeders'))
        if request.POST.get('feeds'):
            if feed_setting.feeds == int(request.POST.get('feeds')):
                pass
            elif feed_setting.item_request.item.quantity < int(request.POST.get('feeds')):
                errors['feeds'] = "Insufficient quantity of feeds available for the slected feed type."
                
            feed_setting.feeds = int(request.POST.get('feeds'))
            feed_setting.item_request.quantity = int(request.POST.get('feeds'))
            feed_setting.item_request.save()
        else:
            feed_setting.feeds = feed_setting.feeds
            
        if errors:
            messages.error(request, "Updating feed setting failed: Please double-check your entries and try again.", extra_tags="danger")
            return render(request, 'pages/poultry/hatchery/feed_setting/details.html', {
                'feed_setting': feed_setting,
                'errors': errors,
                'incubators': Incubators.objects.all(),
                'customers': Customer.objects.all(),
                'breeders': Breeders.objects.all()
            })
        feed_setting.save()
        return redirect('feed_setting_detail', settingcode=feed_setting.settingcode)

    return render(request, 'pages/poultry/hatchery/feed_setting/details.html', {
        'feed_setting': feed_setting,
    })

@login_required
def medicine_setting_detail(request, settingcode):
    medicine_setting = get_object_or_404(medicineSetting, settingcode=settingcode)
    errors={}
    if request.method == 'POST':
        if medicine_setting.is_approved:
            messages.success(request, "medicine Setting request is already approved ", extra_tags='danger')
            return redirect('medicine_setting_detail', settingcode=medicine_setting.settingcode)
        medicine_setting.settingcode = request.POST.get('settingcode', medicine_setting.settingcode)
        medicine_setting.incubator = get_object_or_404(Incubators, id=request.POST.get('incubator'))
        medicine_setting.breeders = get_object_or_404(Breeders, id=request.POST.get('breeders'))
        if request.POST.get('medicines'):
            if medicine_setting.medicines == int(request.POST.get('medicines')):
                pass
            elif medicine_setting.item_request.item.quantity < int(request.POST.get('medicines')):
                errors['medicines'] = "Insufficient quantity of medicines available for the slected medicine type."
                
            medicine_setting.medicines = int(request.POST.get('medicines'))
            medicine_setting.item_request.quantity = int(request.POST.get('medicines'))
            medicine_setting.item_request.save()
        else:
            medicine_setting.medicines = medicine_setting.medicines
            
        if errors:
            messages.error(request, "Updating medicine setting failed: Please double-check your entries and try again.", extra_tags="danger")
            return render(request, 'pages/poultry/hatchery/medicine_setting/details.html', {
                'medicine_setting': medicine_setting,
                'errors': errors,
                'incubators': Incubators.objects.all(),
                'customers': Customer.objects.all(),
                'breeders': Breeders.objects.all()
            })
        medicine_setting.save()
        return redirect('medicine_setting_detail', settingcode=medicine_setting.settingcode)

    return render(request, 'pages/poultry/hatchery/medicine_setting/details.html', {
        'medicine_setting': medicine_setting,
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
            available_quantity = item_request_quantity,
        )

        egg_setting.save()

        is_registered = register_egg_settings_history(egg_setting, item_request_item)

        if is_registered:
            messages.success(request, 'Egg Setting set successfully.', extra_tags='success')
            return redirect('egg_setting_list')
        else:
            item_request.delete()
            egg_setting.delete()

            messages.error(request, "Error registering on blockchain, Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/hatchery/egg_setting/create.html', {
                'errors': errors,
                'incubators': Incubators.objects.all(),
                'customers': Customer.objects.all(),
                'breeders': Breeders.objects.all(),
                'egg': Eggs.objects.all(),
                'items': Item.objects.filter(item_type__type_name="Egg"),
            })

    incubators = Incubators.objects.all()
    customers = Customer.objects.all()
    breeders = Breeders.objects.all()
    eggs = Eggs.objects.all()
    items = Item.objects.filter(item_type__type_name="Egg")

    
    return render(request, 'pages/poultry/hatchery/egg_setting/create.html', {
        'incubators': incubators,
        'customers': customers,
        'breeders': breeders,
        'egg':eggs,
        'items': items,
    })

@login_required
def feed_setting_create(request):
    errors = {}
    if request.method == 'POST':
        item_request_item_id = request.POST.get('item_request_item')
        item_request_quantity = request.POST.get('item_request_quantity')
        
        required_fields = ['item_request_item', 'item_request_quantity']
        for field in required_fields:
            if not request.POST.get(field):
                errors[field] = "* This Field is required"
                
        if item_request_item_id:
            item_request_item = get_object_or_404(Item, id=item_request_item_id)
            feed = Feeds.objects.filter(item=item_request_item).first()
        
            if item_request_quantity and int(item_request_quantity)> feed.received:
                errors['item_request_quantity'] = "Insufficient quantity of feeds available for the slected feed type."
            
        if errors:
            messages.error(request, "Error creating feed setting, Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/hatchery/feed_setting/create.html', {
                'errors': errors,
                'items': Item.objects.filter(item_type__type_name="Feed"),
            })
        
        item_request = ItemRequest(item=item_request_item, quantity=item_request_quantity, requested_by=request.user)
        item_request.save()

        feed_setting = FeedSetting(
            feed = feed,
            item_request = item_request,
            feeds = item_request_quantity,
            available_quantity = item_request_quantity,
        )

        feed_setting.save()

        is_registered = register_feed_settings_history(feed_setting, item_request_item)

        if is_registered:
            messages.success(request, 'Feed Setting set successfully.', extra_tags='success')
            return redirect('feed_setting_list')
        else:
            item_request.delete()
            feed_setting.delete()

            messages.error(request, "Error registering on blockchain, Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/hatchery/feed_setting/create.html', {
                'errors': errors,
                'items': items.objects.all(),
                'customers': Customer.objects.all(),
                'breeders': Breeders.objects.all(),
                'feed': feeds.objects.all(),
                'items': Item.objects.filter(item_type__type_name="Feed"),
            })

    items = Item.objects.filter(item_type__type_name="Feed")

    
    return render(request, 'pages/poultry/hatchery/feed_setting/create.html', {
        'items': items,
    })
def register_feed_settings_history(feed_setting, item):
        try:

            api_data = {
                    "tokenName": item.code,
                    "policyId": item.policyId,
                    "code": feed_setting.settingcode,
                    "blockfrostKey": os.getenv('blockfrostKey'),
                    "secretSeed": os.getenv('secretSeed'),
                    "cborHex": os.getenv('cborHex')
                }

            if os.getenv('data_encryption', 'False') == 'True':
                offchain_data = {
                    "feed_batch": split_string(encrypt_data(feed_setting.feed.batchnumber), "feed_batch"),
                    "item_code": split_string(encrypt_data(item.code), "item_code"),
                    "item_request_code": split_string(encrypt_data(feed_setting.item_request.code), "item_request_code"),
                    "item_request_requested_by": split_string(encrypt_data(feed_setting.item_request.requested_by.first_name), "item_request_requested_by"),
                    "item_request_quantity": split_string(encrypt_data(feed_setting.item_request.quantity), "item_request_quantity"),
                    "is_request_approved": split_string(encrypt_data(str(feed_setting.is_approved)), "is_request_approved"),
                }
                api_data['metadata'] = offchain_data
            else:
                api_data['metadata'] = {
                        "feed_batch": feed_setting.feed.batchnumber,
                        "item_code": item.code,
                        "item_request_code": feed_setting.item_request.code,
                        "item_request_requested_by": feed_setting.item_request.requested_by.first_name,
                        "item_request_quantity": feed_setting.item_request.quantity,
                        "is_request_approved": str(feed_setting.is_approved),
                        }


            response = requests.post(os.getenv('OFFCHAIN_BASE_URL')+'history', json=api_data, verify=False)
            response_data = response.json()
                        
            if response.status_code == 200 and 'status' in response_data:
                feed_setting.txHash = response_data['txHash']
                feed_setting.save()
                return True
            else:
                return False
        
        except requests.exceptions.RequestException as e:
            return False
        
@login_required
def medicine_setting_create(request):
    errors = {}
    if request.method == 'POST':
        item_request_item_id = request.POST.get('item_request_item')
        item_request_quantity = request.POST.get('item_request_quantity')
        
        required_fields = ['item_request_item', 'item_request_quantity']
        for field in required_fields:
            if not request.POST.get(field):
                errors[field] = "* This Field is required"
                
        if item_request_item_id:
            item_request_item = get_object_or_404(Item, id=item_request_item_id)
            medicine_inventory = MedicineInventory.objects.filter(item=item_request_item).first()
        
            if item_request_quantity and int(item_request_quantity)> medicine_inventory.stock_quantity:
                errors['item_request_quantity'] = "Insufficient quantity of medicines available for the slected medicine type."
            
        if errors:
            messages.error(request, "Error creating medicine setting, Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/hatchery/medicine_setting/create.html', {
                'errors': errors,
                'items': Item.objects.filter(item_type__type_name="Medicine"),
            })
        
        item_request = ItemRequest(item=item_request_item, quantity=item_request_quantity, requested_by=request.user)
        item_request.save()

        medicine_setting = MedicineSetting(
            medicine = medicine_inventory,
            item_request = item_request,
            medicines = item_request_quantity,
            available_quantity = item_request_quantity,
        )

        medicine_setting.save()

        is_registered = register_medicine_settings_history(medicine_setting, item_request_item)

        if is_registered:
            messages.success(request, 'Medicine Setting set successfully.', extra_tags='success')
            return redirect('medicine_setting_list')
        else:
            item_request.delete()
            medicine_setting.delete()

            messages.error(request, "Error registering on blockchain, Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/hatchery/medicine_setting/create.html', {
                'errors': errors,
                'items': Item.objects.filter(item_type__type_name="medicine"),
            })


    items = Item.objects.filter(item_type__type_name="Medicine")

    
    return render(request, 'pages/poultry/hatchery/medicine_setting/create.html', {
        'items': items,
    })

def register_medicine_settings_history(medicine_setting, item):
        try:

            api_data = {
                    "tokenName": item.code,
                    "policyId": item.policyId,
                    "code": medicine_setting.settingcode,
                    "blockfrostKey": os.getenv('blockfrostKey'),
                    "secretSeed": os.getenv('secretSeed'),
                    "cborHex": os.getenv('cborHex')
                }

            if os.getenv('data_encryption', 'False') == 'True':
                offchain_data = {
                    "medicine_batch": split_string(encrypt_data(medicine_setting.medicine.batchnumber), "medicine_batch"),
                    "item_code": split_string(encrypt_data(item.code), "item_code"),
                    "item_request_code": split_string(encrypt_data(medicine_setting.item_request.code), "item_request_code"),
                    "item_request_requested_by": split_string(encrypt_data(medicine_setting.item_request.requested_by.first_name), "item_request_requested_by"),
                    "item_request_quantity": split_string(encrypt_data(medicine_setting.item_request.quantity), "item_request_quantity"),
                    "is_request_approved": split_string(encrypt_data(str(medicine_setting.is_approved)), "is_request_approved"),
                }
                api_data['metadata'] = offchain_data
            else:
                api_data['metadata'] = {
                        "medicine_batch": medicine_setting.medicine.batchnumber,
                        "item_code": item.code,
                        "item_request_code": medicine_setting.item_request.code,
                        "item_request_requested_by": medicine_setting.item_request.requested_by.first_name,
                        "item_request_quantity": medicine_setting.item_request.quantity,
                        "is_request_approved": str(medicine_setting.is_approved),
                        }

            response = requests.post(os.getenv('OFFCHAIN_BASE_URL')+'history', json=api_data, verify=False)
            response_data = response.json()
                        
            if response.status_code == 200 and 'status' in response_data:
                medicine_setting.txHash = response_data['txHash']
                medicine_setting.save()
                return True
            else:
                return False
        
        except requests.exceptions.RequestException as e:
            return False
        
def register_egg_settings_history(egg_setting, item):
        try:

            api_data = {
                    "tokenName": item.code,
                    "policyId": item.policyId,
                    "code": egg_setting.settingcode,
                    "blockfrostKey": os.getenv('blockfrostKey'),
                    "secretSeed": os.getenv('secretSeed'),
                    "cborHex": os.getenv('cborHex')
                }

            if os.getenv('data_encryption', 'False') == 'True':
                offchain_data = {
                    "egg_batch": split_string(encrypt_data(egg_setting.egg.batchnumber), "egg_batch"),
                    "item_code": split_string(encrypt_data(item.code), "item_code"),
                    "item_request_code": split_string(encrypt_data(egg_setting.item_request.code), "item_request_code"),
                    "item_request_requested_by": split_string(encrypt_data(egg_setting.item_request.requested_by.first_name), "item_request_requested_by"),
                    "item_request_quantity": split_string(encrypt_data(egg_setting.item_request.quantity), "item_request_quantity"),
                    "is_request_approved": split_string(encrypt_data(str(egg_setting.is_approved)), "is_request_approved"),

                    "incubator": split_string(encrypt_data(egg_setting.incubator.code), "incubator"),
                    "breeders": split_string(encrypt_data(egg_setting.breeders.batch), "breeders"),
                }
                api_data['metadata'] = offchain_data
            else:
                api_data['metadata'] = {
                        "egg_batch": egg_setting.egg.batchnumber,
                        "item_code": item.code,
                        "item_request_code": egg_setting.item_request.code,
                        "item_request_requested_by": egg_setting.item_request.requested_by.first_name,
                        "item_request_quantity": egg_setting.item_request.quantity,
                        "is_request_approved": str(egg_setting.is_approved),

                        "incubator": egg_setting.incubator.code,
                        "breeders": egg_setting.breeders.batch,
                        }

            response = requests.post(os.getenv('OFFCHAIN_BASE_URL')+'history', json=api_data, verify=False)
            response_data = response.json()
                        
            if response.status_code == 200 and 'status' in response_data:
                egg_setting.txHash = response_data['txHash']
                egg_setting.save()
                return True
            else:
                return False
        
        except requests.exceptions.RequestException as e:
            return False
        
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
def feed_setting_update(request, settingcode):
    feed_setting = get_object_or_404(feedSetting, settingcode=settingcode)
    errors={}
    if request.method == 'POST':
        if feed_setting.is_approved:
            messages.success(request, "feed Setting request is already approved ", extra_tags='danger')
            return redirect('feed_setting_detail', settingcode=feed_setting.settingcode)
        feed_setting.settingcode = request.POST.get('settingcode', feed_setting.settingcode)
        feed_setting.incubator = get_object_or_404(Incubators, id=request.POST.get('incubator'))
        feed_setting.breeders = get_object_or_404(Breeders, id=request.POST.get('breeders'))
        if request.POST.get('feeds'):
            if feed_setting.feeds == int(request.POST.get('feeds')):
                pass
            elif feed_setting.item_request.item.quantity < int(request.POST.get('feeds')):
                errors['feeds'] = "Insufficient quantity of feeds available for the slected feed type."
                
            feed_setting.feeds = int(request.POST.get('feeds'))
            feed_setting.item_request.quantity = int(request.POST.get('feeds'))
            feed_setting.item_request.save()
        else:
            feed_setting.feeds = feed_setting.feeds
            
        if errors:
            messages.error(request, "Updating feed setting failed: Please double-check your entries and try again.")
            return render(request, 'pages/poultry/hatchery/feed_setting/details.html', {
                'feed_setting': feed_setting,
                'errors': errors,
                'incubators': Incubators.objects.all(),
                'customers': Customer.objects.all(),
                'breeders': Breeders.objects.all()
            })
        feed_setting.save()
        return redirect('feed_setting_detail', settingcode=feed_setting.settingcode)

    incubators = Incubators.objects.all()
    customers = Customer.objects.all()
    breeders = Breeders.objects.all()
    return render(request, 'pages/poultry/hatchery/feed_setting/details.html', {
        'feed_setting': feed_setting,
        'incubators': incubators,
        'customers': customers,
        'breeders': breeders
    })

@login_required
def medicine_setting_update(request, settingcode):
    feed_setting = get_object_or_404(feedSetting, settingcode=settingcode)
    errors={}
    if request.method == 'POST':
        if feed_setting.is_approved:
            messages.success(request, "feed Setting request is already approved ", extra_tags='danger')
            return redirect('feed_setting_detail', settingcode=feed_setting.settingcode)
        feed_setting.settingcode = request.POST.get('settingcode', feed_setting.settingcode)
        feed_setting.incubator = get_object_or_404(Incubators, id=request.POST.get('incubator'))
        feed_setting.breeders = get_object_or_404(Breeders, id=request.POST.get('breeders'))
        if request.POST.get('feeds'):
            if feed_setting.feeds == int(request.POST.get('feeds')):
                pass
            elif feed_setting.item_request.item.quantity < int(request.POST.get('feeds')):
                errors['feeds'] = "Insufficient quantity of feeds available for the slected feed type."
                
            feed_setting.feeds = int(request.POST.get('feeds'))
            feed_setting.item_request.quantity = int(request.POST.get('feeds'))
            feed_setting.item_request.save()
        else:
            feed_setting.feeds = feed_setting.feeds
            
        if errors:
            messages.error(request, "Updating feed setting failed: Please double-check your entries and try again.")
            return render(request, 'pages/poultry/hatchery/feed_setting/details.html', {
                'feed_setting': feed_setting,
                'errors': errors,
                'incubators': Incubators.objects.all(),
                'customers': Customer.objects.all(),
                'breeders': Breeders.objects.all()
            })
        feed_setting.save()
        return redirect('feed_setting_detail', settingcode=feed_setting.settingcode)

    incubators = Incubators.objects.all()
    customers = Customer.objects.all()
    breeders = Breeders.objects.all()
    return render(request, 'pages/poultry/hatchery/feed_setting/details.html', {
        'feed_setting': feed_setting,
        'incubators': incubators,
        'customers': customers,
        'breeders': breeders
    })

@login_required
def medicine_setting_delete(request, settingcode):
    medicine_setting = get_object_or_404(medicineSetting, settingcode=settingcode)
    if request.method == 'POST':
        if Incubation.objects.filter(medicinesetting=medicine_setting.id).exists():
            messages.error(request, "Cannot delete Incubation associated with existing medicine Setting.", extra_tags='danger')
            return redirect('medicine_setting_list')
        medicine_setting.delete()
        item_request = ItemRequest.objects.filter(id=medicine_setting.item_request.id).first()
        item = get_object_or_404(Item, code=item_request.item.code)
        item.quantity += item_request.quantity
        item.save()
        if medicines.objects.filter(item=item_request.item).exists():
            medicines = medicines.objects.filter(item=item_request.item)
            for medicine in medicines:
                medicine.received += item_request.quantity
                medicine.save()
        item_request.delete()
        messages.success(request, 'medicine Setting deleted successfully.', extra_tags='success')
        return redirect('medicine_setting_list')
    return render(request, 'medicine_settings/medicine_setting_confirm_delete.html', {'medicine_setting': medicine_setting})


@login_required
def feed_setting_delete(request, settingcode):
    feed_setting = get_object_or_404(feedSetting, settingcode=settingcode)
    if request.method == 'POST':
        if Incubation.objects.filter(feedsetting=feed_setting.id).exists():
            messages.error(request, "Cannot delete Incubation associated with existing feed Setting.", extra_tags='danger')
            return redirect('feed_setting_list')
        feed_setting.delete()
        item_request = ItemRequest.objects.filter(id=feed_setting.item_request.id).first()
        item = get_object_or_404(Item, code=item_request.item.code)
        item.quantity += item_request.quantity
        item.save()
        if feeds.objects.filter(item=item_request.item).exists():
            feeds = feeds.objects.filter(item=item_request.item)
            for feed in feeds:
                feed.received += item_request.quantity
                feed.save()
        item_request.delete()
        messages.success(request, 'feed Setting deleted successfully.', extra_tags='success')
        return redirect('feed_setting_list')
    return render(request, 'feed_settings/feed_setting_confirm_delete.html', {'feed_setting': feed_setting})


@login_required
def egg_setting_delete(request, settingcode):
    egg_setting = get_object_or_404(EggSetting, settingcode=settingcode)
    if request.method == 'POST':
        if Incubation.objects.filter(eggsetting=egg_setting.id).exists():
            messages.error(request, "Cannot delete Incubation associated with existing Egg Setting.", extra_tags='danger')
            return redirect('egg_setting_list')
        egg_setting.delete()
        item_request = ItemRequest.objects.filter(id=egg_setting.item_request.id).first()
        item = get_object_or_404(Item, code=item_request.item.code)
        item.quantity += item_request.quantity
        item.save()
        if Eggs.objects.filter(item=item_request.item).exists():
            eggs = Eggs.objects.filter(item=item_request.item)
            for egg in eggs:
                egg.received += item_request.quantity
                egg.save()
        item_request.delete()
        messages.success(request, 'Egg Setting deleted successfully.', extra_tags='success')
        return redirect('egg_setting_list')
    return render(request, 'egg_settings/egg_setting_confirm_delete.html', {'egg_setting': egg_setting})


@login_required
def incubation_list(request):
    incubations = Incubation.objects.all().order_by('-created')
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
    candling = Candling.objects.filter(incubation=incubation).exists()
    errors = {}
    if request.method == 'POST':
        try:
            incubation.eggsetting = EggSetting.objects.get(id=request.POST.get('eggsetting'))
            incubation.breeders = Breeders.objects.get(id=request.POST.get('breeders'))
        except (EggSetting.DoesNotExist, Breeders.DoesNotExist):
            errors['selection'] = "Invalid selection for egg setting or breeders."
        
        eggs = request.POST.get('eggs')
        if eggs:
            try:
                eggs = int(eggs)
                if eggs > incubation.eggsetting.eggs:
                    errors['eggs'] = "Insufficient quantity of eggs available for the selected egg setting."
            except ValueError:
                errors['eggs'] = "Please enter a valid number of eggs."

            if not errors and eggs < incubation.eggsetting.eggs:
                incubation.eggsetting.available_quantity = incubation.eggsetting.eggs - eggs
                incubation.eggsetting.save()
                incubation.eggs = eggs
        
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
        'candling': candling
    }
    return render(request, 'pages/poultry/hatchery/incubation/details.html', context)

## Create View
@login_required
def incubation_create(request):
    errors = {}
    egg_settings = EggSetting.objects.filter(is_approved=True, available_quantity__gte=1)
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
            if eggs and int(eggs) > int(eggsetting.available_quantity if eggsetting.available_quantity else 0):
                errors['eggs'] = "Insufficient quantity of eggs available for the slected egg setting."
        
        context = {
            'egg_settings': egg_settings,
            'customers': customers,
            'breeders': breeders,
            'errors':errors
        }    
        if errors:
            messages.error(request, "Creating incubation failed: Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/hatchery/incubation/create.html', context)
        
        eggsetting=EggSetting.objects.get(id=eggsetting_id)   
        incubation = Incubation(
            eggsetting=eggsetting,
            breeders=eggsetting.breeders,
            eggs=eggs
        )
        incubation.save()
        eggsetting.available_quantity -= int(eggs)
        eggsetting.save()

        is_registered = register_incubation_history(incubation, eggsetting)

        if not is_registered:
            eggsetting.available_quantity += int(eggs)
            eggsetting.save()
            messages.error(request, "Recording on blockchain failed: Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/hatchery/incubation/create.html', context)

        messages.success(request, "Incubation saved successfully", extra_tags='success')
        return redirect('incubation_list')

    context = {
        'egg_settings': egg_settings,
        'customers': customers,
        'breeders': breeders,
    }

    return render(request, 'pages/poultry/hatchery/incubation/create.html', context)

def register_incubation_history(incubation, eggsetting):
    try:
        api_data = {
                "tokenName": eggsetting.item_request.item.code,
                "policyId": eggsetting.item_request.item.policyId,
                "code": incubation.incubationcode,
                "blockfrostKey": os.getenv('blockfrostKey'),
                "secretSeed": os.getenv('secretSeed'),
                "cborHex": os.getenv('cborHex')
            }


        if os.getenv('data_encryption', 'False') == 'True':
            offchain_data = {
                "eggsetting": split_string(encrypt_data(eggsetting.settingcode), "eggsetting"),
                "eggs_quantity": split_string(encrypt_data(str(incubation.eggs)), "eggs_quantity"), 
            }
            api_data['metadata'] = offchain_data
        else:
            api_data['metadata'] = {
                "eggsetting": eggsetting.settingcode,
                "eggs_quantity": incubation.eggs,
                }
        response = requests.post(os.getenv('OFFCHAIN_BASE_URL')+'history', json=api_data, verify=False)
        response_data = response.json()

        if response.status_code == 200 and 'status' in response_data:
            incubation.txHash = response_data['txHash']
            incubation.save()
            return True
        else:
            return False
    
    except requests.exceptions.RequestException as e:
        return False
        
## Update View
@login_required
def incubation_update(request, incubationcode):
    incubation = get_object_or_404(Incubation, incubationcode=incubationcode)
    candling = Candling.objects.filter(incubation=incubation).exists()
    errors = {}
    if request.method == 'POST':
        try:
            incubation.eggsetting = EggSetting.objects.get(id=request.POST.get('eggsetting'))
            incubation.breeders = Breeders.objects.get(id=request.POST.get('breeders'))
        except (EggSetting.DoesNotExist, Breeders.DoesNotExist):
            errors['selection'] = "Invalid selection for egg setting or breeders."
        
        eggs = request.POST.get('eggs')
        if eggs:
            try:
                eggs = int(eggs)
                if eggs > incubation.eggsetting.eggs:
                    errors['eggs'] = "Insufficient quantity of eggs available for the selected egg setting."
            except ValueError:
                errors['eggs'] = "Please enter a valid number of eggs."

            if not errors and eggs < incubation.eggsetting.eggs:
                incubation.eggsetting.available_quantity = incubation.eggsetting.eggs - eggs
                incubation.eggsetting.save()
                incubation.eggs = eggs
        
        if errors:
            messages.error(request, "Updating incubation failed: Please double-check your entries and try again.", extra_tags='danger')
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
        'candling': candling
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


            is_registered = register_candling_history(candling, incubation)

            if not is_registered:
                candling.delete()

                messages.error(request, "Error registering on blockchain, Please double-check your entries and try again.", extra_tags="danger")
                context = {
                    'incubations': Incubation.objects.filter(eggsetting__is_approved=True).exclude(candling_incubation__isnull=False),
                    'customers': Customer.objects.all(),
                    'breeders': Breeders.objects.all(),
                    "errors": errors,
                    'today': datetime.datetime.now().date().strftime('%Y-%m-%d'),
                }
                return render(request, 'pages/poultry/hatchery/candling/create.html', context=context)

                
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


def register_candling_history(candling, incubation):
    try:
        api_data = {
                "tokenName": incubation.eggsetting.item_request.item.code,
                "policyId": incubation.eggsetting.item_request.item.policyId,
                "code": candling.candlingcode,
                "blockfrostKey": os.getenv('blockfrostKey'),
                "secretSeed": os.getenv('secretSeed'),
                "cborHex": os.getenv('cborHex')
            }

        if os.getenv('data_encryption', 'False') == 'True':
            offchain_data = {
                "candled_date": split_string(encrypt_data(candling.candled_date), "candled_date"),
                "eggs": split_string(encrypt_data(str(incubation.eggs)), "eggs"),
                "fertile_eggs": split_string(encrypt_data(str(int(incubation.eggs) - int(candling.spoilt_eggs))), "fertile_eggs"),
                "incubation": split_string(encrypt_data(incubation.incubationcode), "incubation"),
                "spoilt_eggs": split_string(encrypt_data(str(candling.spoilt_eggs)), "spoilt_eggs"),
            }
            api_data['metadata'] = offchain_data
        else:
            api_data['metadata'] = {
                "candled_date": candling.candled_date,
                "eggs": incubation.eggs,
                "fertile_eggs": int(incubation.eggs) - int(candling.spoilt_eggs),
                "incubation": incubation.incubationcode,
                "spoilt_eggs": int(candling.spoilt_eggs),
                }

        response = requests.post(os.getenv('OFFCHAIN_BASE_URL')+'history', json=api_data, verify=False)
        response_data = response.json()

        if response.status_code == 200 and 'status' in response_data:
            candling.txHash = response_data['txHash']
            candling.save()
            return True
        else:
            return False
    
    except requests.exceptions.RequestException as e:
        return False
        
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
        

            txHash = register_hatching_history(hatching, candling, item, chick)
            
            chick_txHash = None
            utxo = None
            
            if txHash:
                utxo = check_utxo_status(txHash)

            if utxo:
                if os.getenv('data_encryption', 'False') == 'True':
                    metadata = {
                        "item_type": split_string(encrypt_data(item.item_type.type_name), "item_type"),
                        "batchnumber": split_string(encrypt_data(chick.batchnumber), "batchnumber"),
                        "source": split_string(encrypt_data(chick.source), "source"),
                        "hatching_code": split_string(encrypt_data(hatching.hatchingcode), "hatching_code"),
                        "breed": split_string(encrypt_data(chick.breed.code), "breed"),
                        "breed_type": split_string(encrypt_data(chick.breed.breed), "breed_type"),
                        "quantity": split_string(encrypt_data(str(hatching.chicks_hatched)), "quantity"),
                        "old_item_code": split_string(encrypt_data(candling.incubation.eggsetting.item_request.item.code), "old_item_code"),
                        "old_item_policyID": split_string(encrypt_data(candling.incubation.eggsetting.item_request.item.policyId), "old_item_policyID"),
                        "old_item_txHash": split_string(encrypt_data(candling.incubation.eggsetting.item_request.item.txHash), "old_item_txHash"),
                        }
                else:
                    metadata = {
                        "item_type": item.item_type.type_name,
                        "batchnumber": chick.batchnumber,
                        "source": chick.source,
                        "hatching_code": hatching.hatchingcode,
                        "breed": chick.breed.code,
                        "breed_type": chick.breed.breed,
                        "quantity": str(hatching.chicks_hatched),
                        "old_item_code": candling.incubation.eggsetting.item_request.item.code,
                        "old_item_policyID": candling.incubation.eggsetting.item_request.item.policyId,
                        "old_item_txHash": candling.incubation.eggsetting.item_request.item.txHash,
                        }
                chick_txHash = mint_chicks_item(item, metadata)


            if not txHash or not chick_txHash:
                hatching.delete()
                item.delete()
                chick.delete()
        
                messages.error(request, "Error registering on blockchain: Please double-check your entries and try again.", extra_tags="danger")
                context = {
                    'candlings': Candling.objects.exclude(hatching_candling__isnull=False),
                    'customers': Customer.objects.all(),
                    'breeders': Breeders.objects.all(),
                    'errors': errors,
                }
                return render(request, 'pages/poultry/hatchery/hatching/create.html', context=context)

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


def check_utxo_status(txHash, retries=10, wait_time=10):
    for attempt in range(retries):
        try:

            api_data = {
                    "blockfrostKey": os.getenv('blockfrostKey'),
                    "secretSeed": os.getenv('secretSeed'),
                    "txHash": txHash,
                }
            response = requests.post(os.getenv('OFFCHAIN_BASE_URL')+'utxo-status', json=api_data, verify=False)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ready":
                    print("UTxO is ready for the next transaction.")
                    
                    time.sleep(wait_time)
                    return True
                else:
                    print(f"Attempt {attempt + 1}/{retries}: UTxO is not ready. Retrying in {wait_time} seconds...")
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
        
        time.sleep(wait_time)

    print("UTxO is still not ready after maximum retries.")
    return None


def register_hatching_history(hatching, candling, new_item, new_chick):
    try:
        api_data = {
                "tokenName": candling.incubation.eggsetting.item_request.item.code,
                "policyId": candling.incubation.eggsetting.item_request.item.policyId,
                "code": hatching.hatchingcode,
                "blockfrostKey": os.getenv('blockfrostKey'),
                "secretSeed": os.getenv('secretSeed'),
                "cborHex": os.getenv('cborHex')
            }


        if os.getenv('data_encryption', 'False') == 'True':
            offchain_data = {
                "breeders": split_string(encrypt_data(hatching.breeders.batch), "breeders"),
                "hatched": split_string(encrypt_data(str(hatching.hatched)), "hatched"),
                "deformed": split_string(encrypt_data(str(hatching.deformed)), "deformed"),
                "spoilt_eggs": split_string(encrypt_data(str(hatching.spoilt)), "spoilt_eggs"),
                "chicks_hatched": split_string(encrypt_data(str(int(hatching.hatched) - int(hatching.deformed) - int(hatching.spoilt))), "chicks_hatched"),
                "new_chicks_batchnumber": split_string(encrypt_data(str(new_chick.batchnumber)), "new_chicks_batchnumber"),
                "new_item_code": split_string(encrypt_data(new_item.code), "new_item_code"),
            }
            api_data['metadata'] = offchain_data
        else:
            api_data['metadata'] = {
                "breeders": hatching.breeders.batch,
                "hatched": str(hatching.hatched),
                "deformed": str(hatching.deformed),
                "spoilt_eggs": str(hatching.spoilt),
                "chicks_hatched": str(int(hatching.hatched) - int(hatching.deformed) - int(hatching.spoilt)),
                "new_chicks_batchnumber": new_chick.batchnumber,
                "new_item_code": new_item.code,
                }

        response = requests.post(os.getenv('OFFCHAIN_BASE_URL')+'history', json=api_data, verify=False)
        response_data = response.json()

        if response.status_code == 200 and 'status' in response_data:
            hatching.txHash = response_data['txHash']
            hatching.save()
            return response_data['txHash']
        else:
            return False
    
    except requests.exceptions.RequestException as e:
        return False
        
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
    egg_setting_id = request.GET.get('egg_setting_id')
    incubation_id = request.GET.get('incubation_id')

    if tracker_type == 'egg':
        egg = tracker.egg
        egg_settings = EggSetting.objects.filter(egg=egg)
        egg_setting = egg_settings.filter(id=egg_setting_id).first() if egg_setting_id else egg_settings.first()
        incubations = Incubation.objects.filter(eggsetting=egg_setting) if egg_setting else Incubation.objects.none()
        incubation = incubations.filter(id=incubation_id).first() if incubation_id else incubations.first()
        candling = Candling.objects.filter(incubation=incubation).first() if incubation else None
        hatching = Hatching.objects.filter(candling=candling).first() if candling else None
        chicks = Chicks.objects.filter(hatching=hatching) if hatching else []

        return render(request, 'pages/poultry/tracker-details.html', {
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
        incubations = Incubation.objects.filter(eggsetting=egg_setting) if egg_setting else Incubation.objects.none()
        incubation = incubations.filter(id=incubation_id).first() if incubation_id else incubations.first()
        candling = Candling.objects.filter(incubation=incubation).first() if incubation else None
        hatching = Hatching.objects.filter(candling=candling).first() if candling else None
        chicks = Chicks.objects.filter(hatching=hatching) if hatching else []

        return render(request, 'pages/poultry/tracker-details.html', {
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
