from fastapi import APIRouter, HTTPException, status

from api.deps import DbSession
from api.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserRead
from repositories.user_repository import UserRepository
from services.dto import LoginDTO, UserCreateDTO
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: UserCreate, db: DbSession) -> UserRead:
    service = AuthService(UserRepository(db))
    try:
        user = service.register(
            UserCreateDTO(
                email=str(payload.email),
                full_name=payload.full_name,
                password=payload.password,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return UserRead.model_validate(user, from_attributes=True)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    service = AuthService(UserRepository(db))
    try:
        token = service.login(
            LoginDTO(
                email=str(payload.email),
                password=payload.password,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    return TokenResponse(access_token=token)
