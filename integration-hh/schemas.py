from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VacancyRef(BaseModel):
    """Упрощённая ссылка на вакансию из webhook HH."""

    model_config = ConfigDict(extra="ignore")

    id: int


class ResumeRef(BaseModel):
    """Упрощённая ссылка на резюме из webhook HH."""

    model_config = ConfigDict(extra="ignore")

    id: str


class HhWebhookItem(BaseModel):
    """Элемент уведомления NEW_RESPONSE_OR_INVITATION_VACANCY.

    Структура упрощена и оставлены только поля, необходимые для задачи.
    Лишние поля из реального webhook-а игнорируются.
    """

    model_config = ConfigDict(extra="ignore")

    id: str
    created_at: datetime | None = None
    vacancy: VacancyRef
    resume: ResumeRef


class HhWebhookPayload(BaseModel):
    """Тело webhook-а HH.

    В реальном API приходит массив элементов; здесь поддерживаем тот же подход.
    """

    model_config = ConfigDict(extra="ignore")

    items: list[HhWebhookItem]

