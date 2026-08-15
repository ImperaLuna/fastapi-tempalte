from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Request

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from sqlalchemy.ext.asyncio import AsyncSession


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """One session per request; commit/rollback is the route's business,
    closing is ours. Tests override this dependency to inject their own."""
    factory = request.app.state.session_factory
    async with factory() as session:
        yield session


SessionDep = Annotated["AsyncSession", Depends(get_session)]
