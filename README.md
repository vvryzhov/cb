# Payroll BI - BI-инструмент для работы с бюджетом ФОТ

Веб-приложение для управления и анализа фонда оплаты труда (ФОТ) компании с интеграцией Saiku для продвинутой аналитики.

## Технологический стек

- **Backend**: Python 3.12+, Django 5.x, Django REST Framework
- **Database**: PostgreSQL 15+
- **Frontend**: Django Templates + HTMX + Alpine.js + Tailwind CSS
- **BI**: Saiku (через Docker)
- **Deployment**: Docker + Docker Compose
- **Data Processing**: pandas + openpyxl

## Основные возможности

### 1. Управление организационной структурой
- Департаменты
- Отделы
- Группы
- Иерархия руководителей

### 2. Управление сотрудниками
- Полная информация о сотрудниках (ФИО, логин, должность, организационная структура)
- Текущие финансовые показатели (оклад, премии)
- История изменений зарплаты с автоматическим расчетом дельт
- Фильтрация и поиск сотрудников

### 3. Аналитические отчеты
- Дельта повышения департамента между годами
- Сводные отчеты по ФОТ
- История изменений зарплаты
- Произвольные отчеты с различными разрезами

### 4. Загрузка данных
- Загрузка справочников (департаменты, отделы, группы) из Excel
- Загрузка сотрудников из Excel с автоматическим созданием истории изменений

## Быстрый старт с Docker

### 1. Клонирование репозитория

```bash
git clone https://github.com/vvryzhov/cb.git
cd cb
```

### 2. Настройка переменных окружения

Создайте файл `.env`:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=payroll_bi_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Django
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media
```

### 3. Запуск через Docker Compose

```bash
docker-compose up -d
```

Это запустит:
- PostgreSQL базу данных
- Django веб-приложение (http://localhost:8000)
- Saiku BI инструмент (http://localhost:8080)

### 4. Применение миграций

```bash
docker-compose exec web python manage.py migrate
```

### 5. Создание суперпользователя

```bash
docker-compose exec web python manage.py createsuperuser
```

## Установка без Docker

### 1. Установка зависимостей

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2. Настройка PostgreSQL

Создайте базу данных:

```sql
CREATE DATABASE payroll_bi_db;
CREATE USER payroll_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE payroll_bi_db TO payroll_user;
```

### 3. Настройка переменных окружения

Создайте файл `.env`:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=payroll_bi_db
DB_USER=payroll_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 4. Применение миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Запуск сервера

```bash
python manage.py runserver
```

## Структура данных

### Модели

1. **Department (Департамент)**
   - Название
   - Руководитель (ссылка на Employee)

2. **Division (Отдел)**
   - Название
   - Департамент (FK)
   - Руководитель (FK на Employee)

3. **Group (Группа)**
   - Название
   - Отдел (FK)
   - Руководитель (FK на Employee)

4. **Employee (Сотрудник)**
   - ФИО, логин
   - Департамент, отдел, группа
   - Должность
   - Функциональный и линейный руководители
   - Дата принятия на работу
   - Текущие финансовые показатели (оклад, премии)
   - Текущий доход (вычисляемое поле)

5. **SalaryHistory (История изменений зарплаты)**
   - Сотрудник (FK)
   - Дата изменения
   - Значения до/после для оклада и всех премий
   - Автоматически вычисляемые дельты (diff)

## API Endpoints

### REST API

#### Справочники
- `GET /api/departments/` - Список департаментов
- `POST /api/departments/` - Создать департамент
- `POST /api/departments/upload/` - Загрузить департаменты из файла
- `GET /api/divisions/` - Список отделов
- `POST /api/divisions/upload/` - Загрузить отделы из файла
- `GET /api/groups/` - Список групп
- `POST /api/groups/upload/` - Загрузить группы из файла

#### Сотрудники
- `GET /api/employees/` - Список сотрудников (с фильтрами)
- `POST /api/employees/` - Создать сотрудника
- `GET /api/employees/{id}/` - Детали сотрудника
- `POST /api/employees/upload/` - Загрузить сотрудников из файла
- `GET /api/employees/{id}/salary_history/` - История зарплаты сотрудника

#### Аналитика
- `GET /api/analytics/department_delta/?department_id=X&year_from=2023&year_to=2024` - Дельта департамента
- `POST /api/analytics/custom_report/` - Произвольный отчет
- `GET /api/analytics/salary_history_report/` - Отчет по истории зарплаты
- `GET /api/analytics/fot_summary/` - Сводный отчет по ФОТ

### Web Endpoints
- `GET /` - Главная страница
- `GET /employees/` - Список сотрудников
- `GET /employees/{id}/` - Детали сотрудника
- `GET /analytics/` - Страница аналитики
- `GET /custom-report/` - Конструктор отчетов

## Загрузка данных

### Формат Excel файлов

#### Департаменты
Колонки: `Название` или `name`

#### Отделы
Колонки: `Департамент` или `department`, `Название` или `name`

#### Группы
Колонки: `Отдел` или `division`, `Название` или `name`

#### Сотрудники
Колонки:
- `Логин` или `login` (обязательно)
- `ФИО` или `full_name`
- `Департамент` или `department`
- `Отдел` или `division`
- `Группа` или `group`
- `Должность` или `position`
- `Дата принятия` или `hire_date`
- `Оклад` или `salary` или `current_salary`
- `Квартальная премия` или `quarterly_bonus`
- `Месячная премия` или `monthly_bonus`
- `Годовая премия` или `yearly_bonus`
- `Функциональный руководитель` или `functional_manager` (логин)
- `Линейный руководитель` или `line_manager` (логин)

## Использование Saiku

Saiku доступен по адресу http://localhost:8080 после запуска Docker Compose.

Для подключения к базе данных используйте настройки из `.env` файла.

## Разработка

### Создание миграций

```bash
python manage.py makemigrations
```

### Применение миграций

```bash
python manage.py migrate
```

### Создание суперпользователя

```bash
python manage.py createsuperuser
```

### Запуск тестов

```bash
python manage.py test
```

## Структура проекта

```
excel_jira_service/
├── config/              # Настройки Django
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── excel_parser/        # Основное приложение
│   ├── models.py        # Модели данных
│   ├── views.py         # Views и ViewSets
│   ├── serializers.py   # DRF сериализаторы
│   ├── services/        # Бизнес-логика
│   │   ├── data_loader.py
│   │   └── analytics.py
│   └── ...
├── templates/           # HTML шаблоны
├── static/              # Статические файлы
├── media/               # Загруженные файлы
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Лицензия

MIT

## Автор

Payroll BI Service
