from django.contrib import admin
from .models import Department, Division, Group, Employee, SalaryHistory


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'manager', 'created_at']
    list_filter = ['department', 'created_at']
    search_fields = ['name', 'department__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'division', 'manager', 'created_at']
    list_filter = ['division__department', 'division', 'created_at']
    search_fields = ['name', 'division__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'login', 'department', 'division', 'group',
        'position', 'current_salary', 'current_income', 'hire_date', 'is_active'
    ]
    list_filter = ['department', 'division', 'group', 'is_active', 'hire_date']
    search_fields = ['full_name', 'login', 'position']
    readonly_fields = ['created_at', 'updated_at', 'current_income']
    fieldsets = (
        ('Основная информация', {
            'fields': ('full_name', 'login', 'position', 'hire_date', 'is_active')
        }),
        ('Организационная структура', {
            'fields': ('department', 'division', 'group')
        }),
        ('Руководители', {
            'fields': ('functional_manager', 'line_manager')
        }),
        ('Текущие финансовые показатели (гросс)', {
            'fields': (
                'current_salary',
                'current_quarterly_bonus',
                'current_monthly_bonus',
                'current_yearly_bonus',
                'current_income'
            )
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(SalaryHistory)
class SalaryHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'change_date', 'salary_diff', 'total_income_diff', 'created_at'
    ]
    list_filter = ['change_date', 'created_at']
    search_fields = ['employee__full_name', 'employee__login']
    readonly_fields = [
        'salary_diff', 'quarterly_bonus_diff', 'monthly_bonus_diff',
        'yearly_bonus_diff', 'total_income_before', 'total_income_after',
        'total_income_diff', 'created_at'
    ]
    date_hierarchy = 'change_date'
