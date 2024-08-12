from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from apps.accounts.models import UserSettings



class Command(BaseCommand):
    help = 'Create a new user with specified details'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='Email address of the user')
        parser.add_argument('--first_name', required=True, help='First name of the user')
        parser.add_argument('--last_name', required=True, help='Last name of the user')
        parser.add_argument('--primary_phone', required=True, help='Primary phone number of the user')
        parser.add_argument('--secondary_phone', help='Secondary phone number of the user')
        parser.add_argument('--date_of_birth', help='Date of birth of the user (YYYY-MM-DD)')
        parser.add_argument('--address', help='Address of the user')

    def handle(self, *args, **options):
        email = options['email']
        first_name = options['first_name']
        last_name = options['last_name']
        primary_phone = options['primary_phone']
        secondary_phone = options.get('secondary_phone')
        date_of_birth = options.get('date_of_birth')
        address = options.get('address')

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
            last_name=last_name
        )
        user.set_password(password)
        user.save()

        # Create user settings
        user_settings = UserSettings(user=user)
        user_settings.primary_phone = primary_phone
        user_settings.secondary_phone = secondary_phone
        user_settings.date_of_birth = date_of_birth
        user_settings.address = address
        user_settings.save()
        
        print(settings.DEFAULT_FROM_EMAIL)

        # Optionally send the password to the user via email
        send_mail(
            'Your account has been created',
            f'Your temporary password is: {password}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        self.stdout.write(self.style.SUCCESS(f'User {email} created successfully.'))
