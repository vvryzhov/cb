from django.contrib import admin
from .models import ExcelFile, ExcelRow, ExcelColumnMapping


@admin.register(ExcelFile)
class ExcelFileAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'uploaded_at', 'total_rows', 'processed_rows', 'status']
    list_filter = ['status', 'uploaded_at']
    search_fields = ['file_name']
    readonly_fields = ['uploaded_at']


@admin.register(ExcelRow)
class ExcelRowAdmin(admin.ModelAdmin):
    list_display = ['row_number', 'excel_file', 'jira_key', 'created_at']
    list_filter = ['excel_file', 'jira_key', 'created_at']
    search_fields = ['jira_key', 'data']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ExcelColumnMapping)
class ExcelColumnMappingAdmin(admin.ModelAdmin):
    list_display = ['excel_file', 'excel_column', 'db_field', 'order']
    list_filter = ['excel_file']

