from __future__ import annotations

from typing import Any

from repositories.models.entities import Response
from repositories.response_repository import ResponseRepository
from repositories.vacancy_repository import VacancyRepository
from services.dto import (
    ContactDTO,
    IngestResponseDTO,
    ManagerNewResponsesDTO,
    MyNewResponsesDTO,
    ResponseDTO,
    ResponseStatusUpdateDTO,
)


class ResponseService:
    def __init__(
        self,
        *,
        response_repository: ResponseRepository,
        vacancy_repository: VacancyRepository,
    ) -> None:
        self.response_repository = response_repository
        self.vacancy_repository = vacancy_repository

    def list_for_vacancy(
        self,
        *,
        vacancy_id: int,
        owner_id: int,
    ) -> list[ResponseDTO]:
        vacancy = self.vacancy_repository.get_for_owner(vacancy_id, owner_id)
        if not vacancy:
            raise LookupError("Vacancy not found.")
        responses = self.response_repository.list_for_vacancy_owner(vacancy_id, owner_id)
        return [self._to_response_dto(response) for response in responses]

    def update_status(self, data: ResponseStatusUpdateDTO) -> ResponseDTO:
        response = self.response_repository.get_for_vacancy_owner(
            vacancy_id=data.vacancy_id,
            response_id=data.response_id,
            owner_id=data.owner_id,
        )
        if not response:
            raise LookupError("Response not found.")

        response.status = data.status
        response = self.response_repository.save(response)
        return self._to_response_dto(response)

    def count_new_for_owner(self, owner_id: int) -> MyNewResponsesDTO:
        return MyNewResponsesDTO(
            new_responses=self.response_repository.count_new_by_owner(owner_id)
        )

    def count_new_grouped_by_manager(self) -> list[ManagerNewResponsesDTO]:
        return [
            ManagerNewResponsesDTO(**item)
            for item in self.response_repository.count_new_grouped_by_manager()
        ]

    def ingest_from_queue(self, data: IngestResponseDTO) -> bool:
        if not isinstance(data.vacancy_id, int):
            raise ValueError("vacancy_id must be an integer.")

        vacancy = self.vacancy_repository.get_by_id(data.vacancy_id)
        if not vacancy:
            return False

        if data.external_response_id and self.response_repository.get_by_external_id(
            data.external_response_id
        ):
            return False

        if not data.first_name or not data.last_name:
            raise ValueError("Response must contain first_name and last_name.")

        if any(not item.type or not item.value for item in data.contacts):
            raise ValueError("Each contact must contain type and value.")

        response = Response(
            vacancy_id=data.vacancy_id,
            first_name=data.first_name,
            middle_name=data.middle_name,
            last_name=data.last_name,
            contacts=[
                {"type": item.type, "value": item.value}
                for item in data.contacts
            ],
            external_response_id=data.external_response_id,
        )
        self.response_repository.create(response)
        return True

    @staticmethod
    def _to_response_dto(response: Response) -> ResponseDTO:
        contacts: list[Any] = response.contacts or []
        return ResponseDTO(
            id=response.id,
            external_response_id=response.external_response_id,
            first_name=response.first_name,
            middle_name=response.middle_name,
            last_name=response.last_name,
            contacts=[
                ContactDTO(
                    type=str(item.get("type", "")).strip(),
                    value=str(item.get("value", "")).strip(),
                )
                for item in contacts
                if isinstance(item, dict)
            ],
            status=response.status,
            created_at=response.created_at,
        )
