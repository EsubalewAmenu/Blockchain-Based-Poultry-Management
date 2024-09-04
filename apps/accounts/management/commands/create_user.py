from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from apps.accounts.models import UserSettings
from apps.human_resource.models import Department, Role, Employee

class Command(BaseCommand):
    help = 'Create a new user with specified details and optionally assign a role and department'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='Email address of the user')
        parser.add_argument('--first_name', required=True, help='First name of the user')
        parser.add_argument('--last_name', required=True, help='Last name of the user')
        parser.add_argument('--primary_phone', required=True, help='Primary phone number of the user')
        parser.add_argument('--secondary_phone', help='Secondary phone number of the user')
        parser.add_argument('--date_of_birth', help='Date of birth of the user (YYYY-MM-DD)')
        parser.add_argument('--address', help='Address of the user')
        parser.add_argument('--role', required=True, help='Role name to assign to the user')
        parser.add_argument('--department', help='Department name to assign to the user (required for Manager role)')
        parser.add_argument('--is_superuser', action='store_true', help='Make this user a superuser')

    def handle(self, *args, **options):
        email = options['email']
        first_name = options['first_name']
        last_name = options['last_name']
        primary_phone = options['primary_phone']
        secondary_phone = options.get('secondary_phone')
        date_of_birth = options.get('date_of_birth')
        address = options.get('address')
        role_name = options['role']
        department_name = options.get('department')
        is_superuser = options.get('is_superuser', False)

        # Basic validation
        if not email or not first_name or not last_name:
            self.stdout.write(self.style.ERROR('Email, first name, and last name are required.'))
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR('Email is already registered.'))
            return

        # Create username from email
        username = email.split('@')[0]

        # Generate a random password
        password = get_random_string(length=8, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)')

        # Create the user
        user = User.objects.create(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_superuser=is_superuser,
            is_staff=True,  # Superusers are always staff; other users can also be staff
        )
        user.set_password(password)
        user.save()

        # Create user settings
        user_settings = UserSettings(
            user=user,
            primary_phone=primary_phone,
            secondary_phone=secondary_phone,
            date_of_birth=date_of_birth,
            address=address,
        )
        user_settings.save()

        # Assign the user to the role (and department if necessary)
        try:
            if role_name == 'Manager':
                if not department_name:
                    self.stdout.write(self.style.ERROR('Department is required when assigning a Manager role.'))
                    return
                department = Department.objects.get(name=department_name)
                role = Role.objects.get(name=role_name, department=department)
            else:
                role = Role.objects.get(name=role_name)
                department = None if is_superuser else Department.objects.get(name=department_name)

        except (Department.DoesNotExist, Role.DoesNotExist) as e:
            self.stdout.write(self.style.ERROR('Department or Role not found.'))
            return

        # Create the employee profile only if the user is not a superuser
        if not is_superuser:
            Employee.objects.create(
                user=user,
                department=department,
                role=role,
                user_settings=user_settings,
                status='Active',
            )

        # Optionally send the password to the user via email
        send_mail(
            'Your account has been created',
            f'Your temporary password is: {password}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        self.stdout.write(self.style.SUCCESS(f'User {email} created successfully and assigned to {role_name}{" in " + department_name if department_name else ""}.'))