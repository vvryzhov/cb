"""
Models for Excel data storage and Jira integration
"""
from django.db import models
from django.core.validators import FileExtensionValidator
import json


class ExcelFile(models.Model):
    """Модель для хранения информации о загруженных Excel файлах"""
    file_name = models.CharField(max_length=255, verbose_name="Имя файла")
    file_path = models.FileField(
        upload_to='excel_files/',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        verbose_name="Путь к файлу"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    total_rows = models.IntegerField(default=0, verbose_name="Всего строк")
    processed_rows = models.IntegerField(default=0, verbose_name="Обработано строк")
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Ожидает обработки'),
            ('processing', 'Обрабатывается'),
            ('completed', 'Завершено'),
            ('failed', 'Ошибка'),
        ],
        default='pending',
        verbose_name="Статус"
    )
    error_message = models.TextField(blank=True, null=True, verbose_name="Сообщение об ошибке")

    class Meta:
        verbose_name = "Excel файл"
        verbose_name_plural = "Excel файлы"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.file_name} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"


class ExcelRow(models.Model):
    """Модель для хранения строк данных из Excel"""
    excel_file = models.ForeignKey(
        ExcelFile,
        on_delete=models.CASCADE,
        related_name='rows',
        verbose_name="Excel файл"
    )
    row_number = models.IntegerField(verbose_name="Номер строки в файле")
    
    # Поля для хранения данных из Excel (JSON)
    # Структура будет динамической в зависимости от колонок Excel
    data = models.JSONField(default=dict, verbose_name="Данные строки")
    
    # Ссылка на созданную задачу в Jira
    jira_key = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ключ задачи Jira")
    jira_url = models.URLField(blank=True, null=True, verbose_name="URL задачи Jira")
    jira_created_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата создания в Jira")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Строка Excel"
        verbose_name_plural = "Строки Excel"
        ordering = ['excel_file', 'row_number']
        indexes = [
            models.Index(fields=['excel_file', 'row_number']),
            models.Index(fields=['jira_key']),
        ]

    def __str__(self):
        return f"Строка {self.row_number} из {self.excel_file.file_name}"

    def get_data_preview(self, max_length=100):
        """Получить предпросмотр данных для отображения"""
        preview = json.dumps(self.data, ensure_ascii=False)[:max_length]
        if len(json.dumps(self.data, ensure_ascii=False)) > max_length:
            preview += "..."
        return preview


class ExcelColumnMapping(models.Model):
    """Модель для хранения маппинга колонок Excel к полям"""
    excel_file = models.ForeignKey(
        ExcelFile,
        on_delete=models.CASCADE,
        related_name='column_mappings',
        verbose_name="Excel файл"
    )
    excel_column = models.CharField(max_length=255, verbose_name="Колонка в Excel")
    db_field = models.CharField(max_length=255, verbose_name="Поле в БД")
    order = models.IntegerField(verbose_name="Порядок")

    class Meta:
        verbose_name = "Маппинг колонок"
        verbose_name_plural = "Маппинги колонок"
        ordering = ['excel_file', 'order']

    def __str__(self):
        return f"{self.excel_column} → {self.db_field}"

