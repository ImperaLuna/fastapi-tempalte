"""Behavioral proof of the db_session fixture's isolation guarantee.

These two tests are order-dependent on purpose: the first commits, the
second asserts nothing survived. If the rollback isolation ever breaks,
the second test fails.
"""

from typing import TYPE_CHECKING

from sqlalchemy import func, select

from app.db.models import Order

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def test_commit_inside_a_test_works(db_session: AsyncSession) -> None:
    db_session.add(Order())
    await db_session.commit()  # becomes a SAVEPOINT release, not a real commit

    count = await db_session.scalar(select(func.count()).select_from(Order))
    assert count == 1


async def test_previous_commit_left_no_trace(db_session: AsyncSession) -> None:
    count = await db_session.scalar(select(func.count()).select_from(Order))
    assert count == 0
