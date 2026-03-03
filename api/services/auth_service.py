from __future__ import annotations

from repositories.models.entities import User
from repositories.user_repository import UserRepository
from services.dto import LoginDTO, UserCreateDTO, UserDTO
from services.security import create_access_token, get_password_hash, verify_password


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def register(self, data: UserCreateDTO) -> UserDTO:
        existing_user = self.user_repository.get_by_email(data.email)
        if existing_user:
            raise ValueError("User with this email already exists.")

        user = User(
            email=data.email,
            full_name=data.full_name,
            password_hash=get_password_hash(data.password),
        )
        user = self.user_repository.create(user)
        return self._to_user_dto(user)

    def login(self, data: LoginDTO) -> str:
        user = self.user_repository.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise ValueError("Invalid email or password.")

        return create_access_token(str(user.id))

    @staticmethod
    def _to_user_dto(user: User) -> UserDTO:
        return UserDTO(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
        )
