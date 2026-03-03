from __future__ import annotations

from repositories.models.entities import Vacancy
from repositories.vacancy_repository import VacancyRepository
from services.dto import VacancyCreateDTO, VacancyDTO, VacancyUpdateDTO


class VacancyService:
    def __init__(self, vacancy_repository: VacancyRepository) -> None:
        self.vacancy_repository = vacancy_repository

    def create(self, data: VacancyCreateDTO) -> VacancyDTO:
        vacancy = Vacancy(
            owner_id=data.owner_id,
            title=data.title,
            description=data.description,
        )
        vacancy = self.vacancy_repository.create(vacancy)
        return self._to_vacancy_dto(vacancy)

    def list_for_owner(self, owner_id: int) -> list[VacancyDTO]:
        vacancies = self.vacancy_repository.list_by_owner(owner_id)
        return [self._to_vacancy_dto(vacancy) for vacancy in vacancies]

    def update(self, data: VacancyUpdateDTO) -> VacancyDTO:
        vacancy = self.vacancy_repository.get_for_owner(data.vacancy_id, data.owner_id)
        if not vacancy:
            raise LookupError("Vacancy not found.")

        vacancy.title = data.title
        vacancy.description = data.description
        vacancy = self.vacancy_repository.save(vacancy)
        return self._to_vacancy_dto(vacancy)

    @staticmethod
    def _to_vacancy_dto(vacancy: Vacancy) -> VacancyDTO:
        return VacancyDTO(
            id=vacancy.id,
            title=vacancy.title,
            description=vacancy.description,
            created_at=vacancy.created_at,
            updated_at=vacancy.updated_at,
        )
