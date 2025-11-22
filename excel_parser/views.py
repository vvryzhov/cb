"""
Views for Payroll BI - ФОТ
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Avg, Count
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.files.uploadedfile import InMemoryUploadedFile
import threading
import json

from .models import Department, Division, Group, Employee, SalaryHistory
from .services import DataLoaderService, AnalyticsService
from .serializers import (
    DepartmentSerializer, DivisionSerializer, GroupSerializer,
    EmployeeSerializer, SalaryHistorySerializer
)


# REST API ViewSets

class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с департаментами"""
    queryset = Department.objects.all().order_by('name')
    serializer_class = DepartmentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Загрузка департаментов из файла"""
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = DataLoaderService.load_departments_from_file(file)
            return Response({
                'success': True,
                'created': result['created'],
                'updated': result['updated']
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DivisionViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с отделами"""
    queryset = Division.objects.select_related('department').all().order_by('department', 'name')
    serializer_class = DivisionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'department__name']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        queryset = Division.objects.select_related('department').all()
        department_id = self.request.query_params.get('department_id', None)
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        return queryset
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Загрузка отделов из файла"""
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = DataLoaderService.load_divisions_from_file(file)
            return Response({
                'success': True,
                'created': result['created'],
                'updated': result['updated']
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GroupViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с группами"""
    queryset = Group.objects.select_related('division', 'division__department').all().order_by('division', 'name')
    serializer_class = GroupSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'division__name']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        queryset = Group.objects.select_related('division', 'division__department').all()
        division_id = self.request.query_params.get('division_id', None)
        if division_id:
            queryset = queryset.filter(division_id=division_id)
        return queryset
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Загрузка групп из файла"""
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = DataLoaderService.load_groups_from_file(file)
            return Response({
                'success': True,
                'created': result['created'],
                'updated': result['updated']
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с сотрудниками"""
    queryset = Employee.objects.select_related(
        'department', 'division', 'group',
        'functional_manager', 'line_manager'
    ).all()
    serializer_class = EmployeeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'login', 'position']
    ordering_fields = ['full_name', 'hire_date', 'current_salary']
    
    def get_queryset(self):
        queryset = Employee.objects.select_related(
            'department', 'division', 'group',
            'functional_manager', 'line_manager'
        ).with_current_income()
        
        # Фильтры
        department_id = self.request.query_params.get('department_id', None)
        division_id = self.request.query_params.get('division_id', None)
        group_id = self.request.query_params.get('group_id', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        if division_id:
            queryset = queryset.filter(division_id=division_id)
        if group_id:
            queryset = queryset.filter(group_id=group_id)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Загрузка сотрудников из файла"""
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = DataLoaderService.load_employees_from_file(file)
            return Response({
                'success': True,
                'created': result['created'],
                'updated': result['updated'],
                'errors': result.get('errors', [])
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def salary_history(self, request, pk=None):
        """История изменений зарплаты сотрудника"""
        employee = self.get_object()
        history = SalaryHistory.objects.filter(employee=employee).order_by('-change_date')
        serializer = SalaryHistorySerializer(history, many=True)
        return Response(serializer.data)


class SalaryHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с историей зарплаты"""
    queryset = SalaryHistory.objects.select_related('employee').all().order_by('-change_date')
    serializer_class = SalaryHistorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['employee__full_name', 'employee__login']
    ordering_fields = ['change_date', 'total_income_diff']
    
    def get_queryset(self):
        queryset = SalaryHistory.objects.select_related('employee').all()
        
        employee_id = self.request.query_params.get('employee_id', None)
        department_id = self.request.query_params.get('department_id', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if department_id:
            queryset = queryset.filter(employee__department_id=department_id)
        if date_from:
            queryset = queryset.filter(change_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(change_date__lte=date_to)
        
        return queryset


# Analytics Views

class AnalyticsViewSet(viewsets.ViewSet):
    """ViewSet для аналитики"""
    
    @action(detail=False, methods=['get'])
    def department_delta(self, request):
        """Дельта повышения департамента между годами"""
        department_id = request.query_params.get('department_id')
        year_from = request.query_params.get('year_from')
        year_to = request.query_params.get('year_to')
        
        if not all([department_id, year_from, year_to]):
            return Response(
                {'error': 'department_id, year_from, year_to are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = AnalyticsService.get_department_delta(
                int(department_id),
                int(year_from),
                int(year_to)
            )
            if result:
                return Response(result)
            else:
                return Response(
                    {'error': 'Department not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def custom_report(self, request):
        """Произвольный отчет с различными разрезами"""
        filters = request.data.get('filters', {})
        group_by = request.data.get('group_by', [])
        metrics = request.data.get('metrics', ['total_income', 'count'])
        
        try:
            result = AnalyticsService.get_custom_report(filters, group_by, metrics)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def salary_history_report(self, request):
        """Отчет по истории изменений зарплаты"""
        employee_id = request.query_params.get('employee_id')
        department_id = request.query_params.get('department_id')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        try:
            result = AnalyticsService.get_salary_history_report(
                employee_id=int(employee_id) if employee_id else None,
                department_id=int(department_id) if department_id else None,
                date_from=date_from,
                date_to=date_to
            )
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def fot_summary(self, request):
        """Сводный отчет по ФОТ"""
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        try:
            result = AnalyticsService.get_fot_summary(date_from, date_to)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Web Views

def index(request):
    """Главная страница"""
    departments_count = Department.objects.count()
    employees_count = Employee.objects.filter(is_active=True).count()
    
    # Сводная статистика по ФОТ
    fot_summary = Employee.objects.filter(is_active=True).with_current_income().aggregate(
        total_fot=Sum('_annotated_current_income'),
        avg_fot=Avg('_annotated_current_income'),
        total_salary=Sum('current_salary')
    )
    
    context = {
        'departments_count': departments_count,
        'employees_count': employees_count,
        'fot_summary': fot_summary,
    }
    return render(request, 'excel_parser/index.html', context)


def employees_list(request):
    """Список сотрудников с фильтрами"""
    employees = Employee.objects.select_related(
        'department', 'division', 'group'
    ).filter(is_active=True).with_current_income()
    
    # Фильтры
    search = request.GET.get('search', '')
    department_id = request.GET.get('department', '')
    division_id = request.GET.get('division', '')
    group_id = request.GET.get('group', '')
    
    if search:
        employees = employees.filter(
            Q(full_name__icontains=search) |
            Q(login__icontains=search) |
            Q(position__icontains=search)
        )
    if department_id:
        employees = employees.filter(department_id=department_id)
    if division_id:
        employees = employees.filter(division_id=division_id)
    if group_id:
        employees = employees.filter(group_id=group_id)
    
    # Сортировка
    sort_by = request.GET.get('sort', 'full_name')
    employees = employees.order_by(sort_by)
    
    # Пагинация
    paginator = Paginator(employees, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Справочники для фильтров
    departments = Department.objects.all().order_by('name')
    divisions = Division.objects.all().order_by('name') if not department_id else Division.objects.filter(department_id=department_id).order_by('name')
    groups = Group.objects.all().order_by('name') if not division_id else Group.objects.filter(division_id=division_id).order_by('name')
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'department_id': department_id,
        'division_id': division_id,
        'group_id': group_id,
        'departments': departments,
        'divisions': divisions,
        'groups': groups,
        'sort': sort_by,
    }
    return render(request, 'excel_parser/employees_list.html', context)


def employee_detail(request, employee_id):
    """Детальная информация о сотруднике"""
    employee = get_object_or_404(Employee, id=employee_id)
    salary_history = SalaryHistory.objects.filter(employee=employee).order_by('-change_date')[:20]
    
    context = {
        'employee': employee,
        'salary_history': salary_history,
    }
    return render(request, 'excel_parser/employee_detail.html', context)


def analytics(request):
    """Страница аналитики"""
    departments = Department.objects.all().order_by('name')
    
    context = {
        'departments': departments,
    }
    return render(request, 'excel_parser/analytics.html', context)


def custom_report_builder(request):
    """Конструктор произвольных отчетов"""
    departments = Department.objects.all().order_by('name')
    divisions = Division.objects.all().order_by('name')
    groups = Group.objects.all().order_by('name')
    
    context = {
        'departments': departments,
        'divisions': divisions,
        'groups': groups,
    }
    return render(request, 'excel_parser/custom_report_builder.html', context)
