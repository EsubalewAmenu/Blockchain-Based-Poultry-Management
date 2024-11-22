from django.db import DataError, IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import *
from django.urls import reverse
from .forms import BreedersForm
import requests
import os

@login_required
def breed_list(request):
    breeds_list = Breed.objects.all()
    paginator = Paginator(breeds_list, 10)
    
    page_number = request.GET.get('page')
    breeds = paginator.get_page(page_number)
    
    return render(request, 'pages/poultry/breeds/list.html', {'breeds': breeds})


@login_required
def breed_detail(request, code):
    breed = get_object_or_404(Breed, code=code)
    errors = {}
    if request.method == 'POST':
        try:
            breed.code = request.POST.get('code', breed.code)
            breed.poultry_type = request.POST.get('poultry_type', breed.poultry_type)
            breed.breed = request.POST.get('breed', breed.breed)
            breed.purpose = request.POST.get('purpose', breed.purpose)
            breed.eggs_year = request.POST.get('eggs_year', breed.eggs_year)
            breed.adult_weight = request.POST.get('adult_weight', breed.adult_weight)
            breed.description = request.POST.get('description', breed.description)
            
            allowed_image_types = ['image/jpeg', 'image/png']
            
            if breed.eggs_year and int(breed.eggs_year) < 0:
                errors['eggs_per_year'] = 'Eggs per year must be a positive integer.'
            
            if breed.adult_weight and float(breed.adult_weight) < 0:
                errors['adult_weight'] = 'Adult weight must be a positive number.'

            if request.FILES.get('front_photo'):
                if request.FILES.get('front_photo').content_type not in allowed_image_types:
                    errors['front_photo'] = 'Invalid image format for front photo. Only JPEG or PNG is allowed.'

            if request.FILES.get('side_photo'):
                if request.FILES.get('side_photo').content_type not in allowed_image_types:
                    errors['side_photo'] = 'Invalid image format for side photo. Only JPEG or PNG is allowed.'


            if request.FILES.get('back_photo'):
                if request.FILES.get('back_photo').content_type not in allowed_image_types:
                    errors['back_photo'] = 'Invalid image format for back photo. Only JPEG or PNG is allowed.'
            
            if errors:
                messages.error(request, f"Updating breed failed: Please double-check your entries and try again.", extra_tags='danger')
                return render(request, 'pages/poultry/breeds/edit.html', {'errors': errors})
                
            if request.FILES.get('front_photo'):
                breed.front_photo = request.FILES.get('front_photo')
            if request.FILES.get('side_photo'):
                breed.side_photo = request.FILES.get('side_photo')
            if request.FILES.get('back_photo'):
                
                breed.back_photo = request.FILES.get('back_photo')
            breed.save()
            messages.success(request, 'Breed updated successfully.', extra_tags='success')
        except Exception as e:
            messages.error(request, f'Error updating breed: {str(e)}', extra_tags='danger')
            return redirect('breed_update')
        return redirect('breed_list')
    
    return render(request, 'pages/poultry/breeds/details.html', {'breed': breed})

@login_required
def breed_create(request):
    errors = {}
    if request.method == 'POST':
        poultry_type = request.POST.get('poultry_type')
        breed_name = request.POST.get('breed_name')
        purpose = request.POST.get('purpose')
        eggs_year = request.POST.get('eggs_per_year')
        adult_weight = request.POST.get('adult_weight')
        description = request.POST.get('description')
        front_photo = request.FILES.get('front_photo')
        side_photo = request.FILES.get('side_photo')
        back_photo = request.FILES.get('back_photo')
        
        required_fields = ['breed_name', 'purpose', 'eggs_per_year', 'adult_weight', 'poultry_type']
        required_file_fields = ['front_photo', 'side_photo', 'back_photo']
        
        for field in required_fields:
            if not request.POST.get(field):
                errors[field] = '* This field is required.'
                
        for field in required_file_fields:
            if not request.FILES.get(field):
                errors[field] = '* This field is required.'
                
        
        allowed_image_types = ['image/jpeg', 'image/png']
        
        if eggs_year and int(eggs_year) < 0:
            errors['eggs_per_year'] = 'Eggs per year must be a positive integer.'
            
        if adult_weight and float(adult_weight) < 0:
            errors['adult_weight'] = 'Adult weight must be a positive number.'
            
        if breed_name:
            if Breed.objects.filter(breed=breed_name).exists():
                errors['breed_name'] = 'Breed name already exists.'
        if front_photo:
            if front_photo.content_type not in allowed_image_types:
                errors['front_photo'] = 'Invalid image format for front photo. Only JPEG or PNG is allowed.'

        if side_photo:
            if side_photo.content_type not in allowed_image_types:
                errors['side_photo'] = 'Invalid image format for side photo. Only JPEG or PNG is allowed.'


        if back_photo:
            if back_photo.content_type not in allowed_image_types:
                errors['back_photo'] = 'Invalid image format for back photo. Only JPEG or PNG is allowed.'
        
        if errors:
            messages.error(request, f"Creating breed failed: Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/breeds/create.html', {'errors': errors})
        try:
            breed = Breed.objects.create(
                poultry_type=poultry_type,
                breed=breed_name,
                purpose=purpose,
                eggs_year=eggs_year,
                adult_weight=adult_weight,
                description=description,
                front_photo=front_photo,
                side_photo=side_photo,
                back_photo=back_photo
            )
            breed.save()

            is_minted = mint_breed(breed)
            
            if not is_minted:
                breed.delete()

                messages.error(request, f"Creating breed failed: Please double-check your entries and try again.", extra_tags='danger')
                return render(request, 'pages/poultry/breeds/create.html', {'errors': errors})


            messages.success(request, 'Breed has been created successfully', extra_tags='success')
        except IntegrityError as e:
            messages.error(request, f'Error creating breed: {str(e)}', extra_tags='danger')
            return render(request, 'pages/poultry/breeds/create.html', {'errors': errors})
        except DataError as e:
            messages.error(request, f'Error creating breed: {str(e)}', extra_tags='danger')
            return render(request, 'pages/poultry/breeds/create.html', {'errors': errors})
        except Exception as e:
            messages.error(request, f'Error creating breed: {str(e)}', extra_tags='danger')
            return render(request, 'pages/poultry/breeds/create.html', {'errors': errors})
        return redirect('breed_list')
    
    return render(request, 'pages/poultry/breeds/create.html')


def mint_breed(breed):
    try:
        api_data = {
                "tokenName": breed.code,
                "metadata": {
                    "poultry_type": breed.poultry_type,
                    "breed": breed.breed,
                    "purpose": breed.purpose,
                    "eggs_year": breed.eggs_year,
                    "adult_weight": breed.adult_weight,
                    "description": breed.description,
                    },
                "blockfrostKey": os.getenv('blockfrostKey'),
                "secretSeed": os.getenv('secretSeed'),
                "cborHex": os.getenv('cborHex')
            }

        response = requests.post(os.getenv('OFFCHAIN_BASE_URL')+'mint', json=api_data)
        response_data = response.json()
        print(response_data)
        if response.status_code == 200 and 'status' in response_data:
            print(response_data['txHash'])
            breed.txHash = response_data['txHash']
            breed.policyId = response_data['policyId']
            breed.save()
            return True
        else:
            return JsonResponse({'error': 'Unexpected API response'}, status=400)
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return JsonResponse({'error': 'Failed to communicate with the external API'}, status=500)
        


@login_required
def breed_update(request, code):
    breed = get_object_or_404(Breed, code=code)
    errors = {}
    if request.method == 'POST':
        try:
            breed.code = request.POST.get('code', breed.code)
            breed.poultry_type = request.POST.get('poultry_type', breed.poultry_type)
            breed.breed = request.POST.get('breed', breed.breed)
            breed.purpose = request.POST.get('purpose', breed.purpose)
            breed.eggs_year = request.POST.get('eggs_year', breed.eggs_year)
            breed.adult_weight = request.POST.get('adult_weight', breed.adult_weight)
            breed.description = request.POST.get('description', breed.description)
            
            allowed_image_types = ['image/jpeg', 'image/png']
            
            if breed.eggs_year and int(breed.eggs_year) < 0:
                errors['eggs_per_year'] = 'Eggs per year must be a positive integer.'
            
            if breed.adult_weight and float(breed.adult_weight) < 0:
                errors['adult_weight'] = 'Adult weight must be a positive number.'

            if request.FILES.get('front_photo'):
                if request.FILES.get('front_photo').content_type not in allowed_image_types:
                    errors['front_photo'] = 'Invalid image format for front photo. Only JPEG or PNG is allowed.'

            if request.FILES.get('side_photo'):
                if request.FILES.get('side_photo').content_type not in allowed_image_types:
                    errors['side_photo'] = 'Invalid image format for side photo. Only JPEG or PNG is allowed.'


            if request.FILES.get('back_photo'):
                if request.FILES.get('back_photo').content_type not in allowed_image_types:
                    errors['back_photo'] = 'Invalid image format for back photo. Only JPEG or PNG is allowed.'
            
            if errors:
                messages.error(request, f"Updating breed failed: Please double-check your entries and try again.", extra_tags='danger')
                return render(request, 'pages/poultry/breeds/edit.html', {'errors': errors})
                
            if request.FILES.get('front_photo'):
                breed.front_photo = request.FILES.get('front_photo')
            if request.FILES.get('side_photo'):
                breed.side_photo = request.FILES.get('side_photo')
            if request.FILES.get('back_photo'):
                
                breed.back_photo = request.FILES.get('back_photo')
            breed.save()
            messages.success(request, 'Breed updated successfully.', extra_tags='success')
        except Exception as e:
            messages.error(request, f'Error updating breed: {str(e)}', extra_tags='danger')
            return redirect('breed_update')
        return redirect('breed_list')
    
    return render(request, 'pages/poultry/breeds/edit.html', {'breed': breed})

@login_required
def breed_delete(request, code):
    breed = get_object_or_404(Breed, code=code)

    if request.method == 'POST':
        breed.delete()
        messages.success(request, 'Breed deleted successfully.')
        return redirect('breed_list')
    
    return redirect('breed_list')


# List View
@login_required
def breeders_list(request):
    breeders_list = Breeders.objects.all()
    paginator = Paginator(breeders_list, 10)
    
    page_number = request.GET.get('page')
    breeders = paginator.get_page(page_number)
    
    return render(request, 'pages/poultry/breeders/list.html', {'breeders': breeders})

# Detail View
@login_required
def breeders_detail(request, batch):
    breeder = get_object_or_404(Breeders, batch=batch)
    errors = {}
    if request.method == 'POST':
        try:
            breeder.batch = request.POST.get('batch', breeder.batch)
            breed = request.POST.get('breed')
            if breed:
                breeder.breed = get_object_or_404(Breed, breed=breed, pk=1)
            else:
                breeder.breed=breeder.breed
            breeder.hens = request.POST.get('hens', breeder.hens)
            breeder.cocks = request.POST.get('cocks', breeder.cocks)
            breeder.mortality = request.POST.get('mortality', breeder.mortality)
            breeder.butchered = request.POST.get('butchered', breeder.butchered)
            breeder.sold = request.POST.get('sold', breeder.sold)
            breeder.current_number = request.POST.get('current_number', breeder.current_number)
            allowed_image_types = ['image/jpeg', 'image/png']
            
            if breeder.cocks and int(breeder.cocks) < 0:
                errors['cocks'] = '* Number of cocks must be a valid number.'
        
            if breeder.hens and int(breeder.hens) < 0:
                errors['hens'] = '* Number of hens must be a valid number.'
            
            if breeder.mortality and int(breeder.mortality) < 0:
                errors['mortality'] = '* Mortality rate must be a valid number.'
                
            if breeder.butchered and int(breeder.butchered) < 0:
                errors['butchered'] = '* Butchered rate must be a valid number.'
                
            if breeder.sold and int(breeder.sold) < 0:
                errors['sold'] = '* Sold rate must be a valid number.'
                
            if breeder.butchered and int(breeder.butchered) > int(breeder.hens) + int(breeder.cocks):
                errors['butchered'] = '* Butchered rate cannot be greater than total hens and cocks.'
                
            if breeder.sold and int(breeder.sold) > int(breeder.hens) + int(breeder.cocks):
                errors['sold'] = '* Sold rate cannot be greater than total hens and cocks.'
                
            if breeder.sold and breeder.butchered:
                if int(breeder.sold) + int(breeder.butchered) > int(breeder.hens) + int(breeder.cocks):
                    errors['sold'] = '* Sold rate cannot be greater than total hens and cocks if butchered rate is also provided.'
                    errors['butchered'] = '* butchered rate cannot be greater than total hens and cocks if sold rate is also provided.'

            if request.FILES.get('hens_photo'):
                if request.FILES.get('hens_photo').content_type not in allowed_image_types:
                    errors['hens_photo'] = 'Invalid image format for hens photo. Only JPEG or PNG is allowed.'
                breeder.hens_photo = request.FILES['hens_photo']
            if request.FILES.get('cocks_photo'):
                if request.FILES.get('cocks_photo').content_type not in allowed_image_types:
                    errors['cocks_photo'] = 'Invalid image format for cocks photo. Only JPEG or PNG is allowed.'
                breeder.cocks_photo = request.FILES['cocks_photo']
                
            if errors:
                messages.error(request, f"Updating breeder failed: Please double-check your entries and try again.", extra_tags='danger')
                return render(request, 'pages/poultry/breeders/details.html', {'breeder': breeder, 'errors': errors, 'breeds':Breed.objects.all()})

            breeder.save()
        except Exception as e:
            
            messages.error(request, f'Error updating breeder: {str(e)}', extra_tags='danger')
        return render(request, 'pages/poultry/breeders/details.html', {'breeder': breeder, 'errors': errors, 'breeds':Breed.objects.all()})

    return render(request, 'pages/poultry/breeders/details.html', {'breeder': breeder,  'breeds':Breed.objects.all()})

# Create View
@login_required
def breeders_create(request):
    breeds = Breed.objects.all()
    errors = {}

    if request.method == 'POST':
        breed_id = request.POST.get('breed')
        breed = Breed.objects.get(id=breed_id) if breed_id else None
        hens = request.POST.get('hens')
        cocks = request.POST.get('cocks')
        mortality = request.POST.get('mortality')
        butchered = request.POST.get('butchered')
        sold = request.POST.get('sold')
        hens_photo = request.FILES.get('hens_photo')
        cocks_photo = request.FILES.get('cocks_photo')
        
        required_fields = ['breed', 'cocks', 'hens']
        required_file_fields = ['hens_photo', 'cocks_photo']
        
        
        for field in required_fields:
            if not request.POST.get(field):
                errors[field] = '* This Field is required.'
            
        for file_field in required_file_fields:
            if not request.FILES.get(file_field):
                errors[file_field] = '* This Field is required'

        if cocks and int(cocks) < 0:
            errors['cocks'] = '* Number of cocks must be a valid number.'
        
        if hens and int(hens) < 0:
            errors['hens'] = '* Number of hens must be a valid number.'
        
        if mortality and int(mortality) < 0:
            errors['mortality'] = '* Mortality rate must be a valid number.'
            
        if butchered and int(butchered) < 0:
            errors['butchered'] = '* Butchered rate must be a valid number.'
            
        if sold and int(sold) < 0:
            errors['sold'] = '* Sold rate must be a valid number.'
            
        if butchered and int(butchered) > int(hens) + int(cocks):
            errors['butchered'] = '* Butchered rate cannot be greater than total hens and cocks.'
            
        if sold and int(sold) > int(hens) + int(cocks):
            errors['sold'] = '* Sold rate cannot be greater than total hens and cocks.'
            
        if sold and butchered:
            if int(sold) + int(butchered) > int(hens) + int(cocks):
                errors['sold'] = '* Sold rate cannot be greater than total hens and cocks if butchered rate is also provided.'
                errors['butchered'] = '* butchered rate cannot be greater than total hens and cocks if sold rate is also provided.'
                
        allowed_image_types = ['image/jpeg', 'image/png']

        if request.FILES.get('hens_photo'):
            if request.FILES.get('hens_photo').content_type not in allowed_image_types:
                errors['hens_photo'] = 'Invalid image format for hens photo. Only JPEG or PNG is allowed.'
            
        if request.FILES.get('cocks_photo'):
            if request.FILES.get('cocks_photo').content_type not in allowed_image_types:
                errors['cocks_photo'] = 'Invalid image format for cocks photo. Only JPEG or PNG is allowed.'
            
        if errors:
            messages.error(request, f"Creating breeder failed: Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/breeders/create.html', {'breeds': breeds, 'errors': errors})
        
        try:
            breeder = Breeders.objects.create(
                breed=breed,
                hens=hens,
                cocks=cocks,
                mortality=mortality,
                butchered=butchered,
                sold=sold,
                hens_photo=hens_photo,
                cocks_photo=cocks_photo
            )
            
            breeder.save()

            is_minted = mint_breeders(breeder)
            
            if not is_minted:
                breeder.delete()

                messages.error(request, f"Creating breeder failed: Please double-check your entries and try again.", extra_tags='danger')
                return render(request, 'pages/poultry/breeds/create.html', {'errors': errors})

            messages.success(request, 'Breeder created successfully.', extra_tags='success')
        except Exception as e:
            messages.error(request, f'Error creating breeder: {str(e)}', extra_tags='danger')
        return redirect('breeders_list')

    return render(request, 'pages/poultry/breeders/create.html', {'breeds': breeds, 'errors': errors})


def mint_breeders(breeder):
    try:
        api_data = {
                "tokenName": breeder.batch,
                "metadata": {
                    "breed": breeder.breed.code,
                    "hens": breeder.hens,
                    "cocks": breeder.cocks,
                    "mortality": breeder.mortality,
                    "butchered": breeder.butchered,
                    "sold": breeder.sold,
                    "current_number": breeder.current_number,
                    },
                "blockfrostKey": os.getenv('blockfrostKey'),
                "secretSeed": os.getenv('secretSeed'),
                "cborHex": os.getenv('cborHex')
            }

        response = requests.post(os.getenv('OFFCHAIN_BASE_URL')+'mint', json=api_data)
        response_data = response.json()
        if response.status_code == 200 and 'status' in response_data:
            breeder.txHash = response_data['txHash']
            breeder.policyId = response_data['policyId']
            breeder.save()
            return True
        else:
            return JsonResponse({'error': 'Unexpected API response'}, status=400)
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return JsonResponse({'error': 'Failed to communicate with the external API'}, status=500)
        
# Update View
@login_required
def breeders_update(request, batch):
    breeder = get_object_or_404(Breeders, batch=batch)
    errors = {}
    if request.method == 'POST':
        try:
            breeder.batch = request.POST.get('batch', breeder.batch)
            breed = request.POST.get('breed')
            if breed:
                breeder.breed = get_object_or_404(Breed, breed=breed, pk=1)
            else:
                breeder.breed=breeder.breed
            breeder.hens = request.POST.get('hens', breeder.hens)
            breeder.cocks = request.POST.get('cocks', breeder.cocks)
            breeder.mortality = request.POST.get('mortality', breeder.mortality)
            breeder.butchered = request.POST.get('butchered', breeder.butchered)
            breeder.sold = request.POST.get('sold', breeder.sold)
            breeder.current_number = request.POST.get('current_number', breeder.current_number)
            allowed_image_types = ['image/jpeg', 'image/png']
            
            if breeder.cocks and int(breeder.cocks) < 0:
                errors['cocks'] = '* Number of cocks must be a valid number.'
        
            if breeder.hens and int(breeder.hens) < 0:
                errors['hens'] = '* Number of hens must be a valid number.'
            
            if breeder.mortality and int(breeder.mortality) < 0:
                errors['mortality'] = '* Mortality rate must be a valid number.'
                
            if breeder.butchered and int(breeder.butchered) < 0:
                errors['butchered'] = '* Butchered rate must be a valid number.'
                
            if breeder.sold and int(breeder.sold) < 0:
                errors['sold'] = '* Sold rate must be a valid number.'
                
            if breeder.butchered and int(breeder.butchered) > int(breeder.hens) + int(breeder.cocks):
                errors['butchered'] = '* Butchered rate cannot be greater than total hens and cocks.'
                
            if breeder.sold and int(breeder.sold) > int(breeder.hens) + int(breeder.cocks):
                errors['sold'] = '* Sold rate cannot be greater than total hens and cocks.'
                
            if breeder.sold and breeder.butchered:
                if int(breeder.sold) + int(breeder.butchered) > int(breeder.hens) + int(breeder.cocks):
                    errors['sold'] = '* Sold rate cannot be greater than total hens and cocks if butchered rate is also provided.'
                    errors['butchered'] = '* butchered rate cannot be greater than total hens and cocks if sold rate is also provided.'

            if request.FILES.get('hens_photo'):
                if request.FILES.get('hens_photo').content_type not in allowed_image_types:
                    errors['hens_photo'] = 'Invalid image format for hens photo. Only JPEG or PNG is allowed.'
                breeder.hens_photo = request.FILES['hens_photo']
            if request.FILES.get('cocks_photo'):
                if request.FILES.get('cocks_photo').content_type not in allowed_image_types:
                    errors['cocks_photo'] = 'Invalid image format for cocks photo. Only JPEG or PNG is allowed.'
                breeder.cocks_photo = request.FILES['cocks_photo']
                
            if errors:
                messages.error(request, f"Updating breeder failed: Please double-check your entries and try again.", extra_tags='danger')
                return render(request, 'pages/poultry/breeders/details.html', {'breeder': breeder, 'errors': errors, 'breeds':Breed.objects.all()})

            breeder.save()
        except Exception as e:
            
            messages.error(request, f'Error updating breeder: {str(e)}', extra_tags='danger')
        return render(request, 'pages/poultry/breeders/details.html', {'breeder': breeder, 'errors': errors, 'breeds':Breed.objects.all()})

    return render(request, 'pages/poultry/breeders/details.html', {'breeder': breeder,  'breeds':Breed.objects.all()})

# Delete View
@login_required
def breeders_delete(request, batch):
    breeder = get_object_or_404(Breeders, batch=batch)
    if request.method == 'POST':
        breeder.delete()
        return redirect('breeders_list')
