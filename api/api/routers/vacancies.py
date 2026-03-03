from fastapi import APIRouter, HTTPException, status

from api.deps import CurrentUser, DbSession
from api.schemas.vacancy import VacancyCreate, VacancyRead, VacancyUpdate
from repositories.vacancy_repository import VacancyRepository
from services.dto import VacancyCreateDTO, VacancyUpdateDTO
from services.vacancy_service import VacancyService

router = APIRouter(prefix="/vacancies", tags=["vacancies"])


@router.post("", response_model=VacancyRead, status_code=status.HTTP_201_CREATED)
def create_vacancy(
    payload: VacancyCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> VacancyRead:
    service = VacancyService(VacancyRepository(db))
    vacancy = service.create(
        VacancyCreateDTO(
            owner_id=current_user.id,
            title=payload.title,
            description=payload.description,
        )
    )
    return VacancyRead.model_validate(vacancy, from_attributes=True)


@router.get("", response_model=list[VacancyRead])
def list_vacancies(db: DbSession, current_user: CurrentUser) -> list[VacancyRead]:
    service = VacancyService(VacancyRepository(db))
    vacancies = service.list_for_owner(current_user.id)
    return [
        VacancyRead.model_validate(vacancy, from_attributes=True)
        for vacancy in vacancies
    ]


@router.put("/{vacancy_id}", response_model=VacancyRead)
def update_vacancy(
    vacancy_id: int,
    payload: VacancyUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> VacancyRead:
    service = VacancyService(VacancyRepository(db))
    try:
        vacancy = service.update(
            VacancyUpdateDTO(
                vacancy_id=vacancy_id,
                owner_id=current_user.id,
                title=payload.title,
                description=payload.description,
            )
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return VacancyRead.model_validate(vacancy, from_attributes=True)
