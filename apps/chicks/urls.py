from django.urls import path
from .views import chicks_list, chicks_detail, chicks_create, chicks_update, chicks_delete, chick_detail_api

urlpatterns = [
    path('chicks/', chicks_list, name='chicks_list'),
    path('chicks/create/', chicks_create, name='chicks_create'),
    path('chicks/<str:batchnumber>/', chicks_detail, name='chicks_detail'),
    path('chicks/<str:batchnumber>/update/', chicks_update, name='chicks_update'),
    path('chicks/<str:batchnumber>/delete/', chicks_delete, name='chicks_delete'),
    path('api/chick/<str:chick_batch>/', chick_detail_api, name='chick-detail'),

]