"""
Сервис для аналитики и отчетов
"""
from django.db.models import (
    Sum, Avg, Count, Q, F, DecimalField, Case, When, Value
)
from django.db.models.functions import ExtractYear, ExtractQuarter, TruncDate
from decimal import Decimal
from datetime import date, datetime
from ..models import Employee, Department, Division, Group, SalaryHistory


class AnalyticsService:
    """Сервис для аналитики ФОТ"""
    
    @staticmethod
    def get_department_delta(department_id, year_from, year_to):
        """
        Получить дельту повышения департамента между годами
        
        Args:
            department_id: ID департамента
            year_from: Год начала (например, 2023)
            year_to: Год окончания (например, 2024)
        
        Returns:
            dict с данными о дельте
        """
        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return None
        
        # Получаем сотрудников департамента с вычисляемым current_income
        employees = Employee.objects.filter(department=department, is_active=True).with_current_income()
        
        # Получаем историю изменений за указанные годы
        history_from = SalaryHistory.objects.filter(
            employee__in=employees,
            change_date__year=year_from
        ).aggregate(
            total_income=Sum('total_income_after'),
            avg_income=Avg('total_income_after'),
            count=Count('id')
        )
        
        history_to = SalaryHistory.objects.filter(
            employee__in=employees,
            change_date__year=year_to
        ).aggregate(
            total_income=Sum('total_income_after'),
            avg_income=Avg('total_income_after'),
            count=Count('id')
        )
        
        # Текущие показатели сотрудников
        current_stats = employees.with_current_income().aggregate(
            total_current=Sum('current_income'),
            avg_current=Avg('current_income'),
            count=Count('id')
        )
        
        # Вычисляем дельту
        total_from = history_from['total_income'] or Decimal('0.00')
        total_to = history_to['total_income'] or current_stats['total_current'] or Decimal('0.00')
        delta_total = total_to - total_from
        
        avg_from = history_from['avg_income'] or Decimal('0.00')
        avg_to = history_to['avg_income'] or current_stats['avg_current'] or Decimal('0.00')
        delta_avg = avg_to - avg_from
        
        return {
            'department': department.name,
            'year_from': year_from,
            'year_to': year_to,
            'total_income_from': float(total_from),
            'total_income_to': float(total_to),
            'delta_total': float(delta_total),
            'delta_percent': float((delta_total / total_from * 100) if total_from > 0 else 0),
            'avg_income_from': float(avg_from),
            'avg_income_to': float(avg_to),
            'delta_avg': float(delta_avg),
            'employees_count': current_stats['count']
        }
    
    @staticmethod
    def get_custom_report(filters=None, group_by=None, metrics=None):
        """
        Создать произвольный отчет с различными разрезами
        
        Args:
            filters: dict с фильтрами (department, division, group, date_from, date_to)
            group_by: список полей для группировки ('department', 'division', 'group', 'year', 'quarter')
            metrics: список метрик ('total_income', 'avg_income', 'count', 'salary_diff')
        
        Returns:
            dict с данными отчета
        """
        if filters is None:
            filters = {}
        if group_by is None:
            group_by = []
        if metrics is None:
            metrics = ['total_income', 'count']
        
        # Базовый queryset с вычисляемым current_income
        queryset = Employee.objects.filter(is_active=True).with_current_income()
        
        # Применяем фильтры
        if filters.get('department'):
            queryset = queryset.filter(department_id=filters['department'])
        if filters.get('division'):
            queryset = queryset.filter(division_id=filters['division'])
        if filters.get('group'):
            queryset = queryset.filter(group_id=filters['group'])
        if filters.get('date_from'):
            queryset = queryset.filter(hire_date__gte=filters['date_from'])
        if filters.get('date_to'):
            queryset = queryset.filter(hire_date__lte=filters['date_to'])
        
        # Группировка и агрегация
        annotations = {}
        
        # Метрики
        if 'total_income' in metrics:
            annotations['total_income'] = Sum('current_income')
        if 'avg_income' in metrics:
            annotations['avg_income'] = Avg('current_income')
        if 'count' in metrics:
            annotations['count'] = Count('id')
        if 'total_salary' in metrics:
            annotations['total_salary'] = Sum('current_salary')
        if 'avg_salary' in metrics:
            annotations['avg_salary'] = Avg('current_salary')
        
        # Группировка
        group_by_fields = []
        if 'department' in group_by:
            group_by_fields.append('department__name')
        if 'division' in group_by:
            group_by_fields.append('division__name')
        if 'group' in group_by:
            group_by_fields.append('group__name')
        
        if group_by_fields:
            queryset = queryset.values(*group_by_fields).annotate(**annotations)
        else:
            queryset = queryset.aggregate(**annotations)
        
        return {
            'filters': filters,
            'group_by': group_by,
            'metrics': metrics,
            'data': list(queryset) if group_by_fields else queryset
        }
    
    @staticmethod
    def get_salary_history_report(employee_id=None, department_id=None, date_from=None, date_to=None):
        """
        Отчет по истории изменений зарплаты
        
        Args:
            employee_id: ID сотрудника (опционально)
            department_id: ID департамента (опционально)
            date_from: Дата начала периода
            date_to: Дата окончания периода
        
        Returns:
            dict с данными отчета
        """
        queryset = SalaryHistory.objects.all()
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if department_id:
            queryset = queryset.filter(employee__department_id=department_id)
        if date_from:
            queryset = queryset.filter(change_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(change_date__lte=date_to)
        
        # Группировка по годам и кварталам
        history_by_period = queryset.annotate(
            year=ExtractYear('change_date'),
            quarter=ExtractQuarter('change_date')
        ).values('year', 'quarter').annotate(
            total_changes=Count('id'),
            total_salary_increase=Sum('salary_diff'),
            total_income_increase=Sum('total_income_diff'),
            avg_salary_increase=Avg('salary_diff'),
            avg_income_increase=Avg('total_income_diff')
        ).order_by('year', 'quarter')
        
        return {
            'period': {
                'from': date_from,
                'to': date_to
            },
            'data': list(history_by_period)
        }
    
    @staticmethod
    def get_fot_summary(date_from=None, date_to=None):
        """
        Сводный отчет по ФОТ
        
        Args:
            date_from: Дата начала периода
            date_to: Дата окончания периода
        
        Returns:
            dict с сводными данными
        """
        employees = Employee.objects.filter(is_active=True).with_current_income()
        
        # Текущий ФОТ
        current_fot = employees.aggregate(
            total=Sum('current_income'),
            avg=Avg('current_income'),
            count=Count('id')
        )
        
        # ФОТ по департаментам
        fot_by_department = employees.values('department__name').annotate(
            total=Sum('current_income'),
            avg=Avg('current_income'),
            count=Count('id')
        ).order_by('-total')
        
        # Изменения за период
        history_changes = None
        if date_from and date_to:
            history_changes = SalaryHistory.objects.filter(
                change_date__gte=date_from,
                change_date__lte=date_to
            ).aggregate(
                total_increase=Sum('total_income_diff'),
                avg_increase=Avg('total_income_diff'),
                changes_count=Count('id')
            )
        
        return {
            'current_fot': current_fot,
            'fot_by_department': list(fot_by_department),
            'period_changes': history_changes,
            'period': {
                'from': date_from,
                'to': date_to
            }
        }

