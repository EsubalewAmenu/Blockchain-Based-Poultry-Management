from django.core.management.base import BaseCommand
from apps.human_resource.models import Department, Role

class Command(BaseCommand):
    help = 'Seed the database with initial HRMS roles and departments'

    def handle(self, *args, **kwargs):
        departments_data = [
            {'name': 'Hatchery', 'description': 'Handles hatchery operations.'},
            {'name': 'Breeders Manager', 'description': 'Manages breeders.'},
            {'name': 'Inventory Manager', 'description': 'Manages inventory.'},
            {'name': 'Admin', 'description': 'Administrative department.'},
        ]
        
        roles_data = [
            {'name': 'Manager', 'role_type': 'Manager'},
            {'name': 'Staff', 'role_type': 'Staff'},
        ]

        for dept_data in departments_data:
            department, created = Department.objects.get_or_create(
                name=dept_data['name'], 
                defaults={'description': dept_data['description']}
            )
            if not created:
                self.stdout.write(self.style.WARNING(f'Department "{dept_data["name"]}" already exists.'))

            if dept_data['name'] == 'Admin':
                self._create_role('Administrator', 'Manager', department)
            else:
                for role_data in roles_data:
                    self._create_role(role_data['name'], role_data['role_type'], department)

        self.stdout.write(self.style.SUCCESS('Successfully seeded HRMS roles and departments.'))

    def _create_role(self, name, role_type, department):
        role, created = Role.objects.get_or_create(
            name=name, 
            role_type=role_type, 
            department=department
        )
        if not created:
            self.stdout.write(self.style.WARNING(f'Role "{name}" in "{department.name}" department already exists.'))
