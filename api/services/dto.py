from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ResponseStatus(str, Enum):
    NEW = "new"
    VIEWED = "viewed"
    REJECTED = "rejected"


@dataclass(slots=True)
class ContactDTO:
    type: str
    value: str


@dataclass(slots=True)
class UserCreateDTO:
    email: str
    full_name: str
    password: str


@dataclass(slots=True)
class LoginDTO:
    email: str
    password: str


@dataclass(slots=True)
class UserDTO:
    id: int
    email: str
    full_name: str


@dataclass(slots=True)
class VacancyCreateDTO:
    owner_id: int
    title: str
    description: str


@dataclass(slots=True)
class VacancyUpdateDTO:
    vacancy_id: int
    owner_id: int
    title: str
    description: str


@dataclass(slots=True)
class VacancyDTO:
    id: int
    title: str
    description: str
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class ResponseStatusUpdateDTO:
    vacancy_id: int
    response_id: int
    owner_id: int
    status: ResponseStatus


@dataclass(slots=True)
class IngestResponseDTO:
    vacancy_id: int
    first_name: str
    middle_name: str | None
    last_name: str
    contacts: list[ContactDTO] = field(default_factory=list)
    external_response_id: str | None = None


@dataclass(slots=True)
class ResponseDTO:
    id: int
    external_response_id: str | None
    first_name: str
    middle_name: str | None
    last_name: str
    contacts: list[ContactDTO]
    status: ResponseStatus
    created_at: datetime


@dataclass(slots=True)
class MyNewResponsesDTO:
    new_responses: int


@dataclass(slots=True)
class ManagerNewResponsesDTO:
    manager_id: int
    manager_name: str
    manager_email: str
    new_responses: int
