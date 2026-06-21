# Developer Portfolio API

Backend-проект портфолио для Александра Зарецкого. Проект сделан как тестовое задание, но рассчитан на дальнейшее использование: лендинг разработчика, API для формы обратной связи, сбор обращений, AI-классификация и email-уведомления.

## Стек

- Python 3.13 как целевая версия, локально совместимо с Python 3.12+
- FastAPI, Pydantic v2
- SQLAlchemy 2 async, Alembic
- PostgreSQL для production, SQLite для быстрого локального запуска
- Neon PostgreSQL
- Gemini API, модель `gemini-2.5-flash-lite`
- Mock fallback для AI
- Resend Email API
- slowapi rate limiting
- pytest, ruff
- Docker, GitHub Actions, Render-ready конфигурация

## Локальный запуск

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
copy .env.example .env
uvicorn app.main:app --reload
```

Открыть:

- лендинг: http://localhost:8000
- Swagger: http://localhost:8000/docs
- health check: http://localhost:8000/api/health

По умолчанию `.env.example` использует SQLite и mock AI, поэтому проект запускается без внешних ключей. Для режима, близкого к production, нужно указать PostgreSQL, Gemini и Resend переменные.

## Переменные окружения

| Переменная | Назначение |
| --- | --- |
| `APP_ENV` | Окружение: `local`, `test`, `production`. |
| `DEBUG` | Включает отладочный режим и SQLAlchemy echo. |
| `DATABASE_URL` | Async SQLAlchemy URL. Для Neon: `postgresql+asyncpg://...`. |
| `AUTO_CREATE_TABLES` | Создает таблицы при старте. Удобно локально, в production предпочтительнее Alembic. |
| `CORS_ORIGINS` | Разрешенные origin через запятую. |
| `CONTACT_RATE_LIMIT` | Лимит slowapi, по умолчанию `5/minute`. |
| `LOG_FILE` | Путь к логам, по умолчанию `logs/app.log`. |
| `AI_PROVIDER` | `mock` или `gemini`. |
| `GEMINI_API_KEY` | Ключ Gemini API. |
| `GEMINI_MODEL` | По умолчанию `gemini-2.5-flash-lite`. |
| `RESEND_API_KEY` | Ключ Resend API. |
| `EMAIL_FROM` | Отправитель писем в Resend. |
| `OWNER_EMAIL` | Email владельца сайта для уведомлений. |
| `EMAIL_ENABLED` | Позволяет отключить email, не ломая API. |

## Архитектура

```text
app/
├── api/             # FastAPI routers и dependencies
├── core/            # config, logging, errors, rate limiting
├── db/              # async SQLAlchemy setup и модели
├── providers/       # Gemini и mock AI providers
├── repositories/    # слой доступа к данным
├── schemas/         # Pydantic request/response модели
├── services/        # бизнес-логика
├── static/          # лендинг
└── main.py          # app factory
```

Основной поток обработки обращения:

```text
Валидация -> Rate limit -> AI-классификация -> Запись в БД -> Email-уведомление -> API-ответ
```

## API

### `POST /api/contact`

```bash
curl -X POST http://localhost:8000/api/contact ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Maria Client\",\"email\":\"maria@example.com\",\"phone\":\"+995 555 11 22 33\",\"message\":\"I need a FastAPI backend for a new project with PostgreSQL.\",\"source\":\"website\"}"
```

Ответ:

```json
{
  "success": true,
  "id": 1,
  "category": "project_request",
  "sentiment": "positive",
  "category_label": "Project Request"
}
```

На лендинге пользователь видит только сообщение об успешной отправке и тип обращения. Полный AI-ответ, тональность, логи и служебные детали не показываются.

Валидация обращения:

- `name` обязателен;
- `message` обязателен;
- нужно указать минимум один способ связи: `email` или `phone`;
- если указан `email`, он должен быть валидным email-адресом.
- если указан `phone`, он валидируется и сохраняется в E.164 формате;
- поддерживаются международные номера (`+995...`, `995...`, `+7...`, `7...`) и российский формат через `8...`.

### `GET /api/health`

```json
{ "status": "ok" }
```

### `GET /api/metrics`

Возвращает общее количество обращений и группировку по категории/источнику.

## AI-интеграция

AI отделен через provider protocol:

```python
class AIProvider(Protocol):
    async def analyze(self, contact: ContactRequest) -> AIAnalysis: ...
```

`GeminiProvider` вызывает Gemini и ожидает строгий JSON:

- `category`: `job_offer`, `project_request`, `partnership`, `support`, `spam`, `other`
- `sentiment`: `positive`, `neutral`, `negative`
- `reply`: короткий текст ответа для email

Если Gemini недоступен, вернул некорректный ответ или не настроен, `AIService` логирует ошибку и использует `MockProvider`. Обращение все равно сохраняется, а API продолжает работать.

Краткая суть prompt:

```text
Классифицировать обращение с сайта-портфолио разработчика.
Вернуть строгий JSON с category, sentiment и коротким вежливым ответом на русском.
Использовать только разрешенные значения category и sentiment.
```

## Email

Письма отправляются через Resend:

- уведомление владельцу сайта с деталями обращения и AI-метаданными;
- копия пользователю с AI-сгенерированным ответом.

Текущий локальный вариант использует тестовый sender Resend:

```text
Developer Portfolio <onboarding@resend.dev>
```

Для production желательно подключить собственный домен в Resend, прописать DNS-записи и заменить `EMAIL_FROM`, например:

```text
Aleksandr Zaretsky <hello@example.com>
```

Обращение сначала сохраняется в БД, затем сервис пытается отправить email-уведомления. Поле `email_sent` показывает, что email workflow завершился успешно. Если Resend не настроен или отправка завершилась ошибкой, API логирует проблему и оставляет `email_sent=false`.

## Данные, логи и rate limiting

- основная таблица: `leads`
- локальная SQLite БД: `data/app.db`
- production БД: Neon PostgreSQL
- логи: `logs/app.log`
- rate limiting: slowapi, по умолчанию `5/minute`

Текущий rate limit хранится в памяти процесса. Этого достаточно для single-instance демо и Render free tier, но для нескольких инстансов нужен общий storage backend, например Redis. Redis намеренно не добавлен, чтобы не усложнять тестовое задание сверх требований.

Пример записи в логах:

```text
2026-06-21 10:30:00 | INFO | app.services.contact_service | Lead created: id=1 category=project_request
```

Логи не предназначены для проверяющего и не должны публиковаться.

## Миграции БД

```bash
alembic upgrade head
```

Для быстрого локального старта можно использовать `AUTO_CREATE_TABLES=true`. Для Render/Neon предпочтительнее `AUTO_CREATE_TABLES=false` и явный запуск Alembic.

В production миграции должны выполняться до старта приложения: вручную через Render Shell, отдельным one-off job или отдельным шагом деплоя. `render.yaml` не хранит секреты и не запускает миграции автоматически, чтобы не смешивать управление схемой БД со стартом web-процесса.

## Тесты и линтинг

```bash
ruff check .
pytest
```

Минимальный набор тестов из задания:

- `test_contact_success`
- `test_contact_validation`
- `test_contact_rate_limit`
- `test_health`
- `test_metrics`

## Docker

Сборка production-образа:

```bash
docker build -t developer-portfolio-api .
docker run --env-file .env -p 8000:8000 developer-portfolio-api
```

Локальная проверка полного стека с PostgreSQL:

```bash
docker compose up --build
```

`docker-compose.yml` использует `.env.example`, поднимает отдельный PostgreSQL в Docker-сети, запускает `alembic upgrade head` перед стартом API и отключает реальную email-отправку. Поэтому compose можно запускать без production-секретов.

Проверка:

```bash
curl http://localhost:8000/api/health
```

## Деплой

Целевой вариант:

- backend: Render
- database: Neon PostgreSQL
- CI/CD: GitHub Actions

`render.yaml` описывает Docker Web Service и безопасные production defaults. Секреты задаются вручную в Render Dashboard в разделе Environment и не коммитятся в репозиторий:

- `DATABASE_URL`
- `GEMINI_API_KEY`
- `RESEND_API_KEY`
- `OWNER_EMAIL`
- `PUBLIC_BASE_URL`
- `CORS_ORIGINS`

`PUBLIC_BASE_URL` и `CORS_ORIGINS` должны указывать на Render URL сервиса, например `https://developer-portfolio-api.onrender.com`. После подключения собственного домена их нужно заменить на домен.

Первый production-запуск:

1. Создать Web Service в Render из `render.yaml`.
2. Заполнить переменные окружения в Dashboard.
3. Выполнить `alembic upgrade head` против той же `DATABASE_URL`.
4. Запустить deploy и проверить `/api/health`, лендинг и отправку формы.

Миграции не запускаются автоматически при старте Render-сервиса: `RUN_MIGRATIONS_ON_STARTUP=false`. Это осознанный выбор, чтобы управление схемой БД оставалось отдельным production-шагом.

## Сценарий проверки

1. Открыть лендинг.
2. Отправить форму обратной связи.
3. Увидеть сообщение об успешной отправке и тип обращения.
4. Открыть `/docs`.
5. Проверить `/api/health`.
6. Проверить `/api/metrics`.

## Использование AI при разработке

AI использовался для подготовки структуры FastAPI-проекта, черновиков сервисов, providers, тестов и документации. Реализация была вручную проверена и доработана:

- явная слоистая архитектура;
- детерминированный mock fallback;
- читаемые границы сервисов;
- безопасная обработка отсутствующих AI/email credentials;
- защита от утечки ключей в логи;
- сфокусированные тесты и линтинг.
