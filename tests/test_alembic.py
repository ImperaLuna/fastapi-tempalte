from typing import TYPE_CHECKING

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Connection, inspect
from sqlalchemy.ext.asyncio import create_async_engine

import app.db.models  # noqa: F401  # register models on Base.metadata
from app.db.autogen import include_object
from app.db.base import Base

if TYPE_CHECKING:
    from alembic.config import Config


async def test_upgrade_head_runs(migrated_database: str) -> None:
    engine = create_async_engine(migrated_database)
    try:
        async with engine.connect() as conn:
            tables = await conn.run_sync(lambda c: inspect(c).get_table_names())
    finally:
        await engine.dispose()
    assert "alembic_version" in tables


async def test_models_match_migrations(migrated_database: str) -> None:
    """Autogenerate must find no diff between the models and the migrated schema.

    Fails when someone changes a model without generating a migration (or
    edits a migration so it no longer produces what the models declare).
    """

    def diff_against_models(conn: Connection) -> list[object]:
        context = MigrationContext.configure(
            conn,
            opts={
                "compare_type": True,
                "compare_server_default": True,
                "include_object": include_object,
            },
        )
        return compare_metadata(context, Base.metadata)

    engine = create_async_engine(migrated_database)
    try:
        async with engine.connect() as conn:
            diffs = await conn.run_sync(diff_against_models)
    finally:
        await engine.dispose()
    assert diffs == [], f"models and migrations have drifted:\n{diffs}"


def test_full_rollback(fresh_database_url: str, alembic_config: Config) -> None:
    """The whole chain must survive head → base → head in one sweep.
    Runs every downgrade in sequence """
    command.upgrade(alembic_config, "head")
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")
