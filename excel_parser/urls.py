"""
URL configuration for excel_parser app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExcelFileViewSet, ExcelRowViewSet, index, file_detail, upload_file, reports, create_jira_issues_web

# API Router
router = DefaultRouter()
router.register(r'files', ExcelFileViewSet, basename='excelfile')
router.register(r'rows', ExcelRowViewSet, basename='excelrow')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Web endpoints
    path('', index, name='index'),
    path('upload/', upload_file, name='upload_file'),
    path('file/<int:file_id>/', file_detail, name='file_detail'),
    path('reports/', reports, name='reports'),
    path('create-jira-issues/', create_jira_issues_web, name='create_jira_issues_web'),
]

