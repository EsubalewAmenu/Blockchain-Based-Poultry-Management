from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from apps.breeders.models import Breed
from apps.customer.models import Eggs
from django.http import HttpResponse
from .models import Chicks

def chicks_list(request):
    chicks = Chicks.objects.all()
    breeds = Breed.objects.all()
    eggs = Eggs.objects.all()
    paginator = Paginator(chicks, 10)
    
    page_number = request.GET.get('page')
    chicks = paginator.get_page(page_number)
    return render(request, 'pages/ecommerce/chicks/list.html', {'chicks': chicks, 'breeds': breeds, 'eggs': eggs})

def chicks_detail(request, batchnumber):
    breeds =  Breed.objects.all()
    chick = get_object_or_404(Chicks, batchnumber=batchnumber)
    return render(request, 'pages/ecommerce/chicks/details.html', {'chick': chick, 'breeds':breeds})

def chicks_create(request):
    breeds = Breed.objects.all()
    eggs = Eggs.objects.all()
    if request.method == 'POST':
        batchnumber = request.POST.get('batchnumber')
        source = request.POST.get('source')
        breed_id = request.POST.get('breed')
        age = request.POST.get('age')
        description = request.POST.get('description')
        egg_id = request.POST.get('egg')
        chick_photo = request.FILES.get('chick_photo')

        chick = Chicks(
            batchnumber=batchnumber,
            source=source,
            breed_id=breed_id,
            age=age,
            description=description,
            egg=egg_id,
            chick_photo=chick_photo
        )
        chick.save()
        return redirect('chicks_list') 

    return render(request, 'pages/ecommerce/chicks/create.html', context={'breeds': breeds, 'eggs': eggs})

def chicks_update(request, batchnumber):
    chick = get_object_or_404(Chicks, batchnumber=batchnumber)
    breeds = Breed.objects.all()  # Fetch all breeds
    
    if request.method == 'POST':
        chick.batchnumber = request.POST.get('batchnumber', chick.batchnumber)
        chick.source = request.POST.get('source', chick.source)
        chick.breed = request.POST.get('breed', chick.breed)
        chick.age = request.POST.get('age', chick.age)
        chick.description = request.POST.get('description', chick.description)

        # Handle file upload if a new photo is provided
        if 'chick_photo' in request.FILES:
            chick.chick_photo = request.FILES['chick_photo']

        chick.save()
        return redirect('chicks_detail', batchnumber=chick.batchnumber)

    return render(request, 'pages/ecommerce/chicks/details.html', {'chick': chick, 'breeds': breeds})

def chicks_delete(request, batchnumber):
    chick = get_object_or_404(Chicks, batchnumber=batchnumber)
    if request.method == 'POST':
        chick.delete()
        return redirect('chicks_list')
    return redirect('chicks_list')