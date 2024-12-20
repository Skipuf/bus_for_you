# Бас для вас (бэк)

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-blue)
![Celery](https://img.shields.io/badge/Celery-green)
![Redis](https://img.shields.io/badge/Redis-red)

## Описание

Проект представляет собой бэкенд-сервис для аренды автобусов, позволяющий клиентам бронировать автобусы с различными направлениями. Система предоставляет пользователям возможность:

- Просматривать доступное расписание автобусов.
- Выбирать удобное время и резервировать его.
- Отменять бронь.

Транспортные компании могут:
- Управлять своим расписанием и создавать карточки автобусов.
- Указывать детали поездок.

Администратор имеет возможность:
- Управлять пользователями и их ролями.
- Блокировать и разблокировать учетные записи.
- Регулировать конфликты между клиентами и транспортными компаниями.

Проект поддерживает уведомления пользователей по электронной почте, а также использует **Redis** для кеширования и **Celery** для управления асинхронными задачами. Для хранения данных используется **PostgreSQL**. API реализовано в соответствии с подходом REST и содержит интерактивную документацию **Swagger**.

## Основные технологии

- **Python** и **Django** для разработки бэкенда.
- **Django REST Framework** для реализации API.
- **PostgreSQL** — основная база данных.
- **Celery** — управление фоновыми задачами.
- **Redis** — кеширование данных.

## Установка и запуск
1. Клонируйте репозиторий:
```bash
git clone https://github.com/Skipuf/bus_for_you.git
cd bus_for_you
```
2. Выполнить миграции:
```bash
python manage.py makemigrations
python manage.py migrate
```
3. запустить проект:
```bash
python manage.py runserver
```
4. запустить келери:
```bash
celery -A project worker --loglevel=info --pool=solo
celery -A project beat --loglevel=info
```

## Полезные команды
1. Заполнить базу городов
```bash
py manage.py load_cities 'database/management/commands/cities.json'
```
2. Создать группы пользователей
```bash
py manage.py create_roles
```
3. Создать 4 пользователей (для тестов)
```bash
py manage.py create_customers
```
4. Создать автобус (для тестов)
```bash
py manage.py create_bus
```