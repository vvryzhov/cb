"""
Management command для генерации тестовых данных
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import random

from excel_parser.models import Department, Division, Group, Employee, SalaryHistory


class Command(BaseCommand):
    help = 'Генерирует тестовые данные: департаменты, отделы, группы и 100 сотрудников'

    def add_arguments(self, parser):
        parser.add_argument(
            '--employees',
            type=int,
            default=100,
            help='Количество сотрудников для генерации (по умолчанию 100)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить существующие данные перед генерацией',
        )

    def handle(self, *args, **options):
        employees_count = options['employees']
        clear_data = options['clear']

        if clear_data:
            self.stdout.write(self.style.WARNING('Очистка существующих данных...'))
            Employee.objects.all().delete()
            SalaryHistory.objects.all().delete()
            Group.objects.all().delete()
            Division.objects.all().delete()
            Department.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Данные очищены'))

        # Генерация департаментов
        self.stdout.write('Создание департаментов...')
        departments_data = [
            'Разработка',
            'Продажи',
            'Маркетинг',
            'HR',
            'Финансы',
            'Операции',
            'Поддержка',
            'Аналитика',
        ]
        departments = []
        for dept_name in departments_data:
            dept, created = Department.objects.get_or_create(name=dept_name)
            departments.append(dept)
            if created:
                self.stdout.write(f'  Создан департамент: {dept_name}')

        # Генерация отделов
        self.stdout.write('Создание отделов...')
        divisions_data = {
            'Разработка': ['Backend', 'Frontend', 'Mobile', 'DevOps'],
            'Продажи': ['B2B', 'B2C', 'Партнеры'],
            'Маркетинг': ['Digital', 'Контент', 'Аналитика'],
            'HR': ['Рекрутинг', 'Обучение', 'Администрация'],
            'Финансы': ['Бухгалтерия', 'Планирование', 'Аудит'],
            'Операции': ['Логистика', 'Склад', 'Доставка'],
            'Поддержка': ['Техподдержка', 'Клиентский сервис'],
            'Аналитика': ['BI', 'Data Science', 'Исследования'],
        }
        divisions = []
        for dept in departments:
            if dept.name in divisions_data:
                for div_name in divisions_data[dept.name]:
                    div, created = Division.objects.get_or_create(
                        department=dept,
                        name=div_name
                    )
                    divisions.append(div)
                    if created:
                        self.stdout.write(f'  Создан отдел: {dept.name} - {div_name}')

        # Генерация групп
        self.stdout.write('Создание групп...')
        groups = []
        for div in divisions:
            # Создаем 1-2 группы на отдел
            num_groups = random.randint(1, 2)
            for i in range(num_groups):
                group_name = f'Группа {i+1}'
                group, created = Group.objects.get_or_create(
                    division=div,
                    name=group_name
                )
                groups.append(group)
                if created:
                    self.stdout.write(f'  Создана группа: {div.department.name} - {div.name} - {group_name}')

        # Генерация сотрудников
        self.stdout.write(f'Создание {employees_count} сотрудников...')
        
        # Списки для генерации данных
        first_names = [
            'Иван', 'Петр', 'Александр', 'Дмитрий', 'Сергей', 'Андрей', 'Алексей',
            'Максим', 'Владимир', 'Николай', 'Михаил', 'Павел', 'Роман', 'Олег',
            'Анна', 'Мария', 'Елена', 'Ольга', 'Татьяна', 'Наталья', 'Ирина',
            'Светлана', 'Екатерина', 'Юлия', 'Анастасия', 'Дарья', 'Виктория'
        ]
        last_names = [
            'Иванов', 'Петров', 'Сидоров', 'Смирнов', 'Кузнецов', 'Попов', 'Соколов',
            'Лебедев', 'Козлов', 'Новиков', 'Морозов', 'Петров', 'Волков', 'Соловьев',
            'Васильев', 'Зайцев', 'Павлов', 'Семенов', 'Голубев', 'Виноградов'
        ]
        middle_names = [
            'Иванович', 'Петрович', 'Александрович', 'Дмитриевич', 'Сергеевич',
            'Андреевич', 'Алексеевич', 'Максимович', 'Владимирович', 'Николаевич',
            'Ивановна', 'Петровна', 'Александровна', 'Дмитриевна', 'Сергеевна'
        ]
        positions = [
            'Разработчик', 'Старший разработчик', 'Ведущий разработчик',
            'Менеджер по продажам', 'Старший менеджер', 'Директор по продажам',
            'Маркетолог', 'Старший маркетолог', 'Руководитель маркетинга',
            'HR-менеджер', 'Рекрутер', 'Руководитель HR',
            'Бухгалтер', 'Финансовый аналитик', 'CFO',
            'Операционный менеджер', 'Логист', 'Руководитель операций',
            'Специалист поддержки', 'Старший специалист', 'Руководитель поддержки',
            'Аналитик данных', 'Data Scientist', 'Руководитель аналитики'
        ]

        # Генерируем сотрудников
        created_employees = []
        for i in range(employees_count):
            # Случайные данные
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            middle_name = random.choice(middle_names)
            full_name = f"{last_name} {first_name} {middle_name}"
            login = f"user_{i+1:03d}"
            
            # Случайная организационная структура
            department = random.choice(departments)
            department_divisions = [d for d in divisions if d.department == department]
            if department_divisions:
                division = random.choice(department_divisions)
                division_groups = [g for g in groups if g.division == division]
                group = random.choice(division_groups) if division_groups else None
            else:
                division = None
                group = None
            
            position = random.choice(positions)
            
            # Дата принятия (от 1 до 5 лет назад)
            years_ago = random.randint(1, 5)
            hire_date = date.today() - timedelta(days=365 * years_ago)
            
            # Финансовые показатели (гросс)
            # Оклад от 50,000 до 500,000
            current_salary = Decimal(random.randint(50000, 500000))
            # Премии (0-50% от оклада)
            current_quarterly_bonus = Decimal(random.randint(0, int(current_salary * 0.5)))
            current_monthly_bonus = Decimal(random.randint(0, int(current_salary * 0.3)))
            current_yearly_bonus = Decimal(random.randint(0, int(current_salary * 2)))
            
            # Создаем сотрудника
            employee = Employee.objects.create(
                full_name=full_name,
                login=login,
                department=department,
                division=division,
                group=group,
                position=position,
                hire_date=hire_date,
                current_salary=current_salary,
                current_quarterly_bonus=current_quarterly_bonus,
                current_monthly_bonus=current_monthly_bonus,
                current_yearly_bonus=current_yearly_bonus,
                is_active=True
            )
            created_employees.append(employee)
            
            # Создаем историю изменений зарплаты (1-3 записи на сотрудника)
            num_history_records = random.randint(1, 3)
            previous_salary = Decimal('0.00')
            previous_quarterly = Decimal('0.00')
            previous_monthly = Decimal('0.00')
            previous_yearly = Decimal('0.00')
            
            for j in range(num_history_records):
                # Дата изменения (между датой приема и сегодня)
                days_since_hire = (date.today() - hire_date).days
                if days_since_hire > 0:
                    change_days_ago = random.randint(0, days_since_hire)
                    change_date = date.today() - timedelta(days=change_days_ago)
                else:
                    change_date = hire_date
                
                # Промежуточные значения (увеличиваем постепенно)
                if j < num_history_records - 1:
                    # Не последняя запись - промежуточное значение
                    intermediate_salary = previous_salary + Decimal(random.randint(10000, 50000))
                    intermediate_quarterly = previous_quarterly + Decimal(random.randint(0, 20000))
                    intermediate_monthly = previous_monthly + Decimal(random.randint(0, 10000))
                    intermediate_yearly = previous_yearly + Decimal(random.randint(0, 50000))
                else:
                    # Последняя запись - текущие значения
                    intermediate_salary = current_salary
                    intermediate_quarterly = current_quarterly_bonus
                    intermediate_monthly = current_monthly_bonus
                    intermediate_yearly = current_yearly_bonus
                
                SalaryHistory.objects.create(
                    employee=employee,
                    change_date=change_date,
                    salary_before=previous_salary,
                    salary_after=intermediate_salary,
                    quarterly_bonus_before=previous_quarterly,
                    quarterly_bonus_after=intermediate_quarterly,
                    monthly_bonus_before=previous_monthly,
                    monthly_bonus_after=intermediate_monthly,
                    yearly_bonus_before=previous_yearly,
                    yearly_bonus_after=intermediate_yearly,
                    comment=f'Изменение зарплаты #{j+1}'
                )
                
                previous_salary = intermediate_salary
                previous_quarterly = intermediate_quarterly
                previous_monthly = intermediate_monthly
                previous_yearly = intermediate_yearly
            
            if (i + 1) % 10 == 0:
                self.stdout.write(f'  Создано сотрудников: {i + 1}/{employees_count}')

        # Назначаем руководителей (случайно)
        self.stdout.write('Назначение руководителей...')
        for dept in departments:
            dept_employees = [e for e in created_employees if e.department == dept]
            if dept_employees:
                manager = random.choice(dept_employees)
                dept.manager = manager
                dept.save()
        
        for div in divisions:
            div_employees = [e for e in created_employees if e.division == div]
            if div_employees:
                manager = random.choice(div_employees)
                div.manager = manager
                div.save()
        
        for group in groups:
            group_employees = [e for e in created_employees if e.group == group]
            if group_employees:
                manager = random.choice(group_employees)
                group.manager = manager
                group.save()
        
        # Назначаем функциональных и линейных руководителей
        self.stdout.write('Назначение функциональных и линейных руководителей...')
        for employee in created_employees:
            # 30% сотрудников имеют функционального руководителя
            if random.random() < 0.3 and created_employees:
                func_manager = random.choice([e for e in created_employees if e != employee])
                employee.functional_manager = func_manager
                employee.save()
            
            # 50% сотрудников имеют линейного руководителя
            if random.random() < 0.5 and created_employees:
                line_manager = random.choice([e for e in created_employees if e != employee])
                employee.line_manager = line_manager
                employee.save()

        self.stdout.write(self.style.SUCCESS(
            f'\nУспешно создано:\n'
            f'  - Департаментов: {Department.objects.count()}\n'
            f'  - Отделов: {Division.objects.count()}\n'
            f'  - Групп: {Group.objects.count()}\n'
            f'  - Сотрудников: {Employee.objects.count()}\n'
            f'  - Записей истории зарплаты: {SalaryHistory.objects.count()}'
        ))

