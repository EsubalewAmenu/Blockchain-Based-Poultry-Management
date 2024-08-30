from django.db import models
from django.contrib.auth.models import User
from apps.accounts.models import UserSettings
from apps.core.models import TimeStampedModel
from django.utils import timezone

class Department(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Role(models.Model):
    ROLE_TYPES = (
        ('Manager', 'Manager'),
        ('Staff', 'Staff'),
    )
    name = models.CharField(max_length=50)
    role_type = models.CharField(max_length=20, choices=ROLE_TYPES)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='roles')

    def __str__(self):
        return f"{self.name} ({self.role_type} in {self.department.name})"

class Employee(TimeStampedModel):
    EMPLOYMENT_STATUS = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Terminated', 'Terminated'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='employees')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, related_name='employees')
    user_settings = models.OneToOneField(UserSettings, on_delete=models.CASCADE, related_name='employee')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS, default='Active')
    supervisor = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subordinates')

    def __str__(self):
        return f"{self.user.username} - {self.department.name} - {self.role.name}"

    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def hire(self):
        self.status = 'Active'
        self.start_date = timezone.now().date()
        self.save()

    def fire(self):
        self.status = 'Terminated'
        self.end_date = timezone.now().date()
        self.save()

    def deactivate(self):
        self.status = 'Inactive'
        self.save()

    def reactivate(self):
        self.status = 'Active'
        self.save()

    class Meta:
        verbose_name_plural = "Employees"