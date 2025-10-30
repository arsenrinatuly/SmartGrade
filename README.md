# 🎓 School Management System

Веб-приложение для управления учебным процессом (электронный журнал, посещаемость, отчёты и роли пользователей).

---

## 🚀 Основные возможности
- Авторизация по email и паролю  
- Роли пользователей: **директор**, **учитель**, **ученик**  
- Управление классами, предметами, уроками  
- Ведение оценок и посещаемости  
- Генерация PDF-отчётов  
- REST API (Django REST Framework)  
- Разграничение прав доступа  

---

## ⚙️ Технологии
- Python 3.12+
- Django 5.x
- Django REST Framework
- PostgreSQL
- Gunicorn
- HTML + Bootstrap
- ReportLab (для PDF)

---

## 🧩 Установка и запуск

### 1️⃣ Клонировать репозиторий
```bash
git clone https://github.com/<your-repo>.git
cd <project-folder>

2️⃣ Создать виртуальное окружение

python3 -m venv venv
source venv/bin/activate

3️⃣ Установить зависимости

pip install -r requirements.txt

4️⃣ Создать файл окружения .env

Пример содержимого:

DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgres://postgres:yourpassword@localhost:5432/school_db
TIME_ZONE=Europe/Moscow

    💡 Если используется django-environ, то достаточно добавить DATABASE_URL.

🗃️ Подготовка базы данных

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

🧰 Статические файлы

python manage.py collectstatic

🧠 Запуск сервера разработки

python manage.py runserver

Открой: http://127.0.0.1:8000
