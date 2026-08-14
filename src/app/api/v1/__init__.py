from fastapi import APIRouter

api_router = APIRouter()

# Route modules register themselves here as they are added, e.g.:
# from app.api.v1.routes import orders
# api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
