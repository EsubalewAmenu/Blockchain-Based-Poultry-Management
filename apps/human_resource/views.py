from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from apps.accounts.models import UserSettings
from apps.human_resource.models import Employee, Department, Role
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from apps.accounts.validators import validate_email
import random
import string

# Utility function to check user roles
def is_admin(user):
    return user.is_superuser

def is_manager(user):
    return user.groups.filter(name='Manager').exists()

def is_admin_or_manager(user):
    return is_admin(user) or is_manager(user)

def is_manager_of_department(user, department):
    return is_manager(user) and user.employee.department == department


# API view to get roles based on department
def roles_by_department(request):
    department_id = request.GET.get('department_id')

    if not department_id:
        return JsonResponse({'roles': []})

    roles_query = Role.objects.all()

    is_admin_department = Department.objects.filter(id=department_id, name__iexact='Admin').exists()

    if is_admin_department:
        roles = roles_query.values('id', 'name')
    else:
        roles = roles_query.filter(name__in=['Staff', 'Manager']).values('id', 'name')

    return JsonResponse({'roles': list(roles)})


# View for creating a new employee
@login_required
@user_passes_test(is_admin_or_manager)
def create_employee(request):
    if request.method == 'POST':
        errors, employee, password = _validate_and_create_employee(request)
        
        # If there are no errors, send the account creation email and redirect
        if not errors:
            _send_account_creation_email(employee.user, request.POST.get('email'), password)
            messages.success(request, 'Employee created successfully!', extra_tags='success')
            return redirect('employee_list')

        # If there are errors, re-render the form with the existing data and errors
        departments = Department.objects.all()
        if not is_admin(request.user):
            departments = departments.filter(id=request.user.employee.department_id)

        return render(request, 'pages/human_resource/employee_create.html', {
            'form_data': request.POST,
            'departments': departments,
            'roles': Role.objects.none(),
            'errors': errors,
        })

    # Handle GET request to render the empty form
    departments = Department.objects.all()
    if not is_admin(request.user):
        departments = departments.filter(id=request.user.employee.department_id)

    return render(request, 'pages/human_resource/employee_create.html', {
        'departments': departments,
        'roles': Role.objects.none(),
    })


# Helper function to validate and create an employee
def _validate_and_create_employee(request):
    errors = {}
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    phone = request.POST.get('phone').replace(' ', '')
    department_id = request.POST.get('department')
    role_id = request.POST.get('role')
    photo = request.FILES.get('photo')
    
    if email:
        if not validate_email(email):
            errors['email'] = 'This email address is not valid.'

    # Validate first name and last name
    if not first_name:
        errors['first_name'] = 'First name is required.'
    if not last_name:
        errors['last_name'] = 'Last name is required.'

    # Validate email
    if not email:
        errors['email'] = 'Email is required.'
    elif User.objects.filter(email=email).exists():
        errors['email'] = 'An account with this email already exists. Please use a different email.'

    # Validate department
    if not department_id:
        errors['department'] = 'Department is required.'

    department = get_object_or_404(Department, id=department_id)

    # Validate role if department is not "Admin"
    if department.name != 'Admin' and not role_id:
        errors['role'] = 'Role is required.'
        
     # Handle profile photo upload
    if photo:
        allowed_image_types = ['image/jpeg', 'image/png'] 
        if photo.content_type not in allowed_image_types:
            errors['role'] = "Invalid image format for profile photo. Only JPEG or PNG is allowed."

    # If there are errors, return them immediately
    if errors:
        return errors, None, None

    # Generate a random password
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    # Create the User object
    user = User.objects.create_user(
        username=email,
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password
    )
    user_settings = UserSettings(
        user=user,
        primary_phone = phone)
    user_settings.save()
    # Assign role if applicable
    if role_id:
        role = Role.objects.get(id=role_id)
        if role.role_type == 'Manager':
            manager_group, _ = Group.objects.get_or_create(name='Manager')
            user.groups.add(manager_group)
    else:
        role = None

    # Create the Employee object
    employee = Employee.objects.create(
        user=user,
        department=department,
        role=role,
        start_date=timezone.now().date()
    )

   
    if photo:
        fs = FileSystemStorage()
        employee.photo = fs.save(photo.name, photo)
        employee.save()
        

    return None, employee, password


# Helper function to send account creation email
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

    # Managers should only be able to view employees in their department
    if is_manager(request.user) and not is_manager_of_department(request.user, employee.department):
        return redirect('no_access')

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

        updated = False
        print(f"Received Role ID: {new_role_id}, Department ID: {new_department_id}")
        if new_role_id:
            new_role = get_object_or_404(Role, id=new_role_id)
            employee.role = new_role
            updated = True

        if new_department_id:
            new_department = get_object_or_404(Department, id=new_department_id)
            employee.department = new_department
            updated = True

        if updated:
            employee.save()
            return redirect(reverse('employee_detail', args=[employee.id]))

    departments = Department.objects.all()
    roles = Role.objects.all()
    context = {
        'employee': employee,
        'departments': departments,
        'roles': roles,
    }
    return render(request, 'pages/human_resource/employee_detail.html', context)

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
    if not (is_admin(request.user) or is_manager_of_department(request.user, employee.department)):
        return redirect('no_access')
    employee.hire()
    return redirect('employee_detail', employee_id=employee.id)

@login_required
@user_passes_test(is_admin_or_manager)
def fire_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if not (is_admin(request.user) or is_manager_of_department(request.user, employee.department)):
        return redirect('no_access')
    employee.fire()
    return redirect('employee_detail', employee_id=employee.id)

@login_required
@user_passes_test(is_admin_or_manager)
def deactivate_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if not (is_admin(request.user) or is_manager_of_department(request.user, employee.department)):
        return redirect('no_access')
    employee.deactivate()
    return redirect('employee_detail', employee_id=employee.id)

@login_required
@user_passes_test(is_admin_or_manager)
def reactivate_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if not (is_admin(request.user) or is_manager_of_department(request.user, employee.department)):
        return redirect('no_access')
    employee.reactivate()
    return redirect('employee_detail', employee_id=employee.id)

# department CRUD operation 
@login_required
@user_passes_test(is_admin)
def department_list(request):
    search_query = request.GET.get('search', '')
    sort = request.GET.get('sort', 'name')
    
    departments = Department.objects.all()

    if search_query:
        departments = departments.filter(name__icontains=search_query)

    if sort == 'name_desc':
        departments = departments.order_by('-name')
    else:
        departments = departments.order_by('name')

    context = {
        'departments': departments,
        'search_query': search_query,
        'sort': sort
    }
    return render(request, 'pages/human_resource/department_list.html', context)

@login_required
@user_passes_test(is_admin)
def department_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            Department.objects.create(name=name, description=description)
            messages.success(request, 'Department created successfully!')
            return redirect('department_list')
        else:
            messages.error(request, 'Please provide a valid department name.')
    
    return render(request, 'pages/human_resource/department_create.html')

@login_required
@user_passes_test(is_admin)
def department_edit(request, id):
    department = get_object_or_404(Department, id=id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            department.name = name
            department.description = description
            department.save()
            messages.success(request, 'Department updated successfully!')
            return redirect('department_list')
        else:
            messages.error(request, 'Please provide a valid department name.')
    
    context = {
        'department': department,
    }
    return render(request, 'pages/human_resource/department_create.html', context)

@login_required
@user_passes_test(is_admin)
def department_delete(request, id):
    department = get_object_or_404(Department, id=id)
    
    if request.method == 'POST':
        department.delete()
        messages.success(request, 'Department deleted successfully!')
        return redirect('department_list')

    context = {
        'department': department,
    }
    return render(request, 'pages/human_resource/department_list.html', {'department': department})

@login_required
@user_passes_test(is_admin_or_manager)
def role_list(request):
    roles = Role.objects.all()
    return render(request, 'pages/human_resource/role_list.html', {'roles': roles})