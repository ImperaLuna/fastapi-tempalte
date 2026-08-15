from typing import TYPE_CHECKING

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.db.models import Order
from app.domain.order import OrderStatus

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def test_new_order_gets_sane_defaults(db_session: AsyncSession) -> None:
    order = Order()
    db_session.add(order)
    await db_session.flush()
    await db_session.refresh(order)

    assert order.id.version == 7, "primary keys must be time-ordered uuid7"
    assert order.status is OrderStatus.DRAFT
    assert order.created_at.tzinfo is not None, "timestamps must be timezone-aware"
    assert order.updated_at.tzinfo is not None


async def test_status_check_constraint_rejects_unknown_values(db_session: AsyncSession) -> None:
    """The CHECK constraint must hold even for writes that bypass the ORM."""
    # id omitted on purpose: the uuidv7() server default must cover
    # writers that bypass the ORM
    with pytest.raises(IntegrityError, match="ck_orders"):
        await db_session.execute(text("INSERT INTO orders (status) VALUES ('bogus')"))
