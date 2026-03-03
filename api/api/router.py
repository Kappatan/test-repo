from fastapi import APIRouter

from api.routers.auth import router as auth_router
from api.routers.internal import router as internal_router
from api.routers.responses import router as responses_router
from api.routers.vacancies import router as vacancies_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(vacancies_router)
api_router.include_router(responses_router)
api_router.include_router(internal_router)
