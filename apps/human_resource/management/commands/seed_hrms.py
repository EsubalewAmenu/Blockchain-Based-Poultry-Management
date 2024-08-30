from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.accounts.models import UserSettings
from apps.human_resource.models import Department, Role, Employee

class Command(BaseCommand):
    help = 'Seed the database with initial HRMS data'

    def handle(self, *args, **kwargs):
        # Create Departments
        hatchery = Department.objects.create(name='Hatchery', description='Handles hatchery operations.')
        breeders_manager = Department.objects.create(name='Breeders Manager', description='Manages breeders.')
        inventory_manager = Department.objects.create(name='Inventory Manager', description='Manages inventory.')
        admin = Department.objects.create(name='Admin', description='Administrative department.')

        # Create Roles for each Department
        hatchery_manager_role = Role.objects.create(name='Hatchery Manager', role_type='Manager', department=hatchery)
        hatchery_staff_role = Role.objects.create(name='Hatchery Staff', role_type='Staff', department=hatchery)

        breeders_manager_role = Role.objects.create(name='Breeders Manager', role_type='Manager', department=breeders_manager)
        breeders_staff_role = Role.objects.create(name='Breeders Staff', role_type='Staff', department=breeders_manager)

        inventory_manager_role = Role.objects.create(name='Inventory Manager', role_type='Manager', department=inventory_manager)
        inventory_staff_role = Role.objects.create(name='Inventory Staff', role_type='Staff', department=inventory_manager)

        admin_role = Role.objects.create(name='Administrator', role_type='Manager', department=admin)

        # Create Users and Employees
        superuser = User.objects.create_superuser(username='admin', email='admin@gmail.com', password='adminpass')
        user_settings = UserSettings.objects.create(user=superuser)
        Employee.objects.create(user=superuser, department=admin, role=admin_role, user_settings=user_settings)

        manager_user = User.objects.create_user(username='manager', email='manager@gmail.com', password='managerpass')
        manager_settings = UserSettings.objects.create(user=manager_user)
        Employee.objects.create(user=manager_user, department=hatchery, role=hatchery_manager_role, user_settings=manager_settings)

        staff_user = User.objects.create_user(username='staff', email='staff@example.com', password='staffpass')
        staff_settings = UserSettings.objects.create(user=staff_user)
        Employee.objects.create(user=staff_user, department=hatchery, role=hatchery_staff_role, user_settings=staff_settings)
        
        manager_user = User.objects.create_user(username='manager1', email='manager@gmail.com', password='managerpass1')
        manager_settings = UserSettings.objects.create(user=manager_user)
        Employee.objects.create(user=manager_user, department=breeders_manager, role=breeders_manager_role, user_settings=manager_settings)

        staff_user = User.objects.create_user(username='staff1', email='staff@example.com', password='staffpass1')
        staff_settings = UserSettings.objects.create(user=staff_user)
        Employee.objects.create(user=staff_user, department=breeders_manager, role=breeders_staff_role, user_settings=staff_settings)
        
        manager_user = User.objects.create_user(username='manager2', email='manager@gmail.com', password='managerpass1')
        manager_settings = UserSettings.objects.create(user=manager_user)
        Employee.objects.create(user=manager_user, department=inventory_manager, role=inventory_manager_role, user_settings=manager_settings)

        staff_user = User.objects.create_user(username='staff2', email='staff@gmail.com', password='staffpass1')
        staff_settings = UserSettings.objects.create(user=staff_user)
        Employee.objects.create(user=staff_user, department=inventory_manager, role=inventory_staff_role, user_settings=staff_settings)

        self.stdout.write(self.style.SUCCESS('Successfully seeded HRMS data.'))