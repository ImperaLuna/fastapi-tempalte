import asyncio
import os
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import get_settings

if TYPE_CHECKING:
    from collections.abc import Iterator

REPO_ROOT = Path(__file__).parent.parent


async def _execute_admin(url: str, sql: str) -> None:
    # DDL like CREATE/DROP DATABASE cannot run inside a transaction,
    # hence AUTOCOMMIT.
    engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as conn:
            await conn.execute(text(sql))
    finally:
        await engine.dispose()


@contextmanager
def _database(name: str) -> Iterator[str]:
    """Create database `name` on the compose Postgres, drop it on exit."""
    app_url = make_url(get_settings().database_url)
    admin_url = app_url.set(database="postgres").render_as_string(hide_password=False)
    url = app_url.set(database=name).render_as_string(hide_password=False)

    try:
        asyncio.run(_execute_admin(admin_url, f'DROP DATABASE IF EXISTS "{name}"'))
    except (OSError, DBAPIError):
        pytest.skip("Postgres unavailable — start it with `docker compose up -d db`")

    asyncio.run(_execute_admin(admin_url, f'CREATE DATABASE "{name}"'))
    try:
        yield url
    finally:
        asyncio.run(_execute_admin(admin_url, f'DROP DATABASE "{name}" WITH (FORCE)'))


@contextmanager
def _settings_pointing_at(url: str) -> Iterator[None]:
    """Point app settings (and therefore migrations/env.py) at `url`."""
    previous = os.environ.get("APP_DATABASE_URL")
    os.environ["APP_DATABASE_URL"] = url
    get_settings.cache_clear()
    try:
        yield
    finally:
        if previous is None:
            del os.environ["APP_DATABASE_URL"]
        else:
            os.environ["APP_DATABASE_URL"] = previous
        get_settings.cache_clear()


@pytest.fixture(scope="session")
def alembic_config() -> Config:
    return Config(str(REPO_ROOT / "alembic.ini"))


@pytest.fixture(scope="session")
def test_database_url() -> Iterator[str]:
    """A dedicated, empty `app_test` database; dropped again after the session."""
    with _database("app_test") as url:
        yield url


@pytest.fixture(scope="session")
def migrated_database(test_database_url: str, alembic_config: Config) -> str:
    """The test database with all migrations applied (alembic upgrade head)."""
    with _settings_pointing_at(test_database_url):
        command.upgrade(alembic_config, "head")
    return test_database_url


@pytest.fixture
def fresh_database_url() -> Iterator[str]:
    """A per-test empty database, with settings pointed at it for the duration.

    For tests that run migrations themselves (e.g. the stairway test) and
    must not interfere with the shared session-scoped `migrated_database`.
    """
    with _database("app_test_fresh") as url, _settings_pointing_at(url):
        yield url
