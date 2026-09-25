# Marketing Content Calendar — Backend API

FastAPI backend for the Marketing Content Calendar application.

## Stack

- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL with SQLAlchemy + Alembic
- **Authentication:** JWT (local HS256)

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Edit .env with your DATABASE_URL and JWT_SECRET
```

## Database Migrations

```bash
alembic upgrade head
python scripts/verify_db.py
```

## Run Server

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/api/v1/health
- Login: POST http://127.0.0.1:8000/api/v1/marketing-team-member/login
- Forgot password: POST http://127.0.0.1:8000/api/v1/marketing-team-member/forgot-password

## Seed a marketing team member

```bash
python scripts/seed_marketing_user.py \
  --email marketing.user@example.com \
  --username marketing_user \
  --password 'SecurePass1!'
```

## Testing

```bash
pytest
```

## Linting & Formatting

```bash
flake8 app tests
black --check app tests
```

## Project Structure

```
app/
  main.py              # ASGI entry point
  api/v1/              # Versioned REST endpoints
  core/                # Config, security, logging
  db/                  # SQLAlchemy session + Alembic migrations
  models/              # ORM models
  schemas/             # Pydantic DTOs
  services/            # Business logic
  repositories/        # Data access
  middleware/          # CORS, logging, auth
  dependencies/        # FastAPI Depends providers
  exceptions/          # Custom HTTP errors
tests/
  unit/
  integration/
scripts/
```
