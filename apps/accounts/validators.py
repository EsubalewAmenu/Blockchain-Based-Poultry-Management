from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


def validate_email_unique(value):
    exists = User.objects.filter(email__iexact=value)

    if exists:
        raise ValidationError('Someone is already using this email address. '
                              'Please try another.')


def validate_username_unique(value):
    exists = User.objects.filter(username__iexact=value)
    invalid_usernames = [
        'glucosetracker',
        'glucose',
        'diabetes',
        'admin',
        'help',
        'helpdesk',
        'sales',
        'support',
        'info',
        'warning',
        'success',
        'danger',
        'error',
        'debug',
        'alert',
        'alerts',
        'signup',
        'signin',
        'signout',
        'login',
        'logout',
        'activate',
        'register',
        'password',
    ]

    if exists or value in invalid_usernames:
        raise ValidationError('This username is not available. '
                              'Please try another.')
        
        
        
from rest_framework import serializers
from django.conf import settings
import smtplib
import dns.resolver
import re

def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        raise serializers.ValidationError({"error":"Invalid email format.", "status_code":400})

    domain = email.split('@')[1]
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_records = [str(mx_record.exchange) for mx_record in mx_records]
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return False

    if not verify_email_account(email, mx_records):
        return False  

    return email

def verify_email_account(email, mx_records):
    for mx_record in mx_records:
        try:
            server = smtplib.SMTP(mx_record)
            server.set_debuglevel(0)
            server.helo()
            server.mail(settings.DEFAULT_FROM_EMAIL)
            code, _ = server.rcpt(email)
            
            if code == 250:
                return True
        except Exception as e:
            print(f"An error occurred during SMTP verification with {mx_record}: {e}")
            return False
        finally:
            server.quit()

    return False