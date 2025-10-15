URL Shortener Service

📌 Описание проекта

Сервис сокращения ссылок (URL Shortener) позволяет быстро сокращать длинные URL и управлять статистикой переходов.
Реализован с использованием FastAPI, PostgreSQL для хранения данных и Redis для кэширования и оптимизации статистики.

Ключевые возможности:

Генерация коротких ссылок по длинным URL.

Перенаправление (redirect) по короткому URL.

Подсчёт кликов и времени последнего доступа.

Кэширование URL и статистики в Redis для высокой производительности.

Авторизация администраторов для удаления ссылок.

Полное покрытие тестами с использованием pytest и pytest-asyncio.

🏗 Архитектура

FastAPI — основной веб-фреймворк для API.

PostgreSQL — хранение основной информации о ссылках: оригинальный URL, код, дата создания, клики.

Redis — кэширование коротких ссылок и статистики (clicks, last_accessed), ускорение редиректов.

Background Tasks — асинхронное обновление статистики кликов в PostgreSQL.

JWT Authentication — защита эндпоинта удаления ссылок.

Пример работы:

POST /api/shorten
-> Возвращает короткий URL

GET /api/{short_code}
-> Редирект на оригинальный URL, обновление статистики

GET /api/stats/{short_code}
-> Возвращает clicks и last_accessed

⚙ Установка и запуск
1. Клонируем репозиторий
git clone <repo-url>
cd url_shortener_service

2. Создаём .env файл

Пример содержимого .env:

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=url_shortener
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=admin
SECRET_KEY=supersecretkey
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://redis:6379/0
REDIS_TTL=3600

3. Docker Compose

Запуск всех сервисов через Docker:

docker-compose up -d --build


Сервисы:

db — PostgreSQL

pgadmin — интерфейс управления БД

url_shortener — FastAPI приложение

redis — Redis кэш

🚀 Использование API
Создание короткой ссылки
POST /api/shorten
Content-Type: application/json

{
  "original_url": "https://example.com/very/long/url"
}


Ответ:

{
  "short_code": "abc123",
  "original_url": "https://example.com/very/long/url"
}

Редирект по короткой ссылке
GET /api/abc123


Вернёт редирект на оригинальный URL.

Обновляет статистику clicks и last_accessed в Redis и фоново в PostgreSQL.

Получение статистики
GET /api/stats/abc123


Пример ответа:

{
  "clicks": 10,
  "last_accessed": "2025-10-15T12:45:30"
}

Удаление ссылки (только для авторизованных администраторов)
DELETE /api/abc123
Authorization: Bearer <JWT_TOKEN>


Ответ:

{
  "detail": "URL deleted successfully"
}

🧪 Тестирование

Тесты покрывают:

Создание коротких ссылок

Редирект и проверку статуса HTTP

Проверку статистики

Обработку дубликатов и невалидных URL

Удаление ссылок с авторизацией

Запуск тестов:

pytest -v


Для работы тестов используется фикстура pytest-asyncio с корректным event_loop.

💡 Особенности реализации

Redis используется для ускорения доступа к ссылкам и статистике, минимизация обращений к PostgreSQL.

Background tasks обновляют статистику кликов в БД без задержки редиректа пользователя.

JWT защита для DELETE эндпоинта.

Асинхронные операции на базе asyncpg и redis.asyncio.

Полная проверка на валидность URL и предотвращение дубликатов.

🛠 Стек технологий

Python 3.12

FastAPI

PostgreSQL 15

Redis 7+

SQLAlchemy + AsyncSession

Redis.asyncio

Passlib (для хэширования паролей)

JWT (PyJWT / python-jose)

Pytest + pytest-asyncio

📌 Дополнительно

Все настройки берутся из .env.

Redis TTL на кэш можно настроить через переменную REDIS_TTL.

Фикстуры тестов используют временную базу SQLite для быстрого и независимого тестирования.

Все эндпоинты версионируются через /api/.
