from django.urls import path
from .views import *

urlpatterns = [
    # Customer
    path('customer/', customer_list, name='customer_list'),
    path('customer/create/', customer_create, name='customer_create'),
    path('customer/<str:full_name>/', customer_detail, name='customer_detail'),
    path('customer/<str:full_name>/update/', customer_update, name='customer_update'),
    path('customer/<str:full_name>/delete/', customer_delete, name='customer_delete'),
    path('customer/<str:full_name>/update_notifications/', customer_update_notifications, name='customer_update_notifications'),
    
    #Eggs
    path('eggs/', eggs_list, name='eggs_list'),
    path('eggs/create/', eggs_create, name='eggs_create'),
    path('eggs/<str:batch_number>/', eggs_detail, name='eggs_detail'),
    path('eggs/<str:batch_number>/update/', eggs_update, name='eggs_update'),
    path('eggs/<str:batch_number>/delete/', eggs_delete, name='eggs_delete'),
    
    # Customer Request
    path('customer_requests/', customer_request_list, name='customer_request_list'),
    path('customer_requests/create/', customer_request_create, name='customer_request_create'),
    path('customer_requests/<str:requestcode>/', customer_request_detail, name='customer_request_detail'),
    path('customer_requests/<str:requestcode>/update/', customer_request_update, name='customer_request_update'),
    path('customer_requests/<str:requestcode>/delete/', customer_request_delete, name='customer_request_delete'),
]
