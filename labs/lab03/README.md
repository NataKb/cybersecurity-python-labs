
# Лабораторна робота №3 — Варіант 7

## Тема

Прикладні бібліотеки Python для побудови вебзастосунків.

## Предметна область

Сервіс обліку часу реагування на інциденти.

Категорії: `account`, `network`, `endpoint`.

Поле `value` зберігає час у хвилинах. Поріг становить 30 хвилин.
Статуси: `new`, `in_progress`, `done`.

## Запуск

Усі команди виконувати з кореня репозиторію.

Встановити залежності:

```bash
pip install fastapi uvicorn pydantic ruff
```

Створити таблиці та початкові дані:

```bash
python -m labs.lab03.seed
```

Запустити API:

```bash
uvicorn labs.lab03.main:app --reload --host 127.0.0.1 --port 8000
```

Документація API:

- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI: http://127.0.0.1:8000/openapi.json

## Приклади запитів

Перевірити API:

```bash
curl http://127.0.0.1:8000/ping
```

Отримати інформацію про студента:

```bash
curl http://127.0.0.1:8000/student
```

Отримати категорії:

```bash
curl http://127.0.0.1:8000/categories
```

Отримати записи:

```bash
curl "http://127.0.0.1:8000/records?limit=5"
```

Відфільтрувати записи:

```bash
curl "http://127.0.0.1:8000/records?category_id=1&status=new"
```

## Перевірка стилю

```bash
ruff check labs/lab03
ruff format --check labs/lab03
ruff check .
ruff format --check .
```

## База даних

Схема зберігається в `schema.sql`, початкові дані — у `data/seed.json`.
Файл `data/lab3.sqlite3` створюється програмою і не додається до Git.
