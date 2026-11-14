# ASCII Studio

Навчальний вебпроєкт на Django: серверна частина, сторінки та API готові, а
JavaScript-функціональність ASCII-редактора залишена для практики.

## Вимоги

- Python 3.10 або новіший
- Django 5.2

## Запуск у Windows

У PowerShell перейдіть до кореневої папки проєкту та виконайте:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Якщо PowerShell забороняє активацію середовища, можна викликати його Python
напряму: `.venv\Scripts\python.exe manage.py runserver`.

## Запуск у macOS

У Terminal перейдіть до кореневої папки проєкту та виконайте:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Відкрийте <http://127.0.0.1:8000/> у браузері. Сторінка адміністратора доступна
за адресою <http://127.0.0.1:8000/admin/>; для входу створіть адміністратора
командою `python manage.py createsuperuser`.

## Перевірки

```bash
python manage.py check
python manage.py test
```

## Маршрути

- `/` — головна сторінка.
- `/studio/editor/` — редактор.
- `/studio/projects/` — власні роботи (потрібен вхід).
- `/accounts/register/`, `/accounts/login/`, `/accounts/logout/` — обліковий запис.
- `/studio/api/projects/` — створення роботи методом POST.
- `/studio/api/projects/<id>/` — отримання, оновлення методом PATCH і видалення
  методом DELETE власної роботи.

Для запитів API, що змінюють дані, використовується звичайний Django CSRF-захист.
Власник роботи встановлюється сервером з активної сесії.

## Практика JavaScript

Файли `static/js/ascii.js`, `editor.js`, `api.js` та `export.js` містять лише
експортовані заготовки та TODO-коментарі. Код генерації ASCII, DOM-обробники,
попередній перегляд, запити до API й експорт PNG навмисно не реалізовані.
