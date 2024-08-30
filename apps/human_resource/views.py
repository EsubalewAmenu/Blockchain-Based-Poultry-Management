from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from .models import Employee, Department, Role

def is_admin_or_manager(user):
    return user.is_superuser or user.groups.filter(name='Manager').exists()

@user_passes_test(is_admin_or_manager)
def hire_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.user.is_superuser or employee.department == request.user.employee.department:
        employee.hire()
    return redirect('employee_detail', employee_id=employee.id)

@user_passes_test(is_admin_or_manager)
def fire_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.user.is_superuser or employee.department == request.user.employee.department:
        employee.fire()
    return redirect('employee_detail', employee_id=employee.id)

@user_passes_test(is_admin_or_manager)
def deactivate_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.user.is_superuser or employee.department == request.user.employee.department:
        employee.deactivate()
    return redirect('employee_detail', employee_id=employee.id)

@user_passes_test(is_admin_or_manager)
def reactivate_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.user.is_superuser or employee.department == request.user.employee.department:
        employee.reactivate()
    return redirect('employee_detail', employee_id=employee.id)

def employee_list(request, department_id=None, status=None):
    if department_id:
        employees = Employee.objects.filter(department__id=department_id)
    elif status:
        employees = Employee.objects.filter(status=status)
    else:
        employees = Employee.objects.all()
    employees = employees.select_related('department', 'role', 'user', 'user_settings')
    return render(request, 'human_resource/employee_list.html', {'employees': employees})

def department_list(request):
    departments = Department.objects.all()
    return render(request, 'human_resource/department_list.html', {'departments': departments})

def role_list(request):
    roles = Role.objects.all()
    return render(request, 'human_resource/role_list.html', {'roles': roles})

def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    return render(request, 'human_resource/employee_detail.html', {'employee': employee})