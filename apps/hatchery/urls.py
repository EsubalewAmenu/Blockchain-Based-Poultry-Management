from django.urls import path
from .views import *

urlpatterns = [
    
    path('egg-settings/create/', egg_setting_create, name='egg_setting_create'),
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
    path('egg-settings/<str:settingcode>/', egg_setting_detail, name='egg_setting_detail'),
    path('egg-settings/<str:settingcode>/update/', egg_setting_update, name='egg_setting_update'),
    path('egg-settings/<str:settingcode>/delete/', egg_setting_delete, name='egg_setting_delete'),
    path('api/eggsetting/<int:egg_id>/', eggsetting_detail_api, name='eggsetting-detail'),

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
    path('api/hatching/<int:hatching_id>/', chick_hatching_detail_api, name='chick-hatching-detail'),

    path('tracker/list/', tracker_list_view, name='tracker_list'),
    path('tracker/<str:tracker_code>/', tracker_details_view, name='tracker_detail'),
    path('tracker/public/<str:tracker_code>/', tracker_public_view, name='tracker_public'),
    path('tracker/<str:tracker_code>/barcode', tracker_barcode_image_view, name='tracker_barcode_image'),
    path('tracker/<str:tracker_code>/qrcode', tracker_qrcode_image_view, name='tracker_qr_code'),

    path('feed-settings/create/', feed_setting_create, name='feed_setting_create'),    
    path('feed-settings/', feed_setting_list, name='feed_setting_list'),
    path('feed-settings/<str:settingcode>/', feed_setting_detail, name='feed_setting_detail'),
    path('feed-settings/<str:settingcode>/update/', feed_setting_update, name='feed_setting_update'),
    path('feed-settings/<str:settingcode>/delete/', feed_setting_delete, name='feed_setting_delete'),
    path('api/feedsetting/<int:feedsetting_id>/', feedsetting_detail_api, name='feedsetting-detail-api'),
    path('api/feedsettings/<int:feed_id>/', feed_detail_api, name='feed-detail-api'),

    path('medicine-settings/create/', medicine_setting_create, name='medicine_setting_create'),    
    path('medicine-settings/', medicine_setting_list, name='medicine_setting_list'),
    path('medicine-settings/<str:settingcode>/', medicine_setting_detail, name='medicine_setting_detail'),
    path('medicine-settings/<str:settingcode>/update/', medicine_setting_update, name='medicine_setting_update'),
    path('medicine-settings/<str:settingcode>/delete/', medicine_setting_delete, name='medicine_setting_delete'),
    path('api/medicinesetting/<int:medicinesetting_id>/', medicinesetting_detail_api, name='medicinesetting-detail-api'),
    path('api/medicinesettings/<int:medicine_id>/', medicinesettings_detail_api, name='medicine-detail-api'),

    path('feeding/', feeding_list, name='feeding_list'),
    path('feeding/create/', feeding_create, name='feeding_create'),
    path('feeding/<str:code>/', feeding_detail, name='feeding_detail'),
    path('feedings/<str:code>/update/', feeding_update, name='feeding_update'),
    path('feeding/<str:code>/delete', feeding_delete, name='feeding_delete'),
    path('api/feeding/<int:chick_id>/', chick_feeding_detail_api, name='chick-feeding-detail'),
    path('api/feeduses/<int:feed_setting_id>/', chick_feed_uses_detail_api, name='chick-feed_uses-detail'),

    path('medication/', medication_list, name='medication_list'),
    path('medication/create/', medication_create, name='medication_create'),
    path('medication/<str:code>/', medication_detail, name='medication_detail'),
    path('medications/<str:code>/update/', medication_update, name='medication_update'),
    path('medication/<str:code>/delete', medication_delete, name='medication_delete'),
    path('api/medications/<int:chick_id>/', chick_medications_detail_api, name='chick-medications-detail'),
    path('api/medicationuses/<int:medicine_setting_id>/', chick_medication_uses_detail_api, name='chick-medication_uses-detail'),

]


