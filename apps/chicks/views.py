from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from apps.breeders.models import Breed
from apps.customer.models import Eggs, Customer
from django.http import HttpResponse

from apps.hatchery.models import Hatching
from .models import Chicks
from apps.inventory.models import Item

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
    breeds =  Breed.objects.all()
    items = Item.objects.all()
    chick = get_object_or_404(Chicks, batchnumber=batchnumber)
    
    if request.method == 'POST':
        chick.batchnumber = request.POST.get('batchnumber', chick.batchnumber)
        chick.source = request.POST.get('source', chick.source)
        breed_id = request.POST.get('breed', chick.breed.pk)
        if breed_id:
            chick.breed = Breed.objects.get(pk=breed_id)
        chick.age = request.POST.get('age', chick.age)
        chick.description = request.POST.get('description', chick.description)

        if 'chick_photo' in request.FILES:
            chick.chick_photo = request.FILES['chick_photo']
        chick.save()
        return redirect('chicks_detail', batchnumber=chick.batchnumber)
    
    return render(request, 'pages/poultry/chicks/details.html', {'chick': chick, 'breeds':breeds})

@login_required
def chicks_create(request):
    breeds = Breed.objects.all()
    eggs = Eggs.objects.all()
    items = Item.objects.all()
    customers = Customer.objects.all()
    hatchings = Hatching.objects.all()
    if request.method == 'POST':
        item_id = request.POST.get('item')
        source = request.POST.get('source')
        breed_id = request.POST.get('breed')
        age = request.POST.get('age')
        description = request.POST.get('description')
        number = int(request.POST.get('number'))
        customer_id = request.POST.get('customer')
        hatching_code = request.POST.get('hatching')
        customer = None
        if customer_id:
            customer = get_object_or_404(Customer, id=customer_id)
            
        hatching = None
        if hatching_code:
            hatching = get_object_or_404(Hatching, hatchingcode=hatching_code)
        
        item = Item.objects.filter(pk=item_id).first()
        item.quantity=int(number)
        item.save()
        
        print(["Item: ", item])    
        chick_photo = request.FILES.get('chick_photo')

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
        
        
        return redirect('chicks_list') 

    return render(request, 'pages/poultry/chicks/create.html', context={'breeds': breeds, 'eggs': eggs,'items':items, 'customers':customers, 'hatchings': hatchings})

@login_required
def chicks_update(request, batchnumber):
    chick = get_object_or_404(Chicks, batchnumber=batchnumber)
    breeds = Breed.objects.all()
    
    if request.method == 'POST':
        chick.batchnumber = request.POST.get('batchnumber', chick.batchnumber)
        chick.source = request.POST.get('source', chick.source)
        
        breed_id = request.POST.get('breed')
        if breed_id:
            chick.breed = Breed.objects.get(pk=breed_id)
        elif chick.breed:
            pass  # Keep the existing breed if no new breed is selected
        else:
            chick.breed = None  # Set breed to None if no value is provided and no existing breed is present
        
        chick.age = request.POST.get('age', chick.age)
        chick.description = request.POST.get('description', chick.description)

        if 'chick_photo' in request.FILES:
            chick.chick_photo = request.FILES['chick_photo']
        elif chick.chick_photo:
            pass  # Keep the existing photo if no new photo is uploaded
        else:
            chick.chick_photo = None  # Set photo to None if no value is provided and no existing photo is present

        chick.save()
        return redirect('chicks_detail', batchnumber=chick.batchnumber)

    return render(request, 'pages/poultry/chicks/details.html', {'chick': chick, 'breeds': breeds})

@login_required
def chicks_delete(request, batchnumber):
    chick = get_object_or_404(Chicks, batchnumber=batchnumber)
    if request.method == 'POST':
        chick.delete()
        chick.item.delete()
        return redirect('chicks_list')
    return redirect('chicks_list')