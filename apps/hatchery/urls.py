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
    
    path('egg-settings/', egg_setting_list, name='egg_setting_list'),
    path('egg-settings/create/', egg_setting_create, name='egg_setting_create'),
    path('egg-settings/<str:settingcode>/', egg_setting_detail, name='egg_setting_detail'),
    path('egg-settings/<str:settingcode>/update/', egg_setting_update, name='egg_setting_update'),
    path('egg-settings/<str:settingcode>/delete/', egg_setting_delete, name='egg_setting_delete'),
    
    path('incubations/', incubation_list, name='incubation_list'),
    path('incubation/create/', incubation_create, name='incubation_create'),
    path('incubation/<slug:incubationcode>/', incubation_detail, name='incubation_detail'),
    path('incubation/<slug:incubationcode>/update/', incubation_update, name='incubation_update'),
    path('incubation/<slug:incubationcode>/delete/', incubation_delete, name='incubation_delete'),
    
    path('candlings/', candling_list, name='candling_list'),
    path('candling/create/', candling_create, name='candling_create'),
    path('candling/<str:candlingcode>/', candling_detail, name='candling_detail'),
    path('candling/<str:candlingcode>/update/', candling_detail, name='candling_update'),
    path('candling/<str:candlingcode>/delete/', candling_delete, name='candling_delete'),
    
    path('hatchings/', hatching_list, name='hatching_list'),
    path('hatching/create/', hatching_create, name='hatching_create'),
    path('hatching/<str:hatchingcode>/', hatching_detail, name='hatching_detail'),
    path('hatching/<str:hatchingcode>/update/', hatching_detail, name='hatching_update'),
    path('hatching/<str:hatchingcode>/delete/', hatching_delete, name='hatching_delete'),
]

