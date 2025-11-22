"""
Views for Excel parser and Jira integration
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Count, Value, CharField
from django.db.models.functions import Concat
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
import threading
import json

from .models import ExcelFile, ExcelRow
from .services import ExcelParserService, ExcelUploadService, JiraService
from .serializers import ExcelFileSerializer, ExcelRowSerializer


class ExcelFileViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с Excel файлами через API"""
    queryset = ExcelFile.objects.all().order_by('-uploaded_at')
    serializer_class = ExcelFileSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['file_name']
    ordering_fields = ['uploaded_at', 'total_rows']
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Обработать Excel файл (запустить парсинг)"""
        excel_file = self.get_object()
        
        # Запускаем парсинг в отдельном потоке
        thread = threading.Thread(target=ExcelParserService.parse_excel_file, args=(excel_file,))
        thread.daemon = True
        thread.start()
        
        return Response({'status': 'processing_started', 'message': 'Файл поставлен в очередь на обработку'})


class ExcelRowViewSet(viewsets.ModelViewSet):
    """ViewSet для работы со строками Excel через API"""
    queryset = ExcelRow.objects.select_related('excel_file').all()
    serializer_class = ExcelRowSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['data', 'jira_key']
    ordering_fields = ['row_number', 'created_at', 'jira_created_at']
    
    def get_queryset(self):
        queryset = ExcelRow.objects.select_related('excel_file').all()
        
        # Фильтр по файлу
        excel_file_id = self.request.query_params.get('excel_file_id', None)
        if excel_file_id:
            queryset = queryset.filter(excel_file_id=excel_file_id)
        
        # Фильтр по наличию Jira ключа
        has_jira = self.request.query_params.get('has_jira', None)
        if has_jira == 'true':
            queryset = queryset.exclude(jira_key__isnull=True).exclude(jira_key='')
        elif has_jira == 'false':
            queryset = queryset.filter(Q(jira_key__isnull=True) | Q(jira_key=''))
        
        # Поиск по данным (JSON)
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(data__icontains=search)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def create_jira_issues(self, request):
        """Создать задачи в Jira для выбранных строк"""
        row_ids = request.data.get('row_ids', [])
        project_key = request.data.get('project_key', None)
        issue_type = request.data.get('issue_type', 'Task')
        summary_template = request.data.get('summary_template', None)
        description_template = request.data.get('description_template', None)
        
        if not row_ids:
            return Response({'error': 'No row_ids provided'}, status=400)
        
        rows = ExcelRow.objects.filter(id__in=row_ids)
        
        if not rows.exists():
            return Response({'error': 'No rows found'}, status=404)
        
        jira_service = JiraService()
        
        try:
            results = jira_service.create_issues_batch(
                rows,
                project_key=project_key,
                issue_type=issue_type,
                summary_template=summary_template,
                description_template=description_template
            )
            
            return Response({
                'status': 'completed',
                'results': results,
                'summary': {
                    'created': len(results['created']),
                    'skipped': len(results['skipped']),
                    'errors': len(results['errors'])
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# Web Views (для Django templates)
def index(request):
    """Главная страница - список Excel файлов"""
    files = ExcelFile.objects.all().order_by('-uploaded_at')[:10]
    
    context = {
        'files': files,
    }
    return render(request, 'excel_parser/index.html', context)


def file_detail(request, file_id):
    """Детальная страница Excel файла со списком строк"""
    excel_file = get_object_or_404(ExcelFile, id=file_id)
    
    # Фильтры и поиск
    search = request.GET.get('search', '')
    has_jira_filter = request.GET.get('has_jira', '')
    
    rows = ExcelRow.objects.filter(excel_file=excel_file)
    
    if search:
        rows = rows.filter(data__icontains=search)
    
    if has_jira_filter == 'yes':
        rows = rows.exclude(jira_key__isnull=True).exclude(jira_key='')
    elif has_jira_filter == 'no':
        rows = rows.filter(Q(jira_key__isnull=True) | Q(jira_key=''))
    
    # Пагинация
    paginator = Paginator(rows, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'excel_file': excel_file,
        'page_obj': page_obj,
        'search': search,
        'has_jira_filter': has_jira_filter,
        'total_rows': rows.count(),
    }
    return render(request, 'excel_parser/file_detail.html', context)


def upload_file(request):
    """Загрузка Excel файла"""
    if request.method == 'POST':
        uploaded_file = request.FILES.get('excel_file')
        
        if not uploaded_file:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        try:
            excel_file = ExcelUploadService.upload_excel_file(uploaded_file)
            
            # Запускаем парсинг в отдельном потоке
            thread = threading.Thread(target=ExcelParserService.parse_excel_file, args=(excel_file,))
            thread.daemon = True
            thread.start()
            
            return JsonResponse({
                'success': True,
                'file_id': excel_file.id,
                'file_name': excel_file.file_name,
                'message': 'Файл загружен и поставлен в очередь на обработку'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return render(request, 'excel_parser/upload.html')


def reports(request):
    """Страница с отчетами и графиками"""
    # Статистика по файлам
    files_stats = ExcelFile.objects.aggregate(
        total_files=Count('id'),
        total_rows=Count('rows'),
        files_with_jira=Count('rows__jira_key', distinct=True)
    )
    
    # Статистика по строкам с Jira
    rows_with_jira = ExcelRow.objects.exclude(jira_key__isnull=True).exclude(jira_key='').count()
    rows_without_jira = ExcelRow.objects.filter(Q(jira_key__isnull=True) | Q(jira_key='')).count()
    
    # Статистика по файлам
    files_status = ExcelFile.objects.values('status').annotate(count=Count('id'))
    
    context = {
        'files_stats': files_stats,
        'rows_with_jira': rows_with_jira,
        'rows_without_jira': rows_without_jira,
        'files_status': list(files_status),
    }
    return render(request, 'excel_parser/reports.html', context)


@require_POST
def create_jira_issues_web(request):
    """Создание задач в Jira (web версия)"""
    try:
        data = json.loads(request.body)
        row_ids = data.get('row_ids', [])
        project_key = data.get('project_key', None)
        issue_type = data.get('issue_type', 'Task')
        
        if not row_ids:
            return JsonResponse({'error': 'No row_ids provided'}, status=400)
        
        rows = ExcelRow.objects.filter(id__in=row_ids)
        
        if not rows.exists():
            return JsonResponse({'error': 'No rows found'}, status=404)
        
        jira_service = JiraService()
        
        results = jira_service.create_issues_batch(
            rows,
            project_key=project_key,
            issue_type=issue_type
        )
        
        return JsonResponse({
            'success': True,
            'results': results,
            'summary': {
                'created': len(results['created']),
                'skipped': len(results['skipped']),
                'errors': len(results['errors'])
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

