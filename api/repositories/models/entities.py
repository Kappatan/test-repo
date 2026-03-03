from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from repositories.models.base import Base
from services.dto import ResponseStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )

    vacancies: Mapped[list[Vacancy]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )


class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text())
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
    )

    owner: Mapped[User] = relationship(back_populates="vacancies")
    responses: Mapped[list[Response]] = relationship(
        back_populates="vacancy",
        cascade="all, delete-orphan",
    )


class Response(Base):
    __tablename__ = "responses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    external_response_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
    )
    vacancy_id: Mapped[int] = mapped_column(
        ForeignKey("vacancies.id", ondelete="CASCADE"),
        index=True,
    )
    first_name: Mapped[str] = mapped_column(String(255))
    middle_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255))
    contacts: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    status: Mapped[ResponseStatus] = mapped_column(
        SqlEnum(ResponseStatus),
        default=ResponseStatus.NEW,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )

    vacancy: Mapped[Vacancy] = relationship(back_populates="responses")
