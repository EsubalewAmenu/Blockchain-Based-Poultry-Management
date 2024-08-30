from django.contrib import admin
from .models import Department, Role, Employee
from django.utils import timezone

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'role', 'get_full_name', 'status', 'start_date', 'end_date']
    search_fields = ['user__username', 'department__name', 'role__name']
    list_filter = ['department', 'role__role_type', 'status']
    ordering = ['department', 'role', 'user__username']
    actions = ['hire_employees', 'fire_employees', 'deactivate_employees', 'reactivate_employees']

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()

    def hire_employees(self, request, queryset):
        if self.has_change_permission(request):
            queryset.update(status='Active', start_date=timezone.now().date())
            self.message_user(request, "Selected employees have been hired.")
        else:
            self.message_user(request, "You do not have permission to perform this action.", level='error')

    def fire_employees(self, request, queryset):
        if self.has_change_permission(request):
            queryset.update(status='Terminated', end_date=timezone.now().date())
            self.message_user(request, "Selected employees have been terminated.")
        else:
            self.message_user(request, "You do not have permission to perform this action.", level='error')

    def deactivate_employees(self, request, queryset):
        if self.has_change_permission(request):
            queryset.update(status='Inactive')
            self.message_user(request, "Selected employees have been deactivated.")
        else:
            self.message_user(request, "You do not have permission to perform this action.", level='error')

    def reactivate_employees(self, request, queryset):
        if self.has_change_permission(request):
            queryset.update(status='Active')
            self.message_user(request, "Selected employees have been reactivated.")
        else:
            self.message_user(request, "You do not have permission to perform this action.", level='error')

    hire_employees.short_description = "Hire selected employees"
    fire_employees.short_description = "Fire selected employees"
    deactivate_employees.short_description = "Deactivate selected employees"
    reactivate_employees.short_description = "Reactivate selected employees"

admin.site.register(Department)
admin.site.register(Role)
admin.site.register(Employee, EmployeeAdmin)
