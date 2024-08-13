from django.urls import path
from .views import *

urlpatterns = [
    path('hatchery/', hatchery_list, name='hatchery_list'),
    path('hatchery/create/', hatcher_create, name='hatchery_create'),
    path('hatchery/<str:name>/', hatchery_detail, name='hatchery_detail'),
    path('hatchery/<str:name>/update/', hatchery_update, name='hatchery_update'),
    path('hatchery/<str:name>/delete/', hatchery_delete, name='hatchery_delete'),
    path('incubator/capacity/', incubator_capacity_list, name='incubator_capacity_list'),
    path('incubator/capacity/create/', incubator_capacity_create, name='incubator_capacity_create'),
    path('incubator/capacity/<int:id>/update/', incubator_capacity_update, name='incubator_capacity_update'),
    path('incubator/capacity/<int:id>/', incubator_capacity_details, name='incubator_capacity_details'),
    path('incubator/capacity/<int:id>/delete/', incubator_capacity_delete, name='incubator_capacity_delete'),
    path('incubator/', incubator_list, name='incubator_list'),
    path('incubator/create/', incubator_create, name='incubator_create'),
    path('incubator/<str:code>/', incubator_detail, name='incubator_detail'),
    path('incubators/<str:code>/update/', incubator_update, name='incubator_update'),
    path('incubator/<str:code>/delete', incubator_delete, name='incubator_delete'),
    

]

