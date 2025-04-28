from django.urls import path
from .views import (
    item_type_list,
    item_type_detail,
    item_type_create,
    item_type_delete,
    item_list,
    item_detail,
    item_create,
    item_delete,
    item_request,
    item_request_list,
    item_request_approve,
    item_request_delete,
    item_request_approve_detail_api
)

urlpatterns = [
    path('item-type/', item_type_list, name='item_type_list'),
    path('item-type/create/', item_type_create, name='item_type_create'),
    path('item-type/<str:code>/', item_type_detail, name='item_type_detail'),
    path('item-type/<str:code>/update/', item_type_detail, name='item_type_update'),
    path('item-type/<str:code>/delete/', item_type_delete, name='item_type_delete'),

    path('items/', item_list, name='item_list'),
    path('item/create/', item_create, name='item_create'),
    path('item/<str:code>/', item_detail, name='item_detail'),
    path('item/<str:code>/update/', item_detail, name='item_update'),
    path('item/<str:code>/delete/', item_delete, name='item_delete'),
    
    
    path('item/request/list/', item_request_list, name='item_request_list'),
    path('item/request/<str:code>/delete/', item_request_delete, name='item_request_delete'),
    path('item/request/', item_request, name='item_request'),
    path('item/request/<str:code>/approve/', item_request_approve, name='item_request_approve'),
    path('api/item-request/<int:item_request_id>/', item_request_approve_detail_api, name='item-request-detail'),

]