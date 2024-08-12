from django.urls import path
from .views import *

urlpatterns = [
    # path('', BreedListView.as_view(), name='breed_list'),
    # path('<int:pk>/', BreedDetailView.as_view(), name='breed_detail'),
    # path('create/', BreedCreateView.as_view(), name='breed_create'),
    # path('<int:pk>/update/', BreedUpdateView.as_view(), name='breed_update'),
    # path('<int:pk>/delete/', BreedDeleteView.as_view(), name='breed_delete'),

    # Uncomment the below lines if using function-based views
    path('breed/', breed_list, name='breed_list'),
    path('breed/<str:code>/', breed_detail, name='breed_detail'),
    path('breed/create/', breed_create, name='breed_create'),
    path('breed/<str:code>/update/', breed_update, name='breed_edit'),
    path('breed/<str:code>/delete/', breed_delete, name='breed_delete'),
    path('breeders/', breeders_list, name='breeders_list'),
    path('breeders/create/', breeders_create, name='breeders_create'),
    path('breeders/<str:batch>/', breeders_detail, name='breeders_detail'),
    path('breeders/<str:batch>/edit/', breeders_update, name='breeders_update'),
    path('breeders/<str:batch>/delete/', breeders_delete, name='breeders_delete'),
]
