from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from apps.human_resource.models import Employee, Department, Role
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.core.mail import send_mail
import random
import string

# Utility function to check user roles
def is_admin(user):
    return user.is_superuser

def is_manager(user):
    return user.groups.filter(name='Manager').exists()

def is_admin_or_manager(user):
    return is_admin(user) or is_manager(user)

# API view to get roles based on department
def roles_by_department(request):
    department_id = request.GET.get('department_id')
    
    if not department_id:
        return JsonResponse({'roles': []})

    roles = Role.objects.filter(department_id=department_id).values('id', 'name')
    return JsonResponse({'roles': list(roles)})

# View for creating a new employee
@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_employee(request):
    if request.method == 'POST':
        errors, employee, password = _validate_and_create_employee(request)
        if not errors:
            _send_account_creation_email(employee.user, request.POST.get('email'), password)
            messages.success(request, 'Employee created successfully!')
            return redirect('employee_list')

    return render(request, 'pages/human_resource/employee_create.html', {
        'departments': Department.objects.all(),
        'roles': Role.objects.none(),
    })

def _validate_and_create_employee(request):
    errors = {}
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    department_id = request.POST.get('department')
    role_id = request.POST.get('role')
    photo = request.FILES.get('photo')

    if not first_name:
        errors['first_name'] = 'First name is required.'
    if not last_name:
        errors['last_name'] = 'Last name is required.'
    if not email:
        errors['email'] = 'Email is required.'
    elif User.objects.filter(email=email).exists():
        errors['email'] = 'An account with this email already exists.'
    if not department_id:
        errors['department'] = 'Department is required.'

    department = get_object_or_404(Department, id=department_id)

    if department.name != 'Admin' and not role_id:
        errors['role'] = 'Role is required.'

    if errors:
        return errors, None, None

    # Generate a random password
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    user = User.objects.create_user(username=email, email=email, first_name=first_name, last_name=last_name, password=password)

    if role_id:
        role = Role.objects.get(id=role_id)
        if role.role_type == 'Manager':
            manager_group, _ = Group.objects.get_or_create(name='Manager')
            user.groups.add(manager_group)
    else:
        role = None

    employee = Employee.objects.create(user=user, department=department, role=role)

    if photo:
        fs = FileSystemStorage()
        employee.photo = fs.save(photo.name, photo)
        employee.save()

    return None, employee, password

def _send_account_creation_email(user, email, password):
    subject = 'Your Account Has Been Created'
    message = (
        f"Hi {user.first_name},\n\n"
        f"Your account has been created. You can log in using the following credentials:\n"
        f"Username: {user.username}\n"
        f"Password: {password}\n\n"
        f"Please change your password after logging in."
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

# View for listing employees with filtering options
@login_required
@user_passes_test(is_admin_or_manager, login_url='no_access')
def employee_list(request):
    department_id = request.GET.get('department')
    status = request.GET.get('status')
    search_query = request.GET.get('search')

    if is_admin(request.user):
        employees = Employee.objects.all()
    else:
        employees = Employee.objects.filter(department=request.user.employee.department)

    if department_id and is_admin(request.user):
        employees = employees.filter(department__id=department_id)
    if status:
        employees = employees.filter(status=status)
    if search_query:
        employees = employees.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(department__name__icontains=search_query) |
            Q(role__name__icontains=search_query)
        )

    employees = employees.select_related('department', 'role', 'user', 'user_settings')
    departments = Department.objects.all()

    return render(request, 'pages/human_resource/employee_list.html', {
        'employees': employees,
        'departments': departments,
        'selected_department': department_id,
        'selected_status': status,
        'search_query': search_query
    })

@login_required
def no_access(request):
    return render(request, 'pages/human_resource/no_access.html')

# View for displaying employee details
@login_required
@user_passes_test(is_admin_or_manager)
def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    departments = Department.objects.all()
    roles = Role.objects.all()
    
    context = {
        'employee': employee,
        'departments': departments,
        'roles': roles,
    }
    return render(request, 'pages/human_resource/employee_detail.html', context)

# View for updating employee role and department
@login_required
@user_passes_test(is_admin_or_manager)
def update_employee_role(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    if not (is_admin(request.user) or employee.department == request.user.employee.department):
        return redirect('no_access')

    if request.method == 'POST':
        new_role_id = request.POST.get('role')
        new_department_id = request.POST.get('department')

        if new_role_id and new_department_id:
            new_role = get_object_or_404(Role, id=new_role_id)
            new_department = get_object_or_404(Department, id=new_department_id)
            employee.role = new_role
            employee.department = new_department
            employee.save()

            # Redirect to the employee detail page after successful update
            return redirect(reverse('employee_detail', args=[employee.id]))

    # If not POST, render the form again (this is for GET requests)
    departments = Department.objects.all()
    roles = Role.objects.all()
    context = {
        'employee': employee,
        'departments': departments,
        'roles': roles,
    }
    return render(request, 'pages/human_resource/update_employee_role.html', context)

@login_required
@user_passes_test(is_admin_or_manager)
def employee_delete(request, id):
    employee = get_object_or_404(Employee, id=id)
    employee.delete()
    return redirect('employee_list')

@login_required
@user_passes_test(is_admin_or_manager)
def hire_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if not (is_admin(request.user) or employee.department == request.user.employee.department):
        return redirect('no_access')
    employee.hire()
    return redirect('employee_detail', employee_id=employee.id)

@login_required
@user_passes_test(is_admin_or_manager)
def fire_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if not (is_admin(request.user) or employee.department == request.user.employee.department):
        return redirect('no_access')
    employee.fire()
    return redirect('employee_detail', employee_id=employee.id)

@login_required
@user_passes_test(is_admin_or_manager)
def deactivate_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if not (is_admin(request.user) or employee.department == request.user.employee.department):
        return redirect('no_access')
    employee.deactivate()
    return redirect('employee_detail', employee_id=employee.id)

@login_required
@user_passes_test(is_admin_or_manager)
def reactivate_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if not (is_admin(request.user) or employee.department == request.user.employee.department):
        return redirect('no_access')
    employee.reactivate()
    return redirect('employee_detail', employee_id=employee.id)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'pages/human_resource/department_list.html', {'departments': departments})

@login_required
@user_passes_test(is_admin_or_manager)
def role_list(request):
    roles = Role.objects.all()
    return render(request, 'pages/human_resource/role_list.html', {'roles': roles})