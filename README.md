# Developer Portfolio API

Backend-oriented portfolio project for Aleksandr Zaretsky. It is both a test assignment solution and a small production-style service that can continue working as a personal landing page and lead collection API.

## Stack

- Python 3.13 target, compatible with local Python 3.12+
- FastAPI, Pydantic v2
- SQLAlchemy 2 async, Alembic
- PostgreSQL target, SQLite default for local zero-config launch
- Gemini API with `gemini-2.5-flash-lite`
- Mock AI fallback
- Resend email API
- slowapi rate limiting
- pytest, ruff
- Docker, GitHub Actions, Render-ready config

## Local Launch

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
copy .env.example .env
uvicorn app.main:app --reload
```

Open:

- Landing page: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

The default `.env.example` uses SQLite and mock AI, so the project starts without external keys. For production-like mode, set PostgreSQL, Gemini, and Resend variables.

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `APP_ENV` | `local`, `test`, or `production`. |
| `DEBUG` | Enables SQLAlchemy echo and debug behavior. |
| `DATABASE_URL` | Async SQLAlchemy URL. Use Neon PostgreSQL with `postgresql+asyncpg://...`. |
| `AUTO_CREATE_TABLES` | Creates tables on startup. Useful locally; prefer Alembic in production. |
| `CORS_ORIGINS` | Comma-separated allowed origins. |
| `CONTACT_RATE_LIMIT` | slowapi limit, default `5/minute`. |
| `LOG_FILE` | File log path, default `logs/app.log`. |
| `AI_PROVIDER` | `mock` or `gemini`. |
| `GEMINI_API_KEY` | Gemini API key. |
| `GEMINI_MODEL` | Default `gemini-2.5-flash-lite`. |
| `RESEND_API_KEY` | Resend API key. |
| `EMAIL_FROM` | Sender address for Resend. |
| `OWNER_EMAIL` | Site owner notification address. |
| `EMAIL_ENABLED` | Can disable email while keeping API working. |

## Architecture

```text
app/
├── api/             # FastAPI routers and dependencies
├── core/            # config, logging, errors, rate limiting
├── db/              # async SQLAlchemy setup and models
├── providers/       # Gemini and mock AI providers
├── repositories/    # data access
├── schemas/         # Pydantic request/response models
├── services/        # business workflows
├── static/          # landing page
└── main.py          # app factory
```

The request flow is intentionally explicit:

```text
Validation -> Rate limit -> AI classification -> Database storage -> Email notification -> API response
```

## API

### `POST /api/contact`

```bash
curl -X POST http://localhost:8000/api/contact ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Maria Client\",\"email\":\"maria@example.com\",\"phone\":\"+995 555 11 22 33\",\"message\":\"I need a FastAPI backend for a new project with PostgreSQL.\",\"source\":\"website\"}"
```

Response:

```json
{
  "success": true,
  "id": 1,
  "category": "project_request",
  "sentiment": "positive",
  "category_label": "Project Request"
}
```

The landing page displays only a successful send message and the request type. It does not expose the AI reply, sentiment, logs, or internal details.

### `GET /api/health`

```json
{ "status": "ok" }
```

### `GET /api/metrics`

Returns total leads and counts by category/source.

## AI Integration

The AI boundary is a provider protocol:

```python
class AIProvider(Protocol):
    async def analyze(self, contact: ContactRequest) -> AIAnalysis: ...
```

`GeminiProvider` calls Gemini and expects strict JSON with:

- `category`: `job_offer`, `project_request`, `partnership`, `support`, `spam`, `other`
- `sentiment`: `positive`, `neutral`, `negative`
- `reply`: short email reply text

If Gemini is unavailable, invalid, or not configured, `AIService` logs the failure and falls back to `MockProvider`. The contact request still gets stored and the API still returns a successful response when the rest of the pipeline works.

Prompt summary:

```text
Classify a developer portfolio contact form submission.
Return strict JSON with category, sentiment, and a short polite Russian email reply.
Use only the allowed category and sentiment values.
```

## Email

Email is sent through Resend:

- owner notification with request details and AI metadata;
- user copy with the generated AI reply.

If Resend is not configured or fails, the API logs the problem and stores the lead with `email_sent=false`.

## Data, Logs, and Rate Limiting

- Primary table: `leads`
- Local SQLite file: `data/app.db`
- Production target: Neon PostgreSQL
- Logs: `logs/app.log`
- Rate limiting: slowapi, default `5/minute`

Sample log entry:

```text
2026-06-21 10:30:00 | INFO | app.services.contact_service | Lead created: id=1 category=project_request
```

## Database Migrations

Run migrations with:

```bash
alembic upgrade head
```

For quick local startup, `AUTO_CREATE_TABLES=true` creates the schema automatically. For Render/Neon, prefer `AUTO_CREATE_TABLES=false` and run Alembic during deployment or manually before release.

## Tests and Linting

```bash
ruff check .
pytest
```

Current minimum coverage from the assignment:

- `test_contact_success`
- `test_contact_validation`
- `test_contact_rate_limit`
- `test_health`
- `test_metrics`

## Docker

```bash
docker build -t developer-portfolio-api .
docker run --env-file .env -p 8000:8000 developer-portfolio-api
```

With PostgreSQL:

```bash
docker compose up --build
```

Set this in `.env` for compose:

```text
DATABASE_URL=postgresql+asyncpg://portfolio:portfolio@postgres:5432/portfolio
```

## Deployment

Target deployment:

- Backend: Render
- Database: Neon PostgreSQL
- CI/CD: GitHub Actions

Render should receive environment variables from `.env.example`, with real values for:

- `DATABASE_URL`
- `GEMINI_API_KEY`
- `RESEND_API_KEY`
- `OWNER_EMAIL`
- `PUBLIC_BASE_URL`

## Reviewer Scenario

1. Open the landing page.
2. Submit the contact form.
3. Confirm the success message and visible request type.
4. Open `/docs`.
5. Call `/api/health`.
6. Call `/api/metrics`.

## AI Usage During Development

AI was used to help structure the FastAPI project, draft boilerplate for services/providers/tests, and keep the README aligned with the assignment. The implementation was manually reviewed and adjusted for:

- explicit layered architecture;
- deterministic mock fallback;
- readable service boundaries;
- safe handling of missing AI/email credentials;
- focused tests and linting.
