from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from repositories.models.entities import Vacancy


class VacancyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, vacancy: Vacancy) -> Vacancy:
        self.session.add(vacancy)
        self.session.commit()
        self.session.refresh(vacancy)
        return vacancy

    def list_by_owner(self, owner_id: int) -> list[Vacancy]:
        statement = (
            select(Vacancy)
            .where(Vacancy.owner_id == owner_id)
            .order_by(Vacancy.created_at.desc())
        )
        return list(self.session.scalars(statement))

    def get_by_id(self, vacancy_id: int) -> Vacancy | None:
        statement = select(Vacancy).where(Vacancy.id == vacancy_id)
        return self.session.scalar(statement)

    def get_for_owner(self, vacancy_id: int, owner_id: int) -> Vacancy | None:
        statement = select(Vacancy).where(
            Vacancy.id == vacancy_id,
            Vacancy.owner_id == owner_id,
        )
        return self.session.scalar(statement)

    def save(self, vacancy: Vacancy) -> Vacancy:
        self.session.add(vacancy)
        self.session.commit()
        self.session.refresh(vacancy)
        return vacancy
