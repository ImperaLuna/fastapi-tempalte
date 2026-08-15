from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def build_engine(url: str) -> AsyncEngine:
    return create_async_engine(url)


def build_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    # expire_on_commit=False: after a commit, ORM objects keep their loaded
    # state instead of expiring. With async sessions the default (True) is a
    # trap — any attribute access after commit triggers implicit IO, which
    # asyncio forbids, so you get MissingGreenlet errors.
    return async_sessionmaker(engine, expire_on_commit=False)
