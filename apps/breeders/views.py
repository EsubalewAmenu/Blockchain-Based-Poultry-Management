from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import *
from django.urls import reverse
from .forms import BreedersForm

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
    if request.method == 'POST':
        breed.code = request.POST.get('code', breed.code)
        breed.poultry_type = request.POST.get('poultry_type', breed.poultry_type)
        breed.breed = request.POST.get('breed', breed.breed)
        breed.purpose = request.POST.get('purpose', breed.purpose)
        breed.eggs_year = request.POST.get('eggs_year', breed.eggs_year)
        breed.adult_weight = request.POST.get('adult_weight', breed.adult_weight)
        breed.description = request.POST.get('description', breed.description)
        allowed_image_types = ['image/jpeg', 'image/png']  # Allowed image types

        if request.FILES.get('back_photo'):
            if request.FILES.get('back_photo').content_type not in allowed_image_types:
                messages.error(request, "Invalid image format for front photo. Only JPEG or PNG is allowed.", extra_tags='danger')
                return redirect('breed_detail', code=code)
            
        if request.FILES.get('front_photo'):
            if request.FILES.get('front_photo').content_type not in allowed_image_types:
                messages.error(request, "Invalid image format for front photo. Only JPEG or PNG is allowed.", extra_tags='danger')
                return redirect('breed_detail', code=code)
            
        if request.FILES.get('side_photo'):
            if request.FILES.get('side_photo').content_type not in allowed_image_types:
                messages.error(request, "Invalid image format for front photo. Only JPEG or PNG is allowed.", extra_tags='danger')
                return redirect('breed_detail', code=code)
        if request.FILES.get('front_photo'):
            breed.front_photo = request.FILES.get('front_photo')
        if request.FILES.get('side_photo'):
            breed.side_photo = request.FILES.get('side_photo')
        if request.FILES.get('back_photo'):
            breed.back_photo = request.FILES.get('back_photo')
        breed.save()
        messages.success(request, 'Breed updated successfully.', extra_tags='success')
        return redirect('breed_detail', code=code)
    return render(request, 'pages/poultry/breeds/edit.html', {'breed': breed, 'breeds': Breed.objects.all()})

@login_required
def breed_create(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        poultry_type = request.POST.get('poultry_type')
        breed_name = request.POST.get('breed_name')
        purpose = request.POST.get('purpose')
        eggs_year = request.POST.get('eggs_per_year')
        adult_weight = request.POST.get('adult_weight')
        description = request.POST.get('description')
        front_photo = request.FILES.get('front_photo')
        side_photo = request.FILES.get('side_photo')
        back_photo = request.FILES.get('back_photo')
        if Breed.objects.filter(code=code).exists():
            messages.error(request, "Breed with this code already exists", extra_tags='danger')
            return redirect('breed_create')
        
        allowed_image_types = ['image/jpeg', 'image/png']  # Allowed image types

        if front_photo:
            if front_photo.content_type not in allowed_image_types:
                messages.error(request, "Invalid image format for front photo. Only JPEG or PNG is allowed.", extra_tags='danger')
                return redirect('breed_create')

        if side_photo:
            if side_photo.content_type not in allowed_image_types:
                messages.error(request, "Invalid image format for side photo. Only JPEG or PNG is allowed.", extra_tags='danger')
                return redirect('breed_create')


        if back_photo:
            if back_photo.content_type not in allowed_image_types:
                messages.error(request, "Invalid image format for back photo. Only JPEG or PNG is allowed.", extra_tags='danger')
                return redirect('breed_create')
            
        breed = Breed.objects.create(
            code=code,
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
        messages.success(request, "Breed has been created successfully", extra_tags='success')
        return redirect('breed_list')
    
    return render(request, 'pages/poultry/breeds/create.html')

@login_required
def breed_update(request, code):
    breed = get_object_or_404(Breed, code=code)
    if request.method == 'POST':
        breed.code = request.POST.get('code', breed.code)
        breed.poultry_type = request.POST.get('poultry_type', breed.poultry_type)
        breed.breed = request.POST.get('breed', breed.breed)
        breed.purpose = request.POST.get('purpose', breed.purpose)
        breed.eggs_year = request.POST.get('eggs_year', breed.eggs_year)
        breed.adult_weight = request.POST.get('adult_weight', breed.adult_weight)
        breed.description = request.POST.get('description', breed.description)
        
        allowed_image_types = ['image/jpeg', 'image/png']  # Allowed image types

        if request.FILES.get('back_photo'):
            if request.FILES.get('back_photo').content_type not in allowed_image_types:
                messages.error(request, "Invalid image format for front photo. Only JPEG or PNG is allowed.", extra_tags='danger')
                return redirect('breed_update')
            
        if request.FILES.get('front_photo'):
            if request.FILES.get('front_photo').content_type not in allowed_image_types:
                messages.error(request, "Invalid image format for front photo. Only JPEG or PNG is allowed.", extra_tags='danger')
                return redirect('breed_update')
            
        if request.FILES.get('side_photo'):
            if request.FILES.get('side_photo').content_type not in allowed_image_types:
                messages.error(request, "Invalid image format for front photo. Only JPEG or PNG is allowed.", extra_tags='danger')
                return redirect('breed_update')
            
        if request.FILES.get('front_photo'):
            breed.front_photo = request.FILES.get('front_photo')
        if request.FILES.get('side_photo'):
            breed.side_photo = request.FILES.get('side_photo')
        if request.FILES.get('back_photo'):
            
            breed.back_photo = request.FILES.get('back_photo')
        breed.save()
        messages.success(request, 'Breed updated successfully.')
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
    paginator = Paginator(breeders_list, 10)  # Show 10 breeders per page
    
    page_number = request.GET.get('page')
    breeders = paginator.get_page(page_number)
    
    return render(request, 'pages/poultry/breeders/list.html', {'breeders': breeders})

# Detail View
@login_required
def breeders_detail(request, batch):
    breeder = get_object_or_404(Breeders, batch=batch)
    if request.method == 'POST':
        # Update breeder instance with the new data from the request
        breeder.batch = request.POST.get('batch', breeder.batch)
                # Retrieve the Breed instance based on the submitted breed ID or slug
        breed = request.POST.get('breed')  # Assuming you are sending the breed ID
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

        # Handle file uploads
        if request.FILES.get('hens_photo'):
            breeder.hens_photo = request.FILES['hens_photo']
        if request.FILES.get('cocks_photo'):
            breeder.cocks_photo = request.FILES['cocks_photo']

        breeder.save()
        return redirect('breeders_list')

    return render(request, 'pages/poultry/breeders/details.html', {'breeder': breeder,  'breeds':Breed.objects.all()})

# Create View
@login_required
def breeders_create(request):
    breeds = Breed.objects.all()

    if request.method == 'POST':
        batch = request.POST.get('batch')
        breed_id = request.POST.get('breed')  # Use the ID of the breed from the form
        breed = Breed.objects.get(id=breed_id) if breed_id else None  # Retrieve the Breed object
        hens = request.POST.get('hens')
        cocks = request.POST.get('cocks')
        mortality = request.POST.get('mortality')
        butchered = request.POST.get('butchered')
        sold = request.POST.get('sold')
        if sold in ['', "", None]:
            sold=0
        if butchered in ['', "", None]:
            butchered=0
        hens_photo = request.FILES.get('hens_photo')
        cocks_photo = request.FILES.get('cocks_photo')

        # Create a new Breeders instance
        breeder = Breeders.objects.create(
            batch=batch,
            breed=breed,
            hens=hens,
            cocks=cocks,
            mortality=mortality,
            butchered=butchered,
            sold=sold,
            hens_photo=hens_photo,
            cocks_photo=cocks_photo
        )
        
        breeder.save()  # Save the breeder instance
        return redirect('breeders_list')

    return render(request, 'pages/poultry/breeders/create.html', {'breeds': breeds})


# Update View
@login_required
def breeders_update(request, batch):
    breeder = get_object_or_404(Breeders, batch=batch)
    
    if request.method == 'POST':
        # Update breeder instance with the new data from the request
        breeder.batch = request.POST.get('batch', breeder.batch)
        breed_name = request.POST.get('breed')
        if breed_name:
            try:
                breed = Breed.objects.get(breed=breed_name)
                breeder.breed = breed
            except Breed.DoesNotExist:
                breeder.breed = None
        breeder.hens = request.POST.get('hens', breeder.hens)
        breeder.cocks = request.POST.get('cocks', breeder.cocks)
        breeder.mortality = request.POST.get('mortality', breeder.mortality)
        breeder.butchered = request.POST.get('butchered', breeder.butchered)
        breeder.sold = request.POST.get('sold', breeder.sold)
        if breeder.sold in ["",'',]:
            breeder.sold=0
        
        if breeder.butchered == None:
            breeder.butchered=0
            
        breeder.current_number = request.POST.get('current_number', breeder.current_number)

        # Handle file uploads
        if request.FILES.get('hens_photo'):
            breeder.hens_photo = request.FILES['hens_photo']
        if request.FILES.get('cocks_photo'):
            breeder.cocks_photo = request.FILES['cocks_photo']

        # Save the updated breeder instance
        breeder.save()
        messages.success(request, "Breeder Updated Successfully.", extra_tags='success')        
        return redirect('breeders_update', batch=batch)  # Redirect to the breeder detail page after saving

    # Render the template with the breeder instance
    return render(request, 'pages/poultry/breeders/details.html', {
        'breeder': breeder,
        'breeds':Breed.objects.all()
         # Pass the breeder instance for additional context
    })

# Delete View
@login_required
def breeders_delete(request, batch):
    breeder = get_object_or_404(Breeders, batch=batch)
    if request.method == 'POST':
        breeder.delete()
        return redirect('breeders_list')