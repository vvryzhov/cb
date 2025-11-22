"""
Serializers for REST API
"""
from rest_framework import serializers
from .models import Department, Division, Group, Employee, SalaryHistory


class DepartmentSerializer(serializers.ModelSerializer):
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    divisions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'manager', 'manager_name',
            'divisions_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_divisions_count(self, obj):
        return obj.divisions.count()


class DivisionSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    groups_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Division
        fields = [
            'id', 'name', 'department', 'department_name',
            'manager', 'manager_name', 'groups_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_groups_count(self, obj):
        return obj.groups.count()


class GroupSerializer(serializers.ModelSerializer):
    division_name = serializers.CharField(source='division.name', read_only=True)
    department_name = serializers.CharField(source='division.department.name', read_only=True)
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    employees_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = [
            'id', 'name', 'division', 'division_name', 'department_name',
            'manager', 'manager_name', 'employees_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_employees_count(self, obj):
        return obj.employees.filter(is_active=True).count()


class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    division_name = serializers.CharField(source='division.name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    functional_manager_name = serializers.CharField(source='functional_manager.full_name', read_only=True)
    line_manager_name = serializers.CharField(source='line_manager.full_name', read_only=True)
    current_income = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'full_name', 'login',
            'department', 'department_name',
            'division', 'division_name',
            'group', 'group_name',
            'position',
            'functional_manager', 'functional_manager_name',
            'line_manager', 'line_manager_name',
            'hire_date',
            'current_salary', 'current_quarterly_bonus',
            'current_monthly_bonus', 'current_yearly_bonus',
            'current_income',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'current_income']


class SalaryHistorySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_login = serializers.CharField(source='employee.login', read_only=True)
    
    class Meta:
        model = SalaryHistory
        fields = [
            'id', 'employee', 'employee_name', 'employee_login',
            'change_date',
            'salary_before', 'salary_after', 'salary_diff',
            'quarterly_bonus_before', 'quarterly_bonus_after', 'quarterly_bonus_diff',
            'monthly_bonus_before', 'monthly_bonus_after', 'monthly_bonus_diff',
            'yearly_bonus_before', 'yearly_bonus_after', 'yearly_bonus_diff',
            'total_income_before', 'total_income_after', 'total_income_diff',
            'comment', 'created_at'
        ]
        read_only_fields = [
            'salary_diff', 'quarterly_bonus_diff', 'monthly_bonus_diff',
            'yearly_bonus_diff', 'total_income_before', 'total_income_after',
            'total_income_diff', 'created_at'
        ]
