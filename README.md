# Order Fulfillment — FastAPI learning template

A FastAPI template repo for learning patterns and best practices. Orders move through
a state machine (draft → placed → paid → shipped → delivered, with cancel/refund
branches). Not a product — see [CLAUDE.md](CLAUDE.md) for the project's intent.

**Stack:** Python 3.14 · FastAPI · SQLAlchemy 2.0 (async) · Alembic · Postgres · uv · ruff · ty

## Quick start

```bash
# Everything in Docker (API + Postgres), docs at http://localhost:8000/docs
docker compose up -d --build

# Tear down (add -v to also drop the Postgres volume)
docker compose down
```

The API container mounts `./src` and runs uvicorn with `--reload`, so code changes
apply without rebuilding. Rebuild only when dependencies change.

## Logs & container access

```bash
# Follow API logs (drop -f for a one-off dump, add --tail 100 for the last 100 lines)
docker compose logs -f api

# Postgres logs
docker compose logs -f db

# Shell inside the API container
docker compose exec api bash

# psql session in the Postgres container (user/db are both "app")
docker compose exec db psql -U app

# One-off query without entering psql
docker compose exec db psql -U app -c "select 1"
```

## Local development (without Docker)

```bash
# Install/sync all dependencies (creates .venv)
uv sync

# Start only Postgres in Docker
docker compose up -d db

# Run the API with hot reload
uv run uvicorn app.main:app --reload
```

## Checks

```bash
# Tests
uv run pytest

# Lint (add --fix to autofix)
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run ty check
```

## Dependency management

```bash
# Add a runtime / dev dependency
uv add <package>
uv add --dev <package>

# Upgrade everything within pyproject constraints
uv lock --upgrade && uv sync
```

## Layout

```
src/app/
├── api/            # HTTP layer: health (unversioned) + v1/ routers & schemas
├── domain/         # Business rules: entities, state machine, policies (no framework imports)
├── services/       # Use cases: orchestrate domain + repositories
├── repositories/   # Data access: domain objects in/out, SQL inside
└── db/             # Engine, sessions, SQLAlchemy models, (later) Alembic
tests/
```
