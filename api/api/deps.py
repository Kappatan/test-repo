from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from repositories.models.entities import User
from repositories.session import get_session
from repositories.user_repository import UserRepository
from services.security import bearer_scheme, decode_access_token

DbSession = Annotated[Session, Depends(get_session)]


def get_current_user(
    db: DbSession,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
        )

    try:
        payload = decode_access_token(credentials.credentials)
        subject = payload.get("sub")
        if subject is None:
            raise ValueError("Token subject is missing.")
        user_id = int(subject)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token.",
        ) from None

    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
