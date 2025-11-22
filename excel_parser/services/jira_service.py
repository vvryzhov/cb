"""
Сервис для интеграции с Jira
"""
import requests
from django.conf import settings
from ..models import ExcelRow
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class JiraService:
    """Сервис для работы с Jira API"""
    
    def __init__(self):
        self.base_url = settings.JIRA_URL.rstrip('/')
        self.email = settings.JIRA_EMAIL
        self.api_token = settings.JIRA_API_TOKEN
        
    def _get_auth(self):
        """Получить заголовки для аутентификации"""
        if not self.email or not self.api_token:
            raise ValueError("JIRA_EMAIL and JIRA_API_TOKEN must be configured in settings")
        
        return (self.email, self.api_token)
    
    def create_issue(self, excel_row: ExcelRow, project_key: str = None, issue_type: str = "Task", 
                    summary_template: str = None, description_template: str = None) -> dict:
        """
        Создать задачу в Jira на основе данных Excel строки
        
        Args:
            excel_row: Модель ExcelRow
            project_key: Ключ проекта в Jira (если не указан, нужно будет получить из настроек)
            issue_type: Тип задачи (Task, Bug, Story и т.д.)
            summary_template: Шаблон для заголовка задачи (может содержать {field_name})
            description_template: Шаблон для описания задачи
        
        Returns:
            dict: Информация о созданной задаче
        """
        if excel_row.jira_key:
            logger.warning(f"Row {excel_row.id} already has Jira issue: {excel_row.jira_key}")
            return {
                'key': excel_row.jira_key,
                'url': excel_row.jira_url,
                'already_exists': True
            }
        
        # Формируем данные задачи
        data = excel_row.data
        
        # Генерируем summary
        if summary_template:
            summary = summary_template.format(**data)
        else:
            # По умолчанию берем первые несколько полей
            summary_parts = []
            for key, value in list(data.items())[:3]:
                if value is not None:
                    summary_parts.append(f"{key}: {value}")
            summary = " | ".join(summary_parts) or f"Задача из Excel (строка {excel_row.row_number})"
        
        # Генерируем description
        if description_template:
            description = description_template.format(**data)
        else:
            description_lines = ["Данные из Excel файла:"]
            for key, value in data.items():
                if value is not None:
                    description_lines.append(f"*{key}*: {value}")
            description = "\n".join(description_lines)
        
        # Формируем payload для Jira API
        issue_data = {
            "fields": {
                "project": {
                    "key": project_key or "PROJ"  # Нужно настраивать по умолчанию
                },
                "summary": summary[:255],  # Ограничение Jira
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": description
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {
                    "name": issue_type
                }
            }
        }
        
        # Отправляем запрос в Jira
        url = f"{self.base_url}/rest/api/3/issue"
        auth = self._get_auth()
        
        try:
            response = requests.post(
                url,
                json=issue_data,
                auth=auth,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            jira_key = result['key']
            jira_url = f"{self.base_url}/browse/{jira_key}"
            
            # Сохраняем информацию о задаче в БД
            excel_row.jira_key = jira_key
            excel_row.jira_url = jira_url
            excel_row.jira_created_at = timezone.now()
            excel_row.save()
            
            logger.info(f"Created Jira issue {jira_key} for Excel row {excel_row.id}")
            
            return {
                'key': jira_key,
                'url': jira_url,
                'id': result.get('id'),
                'already_exists': False
            }
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Jira API error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Error creating Jira issue: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
    
    def create_issues_batch(self, excel_rows, project_key: str = None, issue_type: str = "Task",
                           summary_template: str = None, description_template: str = None):
        """
        Создать несколько задач в Jira
        
        Args:
            excel_rows: QuerySet или список ExcelRow объектов
            project_key: Ключ проекта
            issue_type: Тип задачи
            summary_template: Шаблон заголовка
            description_template: Шаблон описания
        
        Returns:
            dict: Статистика создания задач
        """
        results = {
            'created': [],
            'skipped': [],
            'errors': []
        }
        
        for row in excel_rows:
            try:
                if row.jira_key:
                    results['skipped'].append({
                        'row_id': row.id,
                        'reason': 'Already has Jira key',
                        'jira_key': row.jira_key
                    })
                    continue
                
                result = self.create_issue(
                    row,
                    project_key=project_key,
                    issue_type=issue_type,
                    summary_template=summary_template,
                    description_template=description_template
                )
                
                if not result.get('already_exists'):
                    results['created'].append({
                        'row_id': row.id,
                        'jira_key': result['key'],
                        'jira_url': result['url']
                    })
                else:
                    results['skipped'].append({
                        'row_id': row.id,
                        'reason': 'Already exists',
                        'jira_key': result['key']
                    })
                    
            except Exception as e:
                results['errors'].append({
                    'row_id': row.id,
                    'error': str(e)
                })
                logger.error(f"Error creating Jira issue for row {row.id}: {str(e)}")
        
        return results

