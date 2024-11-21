from fastapi import APIRouter

from src.api.v1.endpoints import maps

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(maps.router, prefix='/maps')