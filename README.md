# Excel → БД → BI → Jira Service

Веб-сервис для загрузки Excel файлов, сохранения данных в PostgreSQL, просмотра через веб-GUI с возможностью создания задач в Jira.

## Технологический стек

### Backend
- **Python 3.12+**
- **Django 5.x**
- **Django REST Framework** для API
- **PostgreSQL 15+** для хранения данных
- **pandas + openpyxl** для парсинга Excel
- **requests** для интеграции с Jira API

### Frontend
- **Django Templates** + **HTMX** + **Alpine.js**
- **Tailwind CSS** для стилизации
- **Chart.js** для графиков и отчетов

### Опционально
- **Celery + Redis** для фоновых задач

## Установка и настройка

### 1. Клонирование и настройка окружения

```bash
cd excel_jira_service
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка базы данных

Создайте базу данных PostgreSQL:

```sql
CREATE DATABASE excel_jira_db;
CREATE USER excel_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE excel_jira_db TO excel_user;
```

### 4. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=excel_jira_db
DB_USER=excel_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Jira Configuration
JIRA_URL=https://your-jira-instance.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token

# Celery (optional)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 5. Применение миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Создание суперпользователя (опционально)

```bash
python manage.py createsuperuser
```

### 7. Запуск сервера разработки

```bash
python manage.py runserver
```

Сервис будет доступен по адресу: http://localhost:8000

## Использование

### 1. Загрузка Excel файла

1. Перейдите на страницу "Загрузить Excel"
2. Выберите файл формата `.xlsx` или `.xls`
3. Нажмите "Загрузить и обработать"
4. Файл будет обработан в фоновом режиме

### 2. Просмотр данных

1. На главной странице отображаются все загруженные файлы
2. Кликните на файл для просмотра его строк данных
3. Используйте поиск и фильтры для нахождения нужных записей

### 3. Создание задач в Jira

1. На странице с данными файла выберите нужные строки (чекбоксы)
2. Нажмите кнопку "Создать задачи в Jira"
3. Укажите ключ проекта Jira и тип задачи
4. Нажмите "Создать"
5. Задачи будут созданы, а ключи задач сохранятся в базе данных

### 4. Просмотр отчетов

Перейдите на страницу "Отчёты" для просмотра статистики:
- Общее количество файлов и строк
- Количество строк с задачами Jira
- Графики распределения данных

## API Endpoints

### REST API

#### Excel Files
- `GET /api/files/` - Список файлов
- `POST /api/files/` - Загрузить файл
- `GET /api/files/{id}/` - Детали файла
- `POST /api/files/{id}/process/` - Обработать файл

#### Excel Rows
- `GET /api/rows/` - Список строк (с фильтрами)
  - `?excel_file_id={id}` - Фильтр по файлу
  - `?has_jira=true|false` - Фильтр по наличию Jira задачи
  - `?search={text}` - Поиск по данным
- `POST /api/rows/create_jira_issues/` - Создать задачи в Jira

### Web Endpoints
- `GET /` - Главная страница
- `GET /upload/` - Страница загрузки файла
- `POST /upload/` - Загрузка файла
- `GET /file/{id}/` - Детали файла со списком строк
- `GET /reports/` - Страница с отчетами
- `POST /create-jira-issues/` - Создание задач в Jira

## Структура проекта

```
excel_jira_service/
├── config/              # Настройки Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── excel_parser/        # Основное приложение
│   ├── models.py        # Модели данных
│   ├── views.py         # Views и ViewSets
│   ├── serializers.py   # DRF сериализаторы
│   ├── services/        # Бизнес-логика
│   │   ├── excel_parser.py
│   │   └── jira_service.py
│   └── urls.py
├── templates/           # HTML шаблоны
│   ├── base.html
│   └── excel_parser/
├── static/              # Статические файлы
├── media/               # Загруженные файлы
├── manage.py
└── requirements.txt
```

## Модели данных

### ExcelFile
Хранит информацию о загруженных Excel файлах:
- `file_name` - имя файла
- `file_path` - путь к файлу
- `uploaded_at` - дата загрузки
- `total_rows` - всего строк
- `processed_rows` - обработано строк
- `status` - статус обработки

### ExcelRow
Хранит данные из строк Excel:
- `excel_file` - ссылка на файл
- `row_number` - номер строки
- `data` - данные строки (JSON)
- `jira_key` - ключ задачи в Jira
- `jira_url` - URL задачи в Jira

## Настройка Jira

Для работы с Jira необходимо:

1. Получить API Token:
   - Зайдите в Jira → Account Settings → Security → API tokens
   - Создайте новый токен

2. Настроить переменные окружения:
   - `JIRA_URL` - URL вашего Jira инстанса
   - `JIRA_EMAIL` - email вашего аккаунта
   - `JIRA_API_TOKEN` - API токен

## Интеграция с Celery (опционально)

Для асинхронной обработки файлов:

1. Установите Redis:
```bash
# Linux
sudo apt-get install redis-server

# Mac
brew install redis

# Windows
# Скачайте и установите Redis for Windows
```

2. Запустите Celery worker:
```bash
celery -A config worker -l info
```

3. Запустите Celery beat (если нужны периодические задачи):
```bash
celery -A config beat -l info
```

## Разработка

### Запуск тестов
```bash
python manage.py test
```

### Создание миграций
```bash
python manage.py makemigrations
```

### Применение миграций
```bash
python manage.py migrate
```

### Сбор статических файлов
```bash
python manage.py collectstatic
```

## Лицензия

MIT

## Автор

Excel → БД → BI → Jira Service

