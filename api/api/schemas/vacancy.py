from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VacancyCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=3)


class VacancyUpdate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=3)


class VacancyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    created_at: datetime
    updated_at: datetime
