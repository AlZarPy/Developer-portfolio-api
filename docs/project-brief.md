# Developer Portfolio API: project brief

## Context

This project starts as a backend-focused test assignment, but it must remain useful after the assignment as a personal developer portfolio, landing page, lead collection point, and backend skills demo.

The service should look like a small production-ready application without unnecessary complexity.

## Core goals

- Build a backend API for a developer landing page.
- Demonstrate clean FastAPI architecture, validation, error handling, logging, and API documentation.
- Store contact requests and derived metadata.
- Integrate AI for request classification, sentiment analysis, and a generated reply.
- Send email notifications to the site owner and a copy/reply to the user.
- Provide health and metrics endpoints.
- Keep the project deployable and documented.

## Technology decisions

- Backend: Python 3.13, FastAPI, Pydantic v2.
- Database: PostgreSQL, SQLAlchemy 2, Alembic.
- Hosted database target: Neon PostgreSQL.
- AI provider abstraction: `AIProvider` protocol.
- Primary AI provider: Gemini API, `gemini-2.5-flash-lite`.
- AI fallback: `MockProvider`.
- Email provider: Resend.
- Rate limiting: slowapi, configured without Redis.
- Deployment target: Render.
- CI/CD: GitHub Actions for dependency install, linting, and tests.
- Containerization: Dockerfile required, docker-compose.yml desirable.

## Explicitly out of scope

- Redis.
- Celery.
- JWT authentication.
- Admin panel.
- Microservice architecture.

These are intentionally omitted because they are excessive for this project size.

## API scope

### `POST /api/contact`

Main endpoint for the contact form.

Expected processing flow:

1. Validate request.
2. Apply rate limit.
3. Analyze with AI.
4. Store lead in the database.
5. Send email notification.
6. Log the operation.
7. Return a compact response.

Expected response shape:

```json
{
  "success": true,
  "id": 1,
  "category": "project_request",
  "sentiment": "positive"
}
```

### `GET /api/health`

Returns service status:

```json
{
  "status": "ok"
}
```

### `GET /api/metrics`

Returns contact request statistics.

## Contact form fields

- `name`
- `email`
- `phone`
- `message`
- `source`

Allowed `source` values:

- `website`
- `github`
- `cv`
- `telegram`
- `kwork`
- `other`

## AI behavior

The backend should classify contact requests into:

- `job_offer`
- `project_request`
- `partnership`
- `support`
- `spam`
- `other`

Sentiment values:

- `positive`
- `neutral`
- `negative`

The AI-generated reply is stored in the database and can be sent by email, but the landing page should show only a concise success message and a human-readable request type. It must not expose the full AI reply, sentiment, or internal service details.

## Database model

Primary table: `leads`.

Fields:

- `id`
- `name`
- `email`
- `phone`
- `message`
- `source`
- `category`
- `sentiment`
- `ai_reply`
- `email_sent`
- `created_at`

## Logging

Application logs go to `logs/app.log`.

Log:

- incoming requests;
- errors;
- lead creation;
- AI failures;
- email failures.

Logs are internal only. README must document the log path and include a sample log entry.

## Landing page scope

Single-page landing site with:

- hero block for Aleksandr Zaretsky;
- backend/full-stack positioning;
- technology highlights: FastAPI, PostgreSQL, React, AI integrations;
- GitHub, CV download, and contact actions;
- about section;
- technology cards;
- project examples: Sigma Profi, Ne Filkina Gramota, EAEU Events;
- backend processing flow block;
- contact form integrated with `POST /api/contact`.

## Minimum tests

- `test_contact_success`
- `test_contact_validation`
- `test_contact_rate_limit`
- `test_health`
- `test_metrics`

## README requirements

README must document:

- setup and local launch;
- environment variables;
- technology stack;
- architecture and project structure;
- API endpoints and examples;
- validation and error handling;
- AI integration and fallback behavior;
- prompts and how AI was used during development;
- data storage, logging, metrics, and rate limiting;
- Render + Neon deployment;
- verification scenario for reviewers.

## Target architecture

```text
app/
├── api/
│   ├── contact.py
│   ├── health.py
│   └── metrics.py
├── core/
│   ├── config.py
│   ├── logger.py
│   ├── exceptions.py
│   └── rate_limit.py
├── db/
│   ├── database.py
│   └── models.py
├── repositories/
│   └── lead_repository.py
├── schemas/
│   └── lead.py
├── services/
│   ├── contact_service.py
│   ├── ai_service.py
│   ├── email_service.py
│   └── metrics_service.py
├── providers/
│   ├── gemini_provider.py
│   └── mock_provider.py
├── tests/
└── main.py
```

## Definition of done

- Backend API works end to end: request -> validation -> business logic -> AI -> storage -> email -> response.
- Graceful fallback keeps the service working when AI or email provider is unavailable.
- Swagger/OpenAPI is available.
- Logs and errors are handled consistently.
- Tests cover the main flow, validation, rate limiting, health, and metrics.
- Docker and CI are present.
- README is sufficient for local launch and reviewer verification.
