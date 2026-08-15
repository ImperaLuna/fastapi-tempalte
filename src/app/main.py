from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.v1 import api_router
from app.config import get_settings
from app.db.session import build_engine, build_session_factory

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # The engine is created at startup — not import time — so importing this
    # module never opens connections or requires valid settings (tests care).
    engine = build_engine(get_settings().database_url)
    app.state.session_factory = build_session_factory(engine)
    yield
    await engine.dispose()


app = FastAPI(title="Order Fulfillment", lifespan=lifespan)

app.include_router(health_router)
app.include_router(api_router, prefix="/api/v1")
