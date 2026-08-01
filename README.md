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

2. Создать виртуальное окружение

bash
python -m venv venv

3. Активировать виртуальное окружение

Windows:

bash
venv\Scripts\activate
Mac/Linux:

bash
source venv/bin/activate

4. Установить зависимости

bash
pip install -r requirements.txt

5. Применить миграции

bash
python manage.py makemigrations
python manage.py migrate

6. Создать суперпользователя

bash
python manage.py createsuperuser
Данные:

Email: admin2@mail.ru

Username: admin2

Password: 12345678

7. Запустить сервер

bash
python manage.py runserver

Доступ к проекту

Админка: http://127.0.0.1:8000/admin/

API: http://127.0.0.1:8000/api/

Импорт товаров (для поставщиков)
bash
POST /api/partner/update/
Authorization: Bearer <ваш-токен>
{
    "url": "https://example.com/shop1.yaml"
}
Эндпоинты

Метод	URL	Описание 
POST	    /api/register/	                       Регистрация

POST	    /api/login/	                           Вход

GET	        /api/profile/	                       Профиль

POST	    /api/confirm-email/	                   Подтверждение email

POST	    /api/password-reset/	               Восстановление пароля

GET	        /api/products/	                       Список товаров

GET	        /api/products/?shop_id=1	           Фильтр по магазину

GET	        /api/products/?category_id=1	       Фильтр по категории

POST	    /api/cart/	                           Добавить в корзину

DELETE	    /api/cart/item/<id>/	               Удалить из корзины

PATCH	    /api/cart/item/<id>/	               Изменить количество

GET	        /api/orders/	                       Список заказов

POST	    /api/partner/update/	               Импорт товаров

PATCH	    /api/partner/state/	                   Вкл/выкл заказы

GET	        /api/partner/orders/	               Заказы поставщика
text

---