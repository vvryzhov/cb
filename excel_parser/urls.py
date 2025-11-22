"""
URL configuration for excel_parser app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, DivisionViewSet, GroupViewSet,
    EmployeeViewSet, SalaryHistoryViewSet, AnalyticsViewSet,
    index, employees_list, employee_detail, analytics, custom_report_builder
)

# API Router
router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'divisions', DivisionViewSet, basename='division')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'salary-history', SalaryHistoryViewSet, basename='salaryhistory')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Web endpoints
    path('', index, name='index'),
    path('employees/', employees_list, name='employees_list'),
    path('employees/<int:employee_id>/', employee_detail, name='employee_detail'),
    path('analytics/', analytics, name='analytics'),
    path('custom-report/', custom_report_builder, name='custom_report_builder'),
]
