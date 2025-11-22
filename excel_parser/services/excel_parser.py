"""
Сервис для парсинга Excel файлов
"""
import pandas as pd
from django.core.files.uploadedfile import InMemoryUploadedFile
from ..models import ExcelFile, ExcelRow, ExcelColumnMapping
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class ExcelParserService:
    """Сервис для парсинга и сохранения Excel файлов"""
    
    @staticmethod
    def parse_excel_file(excel_file_model: ExcelFile):
        """
        Парсит Excel файл и сохраняет данные в БД
        
        Args:
            excel_file_model: Модель ExcelFile
        """
        try:
            excel_file_model.status = 'processing'
            excel_file_model.save()
            
            # Читаем Excel файл
            file_path = excel_file_model.file_path.path
            
            # Поддерживаем оба формата
            try:
                df = pd.read_excel(file_path, engine='openpyxl')
            except Exception:
                df = pd.read_excel(file_path, engine='xlrd')
            
            # Определяем колонки
            columns = df.columns.tolist()
            
            # Создаем маппинг колонок
            for idx, col in enumerate(columns):
                ExcelColumnMapping.objects.get_or_create(
                    excel_file=excel_file_model,
                    excel_column=str(col),
                    defaults={
                        'db_field': str(col).lower().replace(' ', '_'),
                        'order': idx
                    }
                )
            
            # Сохраняем каждую строку
            total_rows = len(df)
            excel_file_model.total_rows = total_rows
            excel_file_model.save()
            
            processed = 0
            for index, row in df.iterrows():
                # Преобразуем строку в словарь
                row_data = {}
                for col in columns:
                    value = row[col]
                    # Обрабатываем NaN значения
                    if pd.isna(value):
                        value = None
                    else:
                        # Преобразуем в простые типы Python
                        if isinstance(value, pd.Timestamp):
                            value = value.isoformat()
                        elif hasattr(value, 'item'):  # numpy типы
                            value = value.item()
                    
                    row_data[str(col)] = value
                
                # Создаем запись в БД
                ExcelRow.objects.create(
                    excel_file=excel_file_model,
                    row_number=index + 2,  # +2 потому что Excel начинается с 1, а заголовок - строка 1
                    data=row_data
                )
                
                processed += 1
                if processed % 100 == 0:
                    excel_file_model.processed_rows = processed
                    excel_file_model.save()
            
            excel_file_model.processed_rows = processed
            excel_file_model.status = 'completed'
            excel_file_model.save()
            
            logger.info(f"Successfully parsed {processed} rows from {excel_file_model.file_name}")
            
        except Exception as e:
            logger.error(f"Error parsing Excel file {excel_file_model.file_name}: {str(e)}", exc_info=True)
            excel_file_model.status = 'failed'
            excel_file_model.error_message = str(e)
            excel_file_model.save()
            raise


class ExcelUploadService:
    """Сервис для загрузки Excel файлов"""
    
    @staticmethod
    def upload_excel_file(uploaded_file, file_name=None):
        """
        Создает модель ExcelFile из загруженного файла
        
        Args:
            uploaded_file: Загруженный файл
            file_name: Имя файла (если не указано, берется из uploaded_file)
        
        Returns:
            ExcelFile: Созданная модель
        """
        if file_name is None:
            file_name = uploaded_file.name
        
        excel_file = ExcelFile.objects.create(
            file_name=file_name,
            file_path=uploaded_file,
            status='pending'
        )
        
        return excel_file

