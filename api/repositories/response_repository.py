from __future__ import annotations

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from repositories.models.entities import Response, User, Vacancy
from services.dto import ResponseStatus


class ResponseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_for_vacancy_owner(self, vacancy_id: int, owner_id: int) -> list[Response]:
        statement = (
            select(Response)
            .join(Vacancy, Vacancy.id == Response.vacancy_id)
            .where(Response.vacancy_id == vacancy_id, Vacancy.owner_id == owner_id)
            .order_by(Response.created_at.desc())
        )
        return list(self.session.scalars(statement))

    def get_for_vacancy_owner(
        self,
        *,
        vacancy_id: int,
        response_id: int,
        owner_id: int,
    ) -> Response | None:
        statement = (
            select(Response)
            .join(Vacancy, Vacancy.id == Response.vacancy_id)
            .where(
                Response.id == response_id,
                Response.vacancy_id == vacancy_id,
                Vacancy.owner_id == owner_id,
            )
        )
        return self.session.scalar(statement)

    def get_by_external_id(self, external_response_id: str) -> Response | None:
        statement = select(Response).where(
            Response.external_response_id == external_response_id
        )
        return self.session.scalar(statement)

    def create(self, response: Response) -> Response:
        self.session.add(response)
        self.session.commit()
        self.session.refresh(response)
        return response

    def save(self, response: Response) -> Response:
        self.session.add(response)
        self.session.commit()
        self.session.refresh(response)
        return response

    def count_new_by_owner(self, owner_id: int) -> int:
        statement = (
            select(func.count(Response.id))
            .join(Vacancy, Vacancy.id == Response.vacancy_id)
            .where(Vacancy.owner_id == owner_id, Response.status == ResponseStatus.NEW)
        )
        return int(self.session.scalar(statement) or 0)

    def count_new_grouped_by_manager(self) -> list[dict[str, Any]]:
        statement = (
            select(
                User.id,
                User.full_name,
                User.email,
                func.count(Response.id).label("new_responses"),
            )
            .outerjoin(Vacancy, Vacancy.owner_id == User.id)
            .outerjoin(
                Response,
                and_(
                    Response.vacancy_id == Vacancy.id,
                    Response.status == ResponseStatus.NEW,
                ),
            )
            .group_by(User.id, User.full_name, User.email)
            .order_by(User.id)
        )
        rows = self.session.execute(statement).all()
        return [
            {
                "manager_id": row.id,
                "manager_name": row.full_name,
                "manager_email": row.email,
                "new_responses": int(row.new_responses or 0),
            }
            for row in rows
        ]
