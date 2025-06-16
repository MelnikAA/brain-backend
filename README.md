# Brain Tumor Detection API

API для обнаружения и сегментации опухолей головного мозга на МРТ-изображениях.

## Возможности

- 🔐 Аутентификация пользователей
- 👥 Управление пользователями
- 🧠 Анализ МРТ-изображений
- 📊 Сегментация опухолей

## Технологии

- FastAPI
- PyTorch
- PostgreSQL
- SQLAlchemy

## Установка

1. Клонируйте репозиторий:

```bash
git clone [url-репозитория]
```

2. Создайте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Создайте файл .env и настройте переменные окружения:

```env
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=diplom-brain
```

5. Примените миграции:

```bash
alembic upgrade head
```

## Запуск

```bash
uvicorn app.main:app --reload
```

## API Документация

После запуска приложения, документация API доступна по следующим URL:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Структура проекта

```
app/
├── api/            # API endpoints
├── core/           # Основные настройки
├── crud/           # CRUD операции
├── db/             # Настройки базы данных
├── models/         # SQLAlchemy модели
├── schemas/        # Pydantic схемы
└── services/       # Бизнес-логика
```

## Разработка

### Добавление новых эндпоинтов

1. Создайте новый файл в `app/api/v1/endpoints/`
2. Добавьте роутер в `app/api/v1/api.py`
3. Документируйте эндпоинты с помощью docstrings

### Миграции базы данных

1. Создайте новую миграцию:

```bash
alembic revision --autogenerate -m "описание изменений"
```

2. Примените миграцию:

```bash
alembic upgrade head
```

## Тестирование

```bash
pytest
```

## Лицензия

MIT
