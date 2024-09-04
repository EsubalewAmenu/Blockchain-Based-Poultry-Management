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

    def _change_status(self, request, queryset, status, end_date=None):
        if self.has_change_permission(request):
            queryset.update(status=status, end_date=end_date)
            self.message_user(request, f"Selected employees have been {status.lower()}.")
        else:
            self.message_user(request, "You do not have permission to perform this action.", level='error')

    def hire_employees(self, request, queryset):
        self._change_status(request, queryset, 'Active', timezone.now().date())

    def fire_employees(self, request, queryset):
        self._change_status(request, queryset, 'Terminated', timezone.now().date())

    def deactivate_employees(self, request, queryset):
        self._change_status(request, queryset, 'Inactive')

    def reactivate_employees(self, request, queryset):
        self._change_status(request, queryset, 'Active')

    hire_employees.short_description = "Hire selected employees"
    fire_employees.short_description = "Fire selected employees"
    deactivate_employees.short_description = "Deactivate selected employees"
    reactivate_employees.short_description = "Reactivate selected employees"

admin.site.register(Department)
admin.site.register(Role)
admin.site.register(Employee, EmployeeAdmin)
