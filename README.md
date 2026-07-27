# Сервис автоматизации закупок

Backend-приложение для автоматизации закупок в розничной сети.  
Студент: Константин  
Проект: Дипломная работа "Python-разработчик: расширенный курс"

## Технологии
- Python 3.10+
- Django 4.2
- Django REST Framework
- JWT-аутентификация
- SQLite
- PyYAML + Requests

## Установка и запуск

### 1. Клонировать репозиторий
```bash
git clone https://github.com/kostya26566-cell/too.git
cd too
```

### 2. Создать виртуальное окружение
```bash
python -m venv venv
```

### 3. Активировать виртуальное окружение
```bash
venv\Scripts\activate
```

### 4. Установить зависимости
```bash
pip install -r requirements.txt
```

### 5. Применить миграции
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Создать суперпользователя
```bash
python manage.py createsuperuser
```

Данные:
- Email: `admin@mail.ru`
- Username: `admin`
- Password: `12345678`

### 7. Запустить сервер
```bash
python manage.py runserver
```