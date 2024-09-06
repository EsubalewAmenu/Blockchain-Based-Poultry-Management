from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings
from django.apps import apps
from django.contrib import messages
from apps.customer.models import Eggs
from apps.chicks.models import Chicks
from apps.hatchery.models import Incubators
from .models import ItemType, Item, ItemRequest
from apps.hatchery.models import EggSetting

@login_required
def item_type_list(request):
    """
    List all ItemType records with optional filtering by code.
    """
    code_filter = request.GET.get('code', '')  # Get the code from the query parameters
    if code_filter:
        item_types = ItemType.objects.filter(code__icontains=code_filter).order_by('-created_at')
    else:
        item_types = ItemType.objects.all().order_by('-created_at')

    paginator = Paginator(item_types, 10)  # Show 10 item types per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        type_name = request.POST.get('type_name')

        # Create the ItemType instance
        item_type = ItemType(
            type_name=type_name
        )
        item_type.save()  # Save the ItemType instance

        return redirect('item_type_list')  # Redirect to the list view

    context = {
        'page_obj': page_obj,
        'code_filter': code_filter,  # Pass the current filter value to the template
    }
    return render(request, 'pages/inventory/item_type/list.html', context)

@login_required
def item_type_detail(request, code):
    """
    Update an existing ItemType record.
    """
    item_type = get_object_or_404(ItemType, code=code)

    if request.method == 'POST':
        item_type.type_name = request.POST.get('type_name')
        item_type.save()
        return redirect('item_type_list')

    return render(request, 'pages/inventory/item_type/details.html', {'item_type': item_type})

@login_required
def item_type_create(request):
    """
    Create a new ItemType record.
    """
    

    if request.method == 'POST':
        type_name = request.POST.get('type_name')
        related_object = request.POST.get('related_object')  # Get the related object model name

        # Create the ItemType instance
        item_type = ItemType(
            type_name=type_name,
        )
        item_type.save()  # Save the ItemType instance

        return redirect('item_type_list')  # Redirect to the list view

    return render(request, 'pages/inventory/item_type/list.html')

@login_required
def item_type_delete(request, code):
    """
    Delete an ItemType record.
    """
    item_type = get_object_or_404(ItemType, code=code)

    if request.method == 'POST':
        item_type.delete()
        return redirect('item_type_list')

    context = {
        'item_type': item_type,
    }
    return render(request, 'pages/inventory/item_type/delete.html', context)

@login_required
def item_list(request):
    """
    List all Item records with optional filtering by code.
    """
    code_filter = request.GET.get('code', '')
    if code_filter:
        items = Item.objects.filter(code__icontains=code_filter).order_by('-created_at')
    else:
        items = Item.objects.all().order_by('-created_at')

    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    items = paginator.get_page(page_number)

    context = {
        'items': items,
        'item_types':ItemType.objects.all(),
        'code_filter': code_filter,
    }
    return render(request, 'pages/inventory/item/list.html', context)

@login_required
def item_detail(request, code):
    """
    View for a single Item record with update functionality.
    """
    item = get_object_or_404(Item, code=code)

    if request.method == 'POST':
        item.item_type = ItemType.objects.get(id=request.POST.get('item_type'))
        item.quantity = request.POST.get('amount')
        item.save()
        return redirect('item_detail', code=item.code)

    context = {
        'item': item,
        'item_types': ItemType.objects.all(),
    }
    return render(request, 'pages/inventory/item/details.html', context)

@login_required
def item_create(request):
    """
    Create a new Item record.
    """
    if request.method == 'POST':
        item_type_id = request.POST.get('item_type')
        item_type = get_object_or_404(ItemType, id=item_type_id)
        quantity=request.POST.get('amount', None)
        if quantity == '':
            quantity=None
        # Create and save the Item
        item = Item(
            item_type=item_type,
            quantity=quantity,
        )
        item.save()
    context = {
        'item_types': ItemType.objects.all(),
    }
    return render(request, 'pages/inventory/item/create.html', context)

@login_required
def item_delete(request, code):
    """
    Delete an Item record.
    """
    item = get_object_or_404(Item, code=code)

    if request.method == 'POST':
        item.delete()
        return redirect('item_list')  # Redirect to the list view

    context = {
        'item': item,
    }
    return render(request, 'pages/inventory/item/delete.html', context)

@login_required
def item_request(request):
    """
    Request items from the inventory.
    """
    item_id = request.POST.get('item')
    amount = request.POST.get('amount')
    item = get_object_or_404(Item, code=item_id)

    if item.quantity is None or item.quantity >= int(amount):
       messages.error(request, "Invalid amount")
       return redirect('item_request_list')
        
    item.quantity -= int(amount)
    item.save()

    item_request = ItemRequest(
        item=item,
        amount=amount,
    )
    item_request.save()
    
    item_request = ItemRequest(
        item=item,
        amount=amount,
    )

    return redirect('item_list')

@login_required
def item_request_list(request):
    item_requests = ItemRequest.objects.all().order_by('-created_at')
    paginator = Paginator(item_requests, 10)
    page_number = request.GET.get('page')
    item_requests = paginator.get_page(page_number)
    
    """
    Request items from the inventory.
    """
    if request.method == 'POST':
        item_id = request.POST.get('item')
        amount = request.POST.get('amount')
        item = get_object_or_404(Item, code=item_id)

        if item.quantity == 0 or item.quantity <= int(amount):
            messages.error(request, "Invalid amount")
            return redirect('item_request_list')

        item_request = ItemRequest(
            item=item,
            quantity=amount,
            requested_by=request.user
        )
        item_request.save()

        return redirect('item_request_list')
    
    

    context = {
        'item_requests': item_requests,
        'items': Item.objects.all(),
    }
    return render(request, 'pages/inventory/item/item_request/list.html', context)

@login_required
def item_request_approve(request, code):
    item_request = get_object_or_404(ItemRequest, code=code)
    item = item_request.item
    item.quantity -= item_request.quantity
    item.save()
    item_request.approve()
    egg_setting = EggSetting.objects.get(item_request=item_request)
    if egg_setting:
        egg_setting.is_approved = True
        egg_setting.save()
    

    return redirect('item_request_list')
    