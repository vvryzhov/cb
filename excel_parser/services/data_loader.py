"""
Сервис для загрузки данных из Excel/CSV
"""
import pandas as pd
from django.core.files.uploadedfile import InMemoryUploadedFile
from ..models import (
    Department, Division, Group, Employee, SalaryHistory
)
from django.utils import timezone
from decimal import Decimal
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DataLoaderService:
    """Сервис для загрузки данных из файлов"""
    
    @staticmethod
    def parse_date(date_value):
        """Парсинг даты из различных форматов"""
        if pd.isna(date_value):
            return None
        if isinstance(date_value, str):
            try:
                return datetime.strptime(date_value, '%Y-%m-%d').date()
            except:
                try:
                    return datetime.strptime(date_value, '%d.%m.%Y').date()
                except:
                    return None
        if isinstance(date_value, pd.Timestamp):
            return date_value.date()
        return None
    
    @staticmethod
    def parse_decimal(value):
        """Парсинг десятичного числа"""
        if pd.isna(value):
            return Decimal('0.00')
        try:
            return Decimal(str(value))
        except:
            return Decimal('0.00')
    
    @staticmethod
    def load_departments_from_file(file):
        """Загрузка департаментов из файла"""
        try:
            # Если это путь к файлу, используем его напрямую, иначе временный файл
            if isinstance(file, str):
                df = pd.read_excel(file, engine='openpyxl')
            else:
                df = pd.read_excel(file, engine='openpyxl')
            created = 0
            updated = 0
            
            for _, row in df.iterrows():
                name = str(row.get('Название', row.get('name', ''))).strip()
                if not name:
                    continue
                
                dept, created_flag = Department.objects.get_or_create(
                    name=name,
                    defaults={}
                )
                
                if created_flag:
                    created += 1
                else:
                    updated += 1
            
            return {'created': created, 'updated': updated}
        except Exception as e:
            logger.error(f"Error loading departments: {str(e)}")
            raise
    
    @staticmethod
    def load_divisions_from_file(file):
        """Загрузка отделов из файла"""
        try:
            df = pd.read_excel(file, engine='openpyxl')
            created = 0
            updated = 0
            
            for _, row in df.iterrows():
                dept_name = str(row.get('Департамент', row.get('department', ''))).strip()
                div_name = str(row.get('Название', row.get('name', ''))).strip()
                
                if not dept_name or not div_name:
                    continue
                
                try:
                    department = Department.objects.get(name=dept_name)
                except Department.DoesNotExist:
                    logger.warning(f"Department {dept_name} not found, skipping division {div_name}")
                    continue
                
                div, created_flag = Division.objects.get_or_create(
                    department=department,
                    name=div_name,
                    defaults={}
                )
                
                if created_flag:
                    created += 1
                else:
                    updated += 1
            
            return {'created': created, 'updated': updated}
        except Exception as e:
            logger.error(f"Error loading divisions: {str(e)}")
            raise
    
    @staticmethod
    def load_groups_from_file(file):
        """Загрузка групп из файла"""
        try:
            df = pd.read_excel(file, engine='openpyxl')
            created = 0
            updated = 0
            
            for _, row in df.iterrows():
                div_name = str(row.get('Отдел', row.get('division', ''))).strip()
                group_name = str(row.get('Название', row.get('name', ''))).strip()
                
                if not div_name or not group_name:
                    continue
                
                try:
                    division = Division.objects.get(name=div_name)
                except Division.DoesNotExist:
                    logger.warning(f"Division {div_name} not found, skipping group {group_name}")
                    continue
                
                group, created_flag = Group.objects.get_or_create(
                    division=division,
                    name=group_name,
                    defaults={}
                )
                
                if created_flag:
                    created += 1
                else:
                    updated += 1
            
            return {'created': created, 'updated': updated}
        except Exception as e:
            logger.error(f"Error loading groups: {str(e)}")
            raise
    
    @staticmethod
    def load_employees_from_file(file, update_salary_history=True):
        """Загрузка сотрудников из файла"""
        try:
            df = pd.read_excel(file, engine='openpyxl')
            created = 0
            updated = 0
            errors = []
            
            for idx, row in df.iterrows():
                try:
                    login = str(row.get('Логин', row.get('login', ''))).strip()
                    if not login:
                        errors.append(f"Row {idx + 2}: Missing login")
                        continue
                    
                    # Получаем или создаем сотрудника
                    employee, employee_created = Employee.objects.get_or_create(
                        login=login,
                        defaults={
                            'full_name': str(row.get('ФИО', row.get('full_name', ''))).strip(),
                            'position': str(row.get('Должность', row.get('position', ''))).strip() or None,
                            'hire_date': DataLoaderService.parse_date(
                                row.get('Дата принятия', row.get('hire_date'))
                            ) or timezone.now().date(),
                        }
                    )
                    
                    # Обновляем организационную структуру
                    dept_name = str(row.get('Департамент', row.get('department', ''))).strip()
                    div_name = str(row.get('Отдел', row.get('division', ''))).strip()
                    group_name = str(row.get('Группа', row.get('group', ''))).strip()
                    
                    if dept_name:
                        try:
                            employee.department = Department.objects.get(name=dept_name)
                        except Department.DoesNotExist:
                            pass
                    
                    if div_name:
                        try:
                            employee.division = Division.objects.get(name=div_name)
                        except Division.DoesNotExist:
                            pass
                    
                    if group_name:
                        try:
                            employee.group = Group.objects.get(name=group_name)
                        except Group.DoesNotExist:
                            pass
                    
                    # Обновляем руководителей
                    func_manager_login = str(row.get('Функциональный руководитель', row.get('functional_manager', ''))).strip()
                    line_manager_login = str(row.get('Линейный руководитель', row.get('line_manager', ''))).strip()
                    
                    if func_manager_login:
                        try:
                            employee.functional_manager = Employee.objects.get(login=func_manager_login)
                        except Employee.DoesNotExist:
                            pass
                    
                    if line_manager_login:
                        try:
                            employee.line_manager = Employee.objects.get(login=line_manager_login)
                        except Employee.DoesNotExist:
                            pass
                    
                    # Сохраняем старые значения для истории
                    old_salary = employee.current_salary
                    old_quarterly = employee.current_quarterly_bonus
                    old_monthly = employee.current_monthly_bonus
                    old_yearly = employee.current_yearly_bonus
                    
                    # Обновляем финансовые показатели
                    employee.current_salary = DataLoaderService.parse_decimal(
                        row.get('Оклад', row.get('salary', row.get('current_salary')))
                    )
                    employee.current_quarterly_bonus = DataLoaderService.parse_decimal(
                        row.get('Квартальная премия', row.get('quarterly_bonus'))
                    )
                    employee.current_monthly_bonus = DataLoaderService.parse_decimal(
                        row.get('Месячная премия', row.get('monthly_bonus'))
                    )
                    employee.current_yearly_bonus = DataLoaderService.parse_decimal(
                        row.get('Годовая премия', row.get('yearly_bonus'))
                    )
                    
                    employee.save()
                    
                    # Создаем запись в истории, если были изменения
                    if update_salary_history and (
                        old_salary != employee.current_salary or
                        old_quarterly != employee.current_quarterly_bonus or
                        old_monthly != employee.current_monthly_bonus or
                        old_yearly != employee.current_yearly_bonus
                    ):
                        SalaryHistory.objects.create(
                            employee=employee,
                            change_date=timezone.now().date(),
                            salary_before=old_salary,
                            salary_after=employee.current_salary,
                            quarterly_bonus_before=old_quarterly,
                            quarterly_bonus_after=employee.current_quarterly_bonus,
                            monthly_bonus_before=old_monthly,
                            monthly_bonus_after=employee.current_monthly_bonus,
                            yearly_bonus_before=old_yearly,
                            yearly_bonus_after=employee.current_yearly_bonus,
                            comment=f"Загружено из файла"
                        )
                    
                    if employee_created:
                        created += 1
                    else:
                        updated += 1
                        
                except Exception as e:
                    errors.append(f"Row {idx + 2}: {str(e)}")
                    logger.error(f"Error processing employee row {idx + 2}: {str(e)}")
            
            return {
                'created': created,
                'updated': updated,
                'errors': errors
            }
        except Exception as e:
            logger.error(f"Error loading employees: {str(e)}")
            raise

