from django.urls import path
from . import views

urlpatterns = [
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('employees/hire/<int:employee_id>/', views.hire_employee, name='hire_employee'),
    path('employees/fire/<int:employee_id>/', views.fire_employee, name='fire_employee'),
    path('employees/deactivate/<int:employee_id>/', views.deactivate_employee, name='deactivate_employee'),
    path('employees/reactivate/<int:employee_id>/', views.reactivate_employee, name='reactivate_employee'),
    path('departments/', views.department_list, name='department_list'),
    path('roles/', views.role_list, name='role_list'),
]