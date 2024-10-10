from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from apps.breeders.models import Breed
from apps.customer.models import Eggs, Customer
from django.http import HttpResponse
from django.contrib import messages
from apps.hatchery.models import Hatching
from .models import Chicks
from apps.inventory.models import Item
import datetime

@login_required
def chicks_list(request):
    chicks = Chicks.objects.all()
    breeds = Breed.objects.all()
    eggs = Eggs.objects.all()
    paginator = Paginator(chicks, 10)
    
    page_number = request.GET.get('page')
    chicks = paginator.get_page(page_number)
    return render(request, 'pages/poultry/chicks/list.html', {'chicks': chicks, 'breeds': breeds, 'eggs': eggs})

@login_required
def chicks_detail(request, batchnumber):
    chick = get_object_or_404(Chicks, batchnumber=batchnumber)
    breeds = Breed.objects.all()
    errors={}
    if request.method == 'POST':
        chick.batchnumber = request.POST.get('batchnumber', chick.batchnumber)
        chick.source = request.POST.get('source', chick.source)
        breed_id = request.POST.get('breed')
        if breed_id:
            chick.breed = Breed.objects.get(pk=breed_id)
        
        chick.age = request.POST.get('age', chick.age)
        chick.description = request.POST.get('description', chick.description)
        allowed_image_types = ['image/jpeg', 'image/png']
        
        if request.POST.get('age') and datetime.datetime.strptime(request.POST.get('age'), "%Y-%m-%d").date() > datetime.datetime.now().date():
            errors['age'] = "Invalid Age. Age should be less than or equal to current date."

        if request.FILES.get('chick_photo'):
            if request.FILES.get('chick_photo').content_type not in allowed_image_types:
                errors['chick_photo'] = "Invalid image format for front photo. Only JPEG or PNG is allowed."
                
        if errors:
            messages.error(request, "Updating chick failed: Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/chicks/details.html', {'chick': chick, 'breeds': breeds, 'errors': errors})
                
        if 'chick_photo' in request.FILES:
            chick.chick_photo = request.FILES['chick_photo']
        try:
            chick.save()
            messages.success(request, "Chicks Updated Successfully", extra_tags="success")
        except Exception as e:
            messages.error(request, f"Error updating chick: {str(e)}", extra_tags='danger')        
        return redirect('chicks_detail', batchnumber=chick.batchnumber)

    return render(request, 'pages/poultry/chicks/details.html', {'chick': chick, 'breeds': breeds})

@login_required
def chicks_create(request):
    breeds = Breed.objects.all()
    eggs = Eggs.objects.all()
    items = Item.objects.filter(item_type__type_name="Chicks")
    customers = Customer.objects.all()
    hatchings = Hatching.objects.all()
    item_data = None
    errors = {}
    
    if 'item_data' in request.session:
        item_data = request.session['item_data']
    if request.method == 'POST':
        item_id = request.POST.get('item')
        source = request.POST.get('source')
        breed_id = request.POST.get('breed')
        age = request.POST.get('age')
        description = request.POST.get('description')
        number = int(request.POST.get('number'))
        customer_id = request.POST.get('customer')
        hatching_code = request.POST.get('hatching')
        chick_photo = request.FILES.get('chick_photo')
        customer = None
        allowed_image_types = ['image/jpeg', 'image/png']
        
        required_fields = ['item', 'source', 'breed', 'number']
        for field in required_fields:
            if not request.POST.get(field):
                errors[field] = "* This field is required."
                
                
        if source:
            if source == 'hatching' and not hatching_code:
                errors['hatching'] = "* This field is required"
            elif source == 'customer' and not customer_id:
                errors['customer'] = "* This field is required"
                
        if age in ['', ""]:
            age = datetime.datetime.now().date()
        
        if age and datetime.datetime.strptime(age, "%Y-%m-%d").date() > datetime.datetime.now().date():
            errors['age'] = "Invalid Age. Age should be less than or equal to current date."
            
        if chick_photo:
            if request.FILES.get('chick_photo').content_type not in allowed_image_types:
                errors['chick_photo'] = "Invalid image format for front photo. Only JPEG or PNG is allowed."
            
        if customer_id:
            customer = get_object_or_404(Customer, id=customer_id)
            
        hatching = None
        if hatching_code:
            hatching = get_object_or_404(Hatching, hatchingcode=hatching_code)
            
        item_data = None    
        if 'item_data' in request.session:
            item_data = request.session['item_data']
            
        if errors:
            messages.error(request, "Creating chick failed: Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/chicks/create.html', {'breeds': breeds, 'eggs': eggs, 'items': items, 'item_data': item_data, 'customers': customers, 'hatchings': hatchings, 'errors': errors})
            
        item = Item.objects.filter(pk=item_id).first()
        
        chick = Chicks(
            item=item,
            source=source,
            breed_id=breed_id,
            customer=customer,
            hatching=hatching,
            age=age,
            description=description,
            chick_photo=chick_photo,
            number=number
        )
        chick.save()
        messages.success(request, "Chicks Created Successfully", extra_tags="success")
        if 'item_data' in request.session:
            request.session.pop('item_data')
        return redirect('chicks_list') 

    return render(request, 'pages/poultry/chicks/create.html', context={'breeds': breeds, 'eggs': eggs,'items':items, 'item_data':item_data, 'customers':customers, 'hatchings': hatchings})

@login_required
def chicks_update(request, batchnumber):
    chick = get_object_or_404(Chicks, batchnumber=batchnumber)
    breeds = Breed.objects.all()
    errors={}
    if request.method == 'POST':
        chick.batchnumber = request.POST.get('batchnumber', chick.batchnumber)
        chick.source = request.POST.get('source', chick.source)
        breed_id = request.POST.get('breed')
        if breed_id:
            chick.breed = Breed.objects.get(pk=breed_id)
        
        chick.age = request.POST.get('age', chick.age)
        chick.description = request.POST.get('description', chick.description)
        allowed_image_types = ['image/jpeg', 'image/png']
        
        if request.POST.get('age') and datetime.datetime.strptime(request.POST.get('age'), "%Y-%m-%d").date() > datetime.datetime.now().date():
            errors['age'] = "Invalid Age. Age should be less than or equal to current date."

        if request.FILES.get('chick_photo'):
            if request.FILES.get('chick_photo').content_type not in allowed_image_types:
                errors['chick_photo'] = "Invalid image format for front photo. Only JPEG or PNG is allowed."
                
        if errors:
            messages.error(request, "Updating chick failed: Please double-check your entries and try again.", extra_tags='danger')
            return render(request, 'pages/poultry/chicks/details.html', {'chick': chick, 'breeds': breeds, 'errors': errors})
                
        if 'chick_photo' in request.FILES:
            chick.chick_photo = request.FILES['chick_photo']
        try:
            chick.save()
            messages.success(request, "Chicks Updated Successfully", extra_tags="success")
        except Exception as e:
            messages.error(request, f"Error updating chick: {str(e)}", extra_tags='danger')        
        return redirect('chicks_detail', batchnumber=chick.batchnumber)

    return render(request, 'pages/poultry/chicks/details.html', {'chick': chick, 'breeds': breeds})

@login_required
def chicks_delete(request, batchnumber):
    chick = get_object_or_404(Chicks, batchnumber=batchnumber)
    if request.method == 'POST':
        chick.delete()
        chick.item.delete()
        messages.success(request, "Chicks Deleted Successfully", extra_tags="success")
        return redirect('chicks_list')
    return redirect('chicks_list')