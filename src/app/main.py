from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.v1 import api_router

app = FastAPI(title="Order Fulfillment")

app.include_router(health_router)
app.include_router(api_router, prefix="/api/v1")
