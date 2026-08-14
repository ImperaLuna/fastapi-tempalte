# Order Fulfillment — a learning template

Not a product: a FastAPI template repo for learning patterns and best practices.
Patterns may be deliberately over-applied to learn them — explain the *why* and do them
well; only push back when a pattern is used *incorrectly*. Prefer behavioral tests over
smoke tests.

Domain: orders move through a state machine (draft → placed → paid → shipped →
delivered, with cancel/refund branches); CRUD routers plus an "operations" router for
transitions and automation.

Stack: Python 3.14 (`uuid.uuid7()` IDs), FastAPI, SQLAlchemy 2.0 async + Alembic,
Postgres (`docker compose up -d`), uv, ruff, ty. Check with `uv run pytest`,
`uv run ruff check .`, `uv run ty check`.

Workflow preferences (commits etc.) live in Claude's persistent memory, not here.
