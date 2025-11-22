"""
Models for Payroll BI - ФОТ (Фонд оплаты труда)
"""
from django.db import models
from django.db.models import F, Sum, DecimalField, ExpressionWrapper
from django.core.validators import MinValueValidator
from decimal import Decimal


class Department(models.Model):
    """Департамент"""
    name = models.CharField(max_length=255, unique=True, verbose_name="Название")
    manager = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        verbose_name="Руководитель"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Департамент"
        verbose_name_plural = "Департаменты"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def divisions(self):
        """Список отделов департамента"""
        return self.divisions.all()


class Division(models.Model):
    """Отдел"""
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='divisions',
        verbose_name="Департамент"
    )
    name = models.CharField(max_length=255, verbose_name="Название")
    manager = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_divisions',
        verbose_name="Руководитель"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"
        ordering = ['department', 'name']
        unique_together = [['department', 'name']]

    def __str__(self):
        return f"{self.department.name} - {self.name}"

    @property
    def groups(self):
        """Список групп отдела"""
        return self.groups.all()


class Group(models.Model):
    """Группа"""
    division = models.ForeignKey(
        Division,
        on_delete=models.CASCADE,
        related_name='groups',
        verbose_name="Отдел"
    )
    name = models.CharField(max_length=255, verbose_name="Название")
    manager = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_groups',
        verbose_name="Руководитель"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"
        ordering = ['division', 'name']
        unique_together = [['division', 'name']]

    def __str__(self):
        return f"{self.division.department.name} - {self.division.name} - {self.name}"


class EmployeeQuerySet(models.QuerySet):
    """Кастомный QuerySet для Employee с поддержкой current_income в запросах"""
    
    def with_current_income(self):
        """Добавляет вычисляемое поле current_income через annotate"""
        # Используем другое имя для annotate, чтобы не конфликтовать с property
        return self.annotate(
            _annotated_current_income=ExpressionWrapper(
                F('current_salary') + 
                F('current_quarterly_bonus') + 
                F('current_monthly_bonus') + 
                F('current_yearly_bonus'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )


class EmployeeManager(models.Manager):
    """Кастомный Manager для Employee"""
    
    def get_queryset(self):
        return EmployeeQuerySet(self.model, using=self._db)
    
    def with_current_income(self):
        """Возвращает QuerySet с вычисляемым полем current_income"""
        return self.get_queryset().with_current_income()


class Employee(models.Model):
    """Сотрудник"""
    # Основная информация
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    login = models.CharField(max_length=100, unique=True, verbose_name="Логин")
    
    # Организационная структура
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name="Департамент"
    )
    division = models.ForeignKey(
        Division,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name="Отдел"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name="Группа"
    )
    position = models.CharField(max_length=255, blank=True, null=True, verbose_name="Должность")
    
    # Руководители
    functional_manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='functional_subordinates',
        verbose_name="Функциональный руководитель"
    )
    line_manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='line_subordinates',
        verbose_name="Линейный руководитель"
    )
    
    # Даты
    hire_date = models.DateField(verbose_name="Дата принятия на работу")
    
    # Текущие финансовые показатели (гросс)
    current_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Текущий оклад, гросс"
    )
    current_quarterly_bonus = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Текущая квартальная премия, гросс"
    )
    current_monthly_bonus = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Текущая месячная премия, гросс"
    )
    current_yearly_bonus = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Текущая годовая премия, гросс"
    )
    
    # Метод для вычисления текущего дохода
    def _get_current_income(self):
        """Текущий доход, гросс - сумма оклада и всех премий"""
        # Если есть annotate поле (из with_current_income()), используем его
        if '_annotated_current_income' in self.__dict__:
            return self.__dict__['_annotated_current_income']
        
        # Иначе вычисляем вручную
        return (
            self.current_salary +
            self.current_quarterly_bonus +
            self.current_monthly_bonus +
            self.current_yearly_bonus
        )
    
    current_income = property(_get_current_income)
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    
    # Кастомный менеджер
    objects = EmployeeManager()

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ['full_name']
        indexes = [
            models.Index(fields=['login']),
            models.Index(fields=['department', 'division', 'group']),
            models.Index(fields=['hire_date']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.login})"

    def save(self, *args, **kwargs):
        # При сохранении можно автоматически обновлять историю зарплаты
        super().save(*args, **kwargs)


class SalaryHistory(models.Model):
    """История изменений зарплаты сотрудника"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='salary_history',
        verbose_name="Сотрудник"
    )
    change_date = models.DateField(verbose_name="Дата изменения")
    
    # Изменения оклада
    salary_before = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Оклад до изменения"
    )
    salary_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Оклад после изменения"
    )
    salary_diff = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Изменение оклада (diff)"
    )
    
    # Изменения премий
    quarterly_bonus_before = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Квартальная премия до"
    )
    quarterly_bonus_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Квартальная премия после"
    )
    quarterly_bonus_diff = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Изменение квартальной премии (diff)"
    )
    
    monthly_bonus_before = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Месячная премия до"
    )
    monthly_bonus_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Месячная премия после"
    )
    monthly_bonus_diff = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Изменение месячной премии (diff)"
    )
    
    yearly_bonus_before = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Годовая премия до"
    )
    yearly_bonus_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Годовая премия после"
    )
    yearly_bonus_diff = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Изменение годовой премии (diff)"
    )
    
    # Общее изменение дохода
    total_income_before = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Общий доход до"
    )
    total_income_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Общий доход после"
    )
    total_income_diff = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Изменение общего дохода (diff)"
    )
    
    # Комментарий к изменению
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания записи")

    class Meta:
        verbose_name = "История изменения зарплаты"
        verbose_name_plural = "История изменений зарплаты"
        ordering = ['-change_date', '-created_at']
        indexes = [
            models.Index(fields=['employee', 'change_date']),
            models.Index(fields=['change_date']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.change_date} (Δ {self.total_income_diff})"

    def save(self, *args, **kwargs):
        # Автоматически вычисляем diff при сохранении
        self.salary_diff = self.salary_after - self.salary_before
        self.quarterly_bonus_diff = self.quarterly_bonus_after - self.quarterly_bonus_before
        self.monthly_bonus_diff = self.monthly_bonus_after - self.monthly_bonus_before
        self.yearly_bonus_diff = self.yearly_bonus_after - self.yearly_bonus_before
        
        self.total_income_before = (
            self.salary_before +
            self.quarterly_bonus_before +
            self.monthly_bonus_before +
            self.yearly_bonus_before
        )
        self.total_income_after = (
            self.salary_after +
            self.quarterly_bonus_after +
            self.monthly_bonus_after +
            self.yearly_bonus_after
        )
        self.total_income_diff = self.total_income_after - self.total_income_before
        
        super().save(*args, **kwargs)
