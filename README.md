# Foodgram
### Описание проекта
Foodgram — это веб-приложение для обмена рецептами и создания сообщества любителей кулинарии. Пользователи могут просматривать, делиться и обсуждать рецепты, а также знакомиться с новыми кулинарными идеями.

[![Main Foodgram Workflow](https://github.com/Artymonae/foodgram/actions/workflows/deploy.yaml/badge.svg)](https://github.com/Artymonae/foodgram/actions/workflows/deploy.yaml)

### Пример сайта

[Пример сайта](https:/foodgramevans.serveftp.com/)  

[Документация АПИ](https://foodgramevans.serveftp.com/api/docs/)

### Структура проекта
backend/ – серверная часть проекта (API, бизнес-логика, работа с базой данных).  

frontend/ – клиентская часть, содержащая веб-интерфейс для пользователей.  

infra/ – файлы конфигурации Docker и docker-compose, необходимые для развёртывания приложения.  

docs/ – документация проекта, включая спецификацию API.  

data/ – (если применимо) файлы с данными или статическими ресурсами.  

postman_collection/ – коллекция Postman для тестирования API.

### Стэк технологий.

[Django](https://www.djangoproject.com/)  

[Python](https://www.python.org/)  

[Django Rest Framework](https://www.django-rest-framework.org/)  

[Djoser](https://github.com/sunscrapers/djoser)

### Установка и запуск

### 1. Клонирование репозитория:
```bash
git clone https://github.com/Artymonae/foodgram.git
cd foodgram
```

### 2. Запуск с использованием Docker Compose:
Перейдите в папку infra:
```bash
cd infra
```

создайте .env следующими переменными
- PGADMIN_DEFAULT_EMAIL
- PGADMIN_DEFAULT_PASSWORD
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_HOST
- POSTGRES_PORT
- DJANGO_ALLOWED_HOSTS
- DJANGO_SECRET_KEY
- DJANGO_CSRF_TRUSTED_ORIGINS

Запустите контейнеры командой:
```bash
docker compose up --build
```

### 3. Заполняем базу данных.

Для этого нам *необходимо:*

```bash
cd foodgram
docker cp data foodgram_backend:/app/data
docker exec -it foodgram_backend bash
python manage.py load_db
```
### 4. Доступ к приложению:

Фронтенд веб-приложения доступен по адресу: http://localhost

Спецификация API доступна по адресу: http://localhost/api/docs/

### Автор проекта:

- Болдырев Артём
- tg: @artymonae
