from datetime import datetime

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Deterministic constraint/index names. Without this, Postgres invents names
# for unnamed constraints, and Alembic can't generate reliable downgrades or
# detect drift (it has no idea what the constraint it should drop is called).
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    # Every datetime column becomes TIMESTAMPTZ. Postgres' plain TIMESTAMP
    # stores wall-clock time with no zone — a notorious source of silent bugs.
    type_annotation_map = {datetime: DateTime(timezone=True)}  # noqa: RUF012


class TimestampMixin:
    """created_at/updated_at maintained by the database, not the application.

    Server-side defaults mean the timestamps are correct no matter who writes
    the row (app, psql, a migration backfill) and use the database clock —
    one clock instead of many app clocks that may disagree.
    """

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
