from datetime import datetime

from pydantic import BaseModel, ConfigDict

from services.dto import ResponseStatus


class Contact(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str
    value: str


class ResponseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_response_id: str | None
    first_name: str
    middle_name: str | None
    last_name: str
    contacts: list[Contact]
    status: ResponseStatus
    created_at: datetime


class ResponseStatusUpdate(BaseModel):
    status: ResponseStatus


class MyNewResponses(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    new_responses: int


class ManagerNewResponses(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    manager_id: int
    manager_name: str
    manager_email: str
    new_responses: int
