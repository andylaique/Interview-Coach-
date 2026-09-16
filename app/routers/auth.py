from fastapi import APIRouter, Depends
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserOut
from app.services.auth_service import auth_service
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
def register(body: RegisterRequest):
    return auth_service.register(body)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    return auth_service.login(body)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(auth_service.get_current_user)):
    return UserOut(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
    )
