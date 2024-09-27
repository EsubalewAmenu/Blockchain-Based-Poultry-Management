from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('employees/create/', views.create_employee, name='employee_create'),
    path('employee/delete/<int:id>/', employee_delete, name='employee_delete'),
    path('employees/update/<int:employee_id>/', views.update_employee_role, name='update_employee_role'),
    path('employees/hire/<int:employee_id>/', views.hire_employee, name='hire_employee'),
    path('employees/fire/<int:employee_id>/', views.fire_employee, name='fire_employee'),
    path('employees/deactivate/<int:employee_id>/', views.deactivate_employee, name='deactivate_employee'),
    path('employees/reactivate/<int:employee_id>/', views.reactivate_employee, name='reactivate_employee'),
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/edit/<int:id>/', views.department_edit, name='department_edit'),
    path('departments/delete/<int:id>/', views.department_delete, name='department_delete'),
    path('roles/', views.role_list, name='role_list'),
    path('no-access/', views.no_access, name='no_access'),
    path('roles_by_department/', views.roles_by_department, name='roles_by_department'),
]