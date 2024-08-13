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
    paginator = Paginator(breeds_list, 10)  # Show 10 breeders per page
    
    page_number = request.GET.get('page')
    breeds = paginator.get_page(page_number)
    return render(request, 'pages/ecommerce/products/products-list.html', {'breeds': breeds})


@login_required
def breed_detail(request, code):
    breed = get_object_or_404(Breed, code=code)
    return render(request, 'pages/ecommerce/products/edit-product.html', {'breed': breed})

@login_required
@csrf_exempt
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
        
        print(front_photo)
        print(side_photo)
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
        return redirect('breed_list')
    
    return render(request, 'pages/ecommerce/products/new-product.html')

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
        if request.FILES.get('front_photo'):
            breed.front_photo = request.FILES.get('front_photo')
        if request.FILES.get('side_photo'):
            breed.side_photo = request.FILES.get('side_photo')
        if request.FILES.get('back_photo'):
            breed.back_photo = request.FILES.get('back_photo')
        breed.save()
        return redirect('breed_list')
    
    return render(request, 'pages/ecommerce/products/edit-product.html', {'breed': breed})

@login_required
def breed_delete(request, code):
    breed = get_object_or_404(Breed, code=code)

    if request.method == 'POST':
        breed.delete()
        messages.success(request, 'Breed deleted successfully.')
        return redirect('breed_list')
    
    return redirect('breed_list')

@login_required
def breeders_list(request):
    breeders = Breeders.objects.all()
    return render(request, 'your_template.html', {'breeders': breeders})




# List View
@login_required
def breeders_list(request):
    breeders_list = Breeders.objects.all()
    paginator = Paginator(breeders_list, 10)  # Show 10 breeders per page
    
    page_number = request.GET.get('page')
    breeders = paginator.get_page(page_number)
    
    return render(request, 'pages/ecommerce/breeders/list.html', {'breeders': breeders})

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

    return render(request, 'pages/ecommerce/breeders/details.html', {'breeder': breeder})

# Create View
@login_required
def breeders_create(request):
    breeds = Breed.objects.all()
    if request.method == 'POST':
        form = BreedersForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('breeders_list')
    else:
        form = BreedersForm()
    return render(request, 'pages/ecommerce/breeders/create.html', {'form': form, 'breeds':breeds})

# Update View
@login_required
def breeders_update(request, batch):
    breeder = get_object_or_404(Breeders, batch=batch)
    
    if request.method == 'POST':
        # Update breeder instance with the new data from the request
        breeder.batch = request.POST.get('batch', breeder.batch)
        breeder.breed = request.POST.get('breed', breeder.breed)
        breeder.hens = request.POST.get('hens', breeder.hens)
        breeder.cocks = request.POST.get('cocks', breeder.cocks)
        breeder.mortality = request.POST.get('mortality', breeder.mortality)
        breeder.butchered = request.POST.get('butchered', breeder.butchered)
        breeder.sold = request.POST.get('sold', breeder.sold)
        breeder.current_number = request.POST.get('current_number', breeder.current_number)
        breeder.description = request.POST.get('description', breeder.description)

        # Handle file uploads
        if request.FILES.get('hens_photo'):
            breeder.hens_photo = request.FILES['hens_photo']
        if request.FILES.get('cocks_photo'):
            breeder.cocks_photo = request.FILES['cocks_photo']

        # Save the updated breeder instance
        breeder.save()
        return redirect('breeders_list')  # Redirect to the breeder detail page after saving

    # Render the template with the breeder instance
    return render(request, 'pages/ecommerce/breeders/details.html', {
        'breeder': breeder  # Pass the breeder instance for additional context
    })

# Delete View
@login_required
def breeders_delete(request, batch):
    breeder = get_object_or_404(Breeders, batch=batch)
    if request.method == 'POST':
        breeder.delete()
        return redirect('breeders_list')
