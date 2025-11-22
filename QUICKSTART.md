# Быстрый старт

## Шаг 1: Установка зависимостей

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

## Шаг 2: Настройка базы данных PostgreSQL

1. Установите PostgreSQL 15+
2. Создайте базу данных:

```sql
CREATE DATABASE excel_jira_db;
CREATE USER excel_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE excel_jira_db TO excel_user;
```

## Шаг 3: Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=excel_jira_db
DB_USER=excel_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

JIRA_URL=https://your-jira-instance.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token
```

## Шаг 4: Применение миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

## Шаг 5: Создание суперпользователя (опционально)

```bash
python manage.py createsuperuser
```

## Шаг 6: Запуск сервера

```bash
python manage.py runserver
```

Откройте браузер и перейдите на: http://localhost:8000

## Использование

1. **Загрузка Excel файла**: Перейдите на страницу "Загрузить Excel" и выберите файл
2. **Просмотр данных**: Откройте загруженный файл для просмотра строк данных
3. **Фильтрация**: Используйте поиск и фильтры для нахождения нужных записей
4. **Создание задач в Jira**: Выберите строки и нажмите "Создать задачи в Jira"
5. **Отчеты**: Перейдите на страницу "Отчёты" для просмотра статистики

## API документация

После запуска сервера API доступно по адресу:
- REST API: http://localhost:8000/api/
- Browsable API: http://localhost:8000/api/files/ (если включен DEBUG)

## Решение проблем

### Ошибка подключения к PostgreSQL
- Убедитесь, что PostgreSQL запущен
- Проверьте настройки в `.env` файле
- Проверьте, что пользователь имеет права на базу данных

### Ошибка при загрузке Excel
- Убедитесь, что файл имеет формат `.xlsx` или `.xls`
- Проверьте, что первая строка содержит заголовки колонок

### Ошибка при создании задач в Jira
- Проверьте настройки Jira в `.env` файле
- Убедитесь, что API токен валидный
- Проверьте, что указан правильный ключ проекта Jira

