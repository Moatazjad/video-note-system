from fastapi import APIRouter
from app.core.config import settings

from app.api.v1.endpoints import health, process, status, result

api_router = APIRouter(prefix=settings.API_V1_PREFIX)

api_router.include_router(health.router, tags=["health"])
api_router.include_router(process.router, tags=["process"])
api_router.include_router(status.router, tags=["status"])
api_router.include_router(result.router, tags=["result"])
