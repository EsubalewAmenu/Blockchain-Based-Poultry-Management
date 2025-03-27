from django.urls import path
from .views import *

urlpatterns = [
    # Customer
    path('vendor/', vendor_list, name='vendor_list'),
    path('vendor/create/', vendor_create, name='vendor_create'),
    path('vendor/<str:full_name>/', vendor_detail, name='vendor_detail'),
    path('vendor/<str:full_name>/update/', vendor_update, name='vendor_update'),
    path('vendor/<str:full_name>/delete/', vendor_delete, name='vendor_delete'),
    path('vendor/<str:full_name>/update_notifications/', vendor_update_notifications, name='vendor_update_notifications'),
    
    #Feeds
    path('feeds/', feeds_list, name='feeds_list'),
    path('feeds/create/', feeds_create, name='feeds_create'),
    path('feeds/<str:batch_number>/', feeds_detail, name='feeds_detail'),
    path('feeds/<str:batch_number>/update/', feeds_update, name='feeds_update'),
    path('feeds/<str:batch_number>/delete/', feeds_delete, name='feeds_delete'),
    
    #Medicines
    path('medicines/', medicines_list, name='medicines_list'),
    path('medicines/create/', medicines_create, name='medicines_create'),
    path('medicines/<str:batch_number>/', medicines_detail, name='medicines_detail'),
    path('medicines/<str:batch_number>/update/', medicines_update, name='medicines_update'),
    path('medicines/<str:batch_number>/delete/', medicines_delete, name='medicines_delete'),
    
]
