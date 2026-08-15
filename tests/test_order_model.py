import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.models import Order
from app.domain.order import OrderStatus


async def test_new_order_gets_sane_defaults(migrated_database: str) -> None:
    engine = create_async_engine(migrated_database)
    try:
        factory = async_sessionmaker(engine, expire_on_commit=False)
        async with factory() as session:
            order = Order()
            session.add(order)
            await session.flush()
            await session.refresh(order)

            assert order.id.version == 7, "primary keys must be time-ordered uuid7"
            assert order.status is OrderStatus.DRAFT
            assert order.created_at.tzinfo is not None, "timestamps must be timezone-aware"
            assert order.updated_at.tzinfo is not None
            # no commit: leaving the block rolls the row back
    finally:
        await engine.dispose()


async def test_status_check_constraint_rejects_unknown_values(migrated_database: str) -> None:
    """The CHECK constraint must hold even for writes that bypass the ORM."""
    engine = create_async_engine(migrated_database)
    try:
        factory = async_sessionmaker(engine)
        async with factory() as session:
            # id omitted on purpose: the uuidv7() server default must cover
            # writers that bypass the ORM
            with pytest.raises(IntegrityError, match="ck_orders"):
                await session.execute(text("INSERT INTO orders (status) VALUES ('bogus')"))
    finally:
        await engine.dispose()
