from fastapi import APIRouter, HTTPException, status

from api.deps import CurrentUser, DbSession
from api.schemas.response import MyNewResponses, ResponseRead, ResponseStatusUpdate
from repositories.response_repository import ResponseRepository
from repositories.vacancy_repository import VacancyRepository
from services.dto import ResponseStatusUpdateDTO
from services.response_service import ResponseService

router = APIRouter(tags=["responses"])


@router.get(
    "/vacancies/{vacancy_id}/responses",
    response_model=list[ResponseRead],
)
def list_responses(
    vacancy_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> list[ResponseRead]:
    service = ResponseService(
        response_repository=ResponseRepository(db),
        vacancy_repository=VacancyRepository(db),
    )
    try:
        responses = service.list_for_vacancy(
            vacancy_id=vacancy_id,
            owner_id=current_user.id,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return [
        ResponseRead.model_validate(response, from_attributes=True)
        for response in responses
    ]


@router.patch(
    "/vacancies/{vacancy_id}/responses/{response_id}",
    response_model=ResponseRead,
)
def update_response_status(
    vacancy_id: int,
    response_id: int,
    payload: ResponseStatusUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ResponseRead:
    service = ResponseService(
        response_repository=ResponseRepository(db),
        vacancy_repository=VacancyRepository(db),
    )
    try:
        response = service.update_status(
            ResponseStatusUpdateDTO(
                vacancy_id=vacancy_id,
                response_id=response_id,
                owner_id=current_user.id,
                status=payload.status,
            )
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return ResponseRead.model_validate(response, from_attributes=True)


@router.get("/responses/new-count", response_model=MyNewResponses)
def get_my_new_responses(db: DbSession, current_user: CurrentUser) -> MyNewResponses:
    service = ResponseService(
        response_repository=ResponseRepository(db),
        vacancy_repository=VacancyRepository(db),
    )
    dto = service.count_new_for_owner(current_user.id)
    return MyNewResponses.model_validate(dto, from_attributes=True)
