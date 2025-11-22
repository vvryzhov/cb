"""
Serializers for REST API
"""
from rest_framework import serializers
from .models import ExcelFile, ExcelRow, ExcelColumnMapping


class ExcelColumnMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcelColumnMapping
        fields = ['id', 'excel_column', 'db_field', 'order']


class ExcelFileSerializer(serializers.ModelSerializer):
    rows_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ExcelFile
        fields = [
            'id', 'file_name', 'file_path', 'uploaded_at',
            'total_rows', 'processed_rows', 'status', 'error_message', 'rows_count'
        ]
        read_only_fields = ['uploaded_at', 'total_rows', 'processed_rows', 'status', 'error_message']
    
    def get_rows_count(self, obj):
        return obj.rows.count()


class ExcelRowSerializer(serializers.ModelSerializer):
    excel_file_name = serializers.CharField(source='excel_file.file_name', read_only=True)
    data_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = ExcelRow
        fields = [
            'id', 'excel_file', 'excel_file_name', 'row_number',
            'data', 'data_preview', 'jira_key', 'jira_url',
            'jira_created_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'jira_created_at']
    
    def get_data_preview(self, obj):
        return obj.get_data_preview(max_length=200)

