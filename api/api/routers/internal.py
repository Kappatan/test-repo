from fastapi import APIRouter

from api.deps import DbSession
from api.schemas.response import ManagerNewResponses
from repositories.response_repository import ResponseRepository
from repositories.vacancy_repository import VacancyRepository
from services.response_service import ResponseService

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/managers/new-responses", response_model=list[ManagerNewResponses])
def get_managers_new_responses(db: DbSession) -> list[ManagerNewResponses]:
    service = ResponseService(
        response_repository=ResponseRepository(db),
        vacancy_repository=VacancyRepository(db),
    )
    return [
        ManagerNewResponses.model_validate(item, from_attributes=True)
        for item in service.count_new_grouped_by_manager()
    ]
