from fastapi import APIRouter

from src.api.v1.endpoints import co2_concentrations

api_router = APIRouter(prefix="/maps")
api_router.include_router(co2_concentrations.router, prefix='/co2-concentration')