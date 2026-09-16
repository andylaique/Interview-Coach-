from __future__ import annotations
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import get_settings
from app.models.user import User
from app.repositories import user_repository
from app.schemas.auth import RegisterRequest, LoginRequest, UserOut, TokenResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


class AuthService:
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    def create_access_token(self, user: User) -> str:
        settings = get_settings()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_expire_minutes
        )
        payload = {
            "sub": user.id,
            "email": user.email,
            "name": user.name,
            "exp": expire,
        }
        return jwt.encode(
            payload, settings.jwt_secret, algorithm=settings.jwt_algorithm
        )

    def decode_token(self, token: str) -> dict:
        settings = get_settings()
        try:
            return jwt.decode(
                token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

    def register(self, data: RegisterRequest) -> TokenResponse:
        if user_repository.exists(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        user = User(
            email=data.email.lower().strip(),
            name=data.name.strip(),
            password_hash=self.hash_password(data.password),
        )
        user_repository.create(user)
        token = self.create_access_token(user)
        return TokenResponse(
            access_token=token,
            user=UserOut(
                id=user.id,
                email=user.email,
                name=user.name,
                created_at=user.created_at,
            ),
        )

    def login(self, data: LoginRequest) -> TokenResponse:
        user = user_repository.get_by_email(data.email)
        if not user or not self.verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        token = self.create_access_token(user)
        return TokenResponse(
            access_token=token,
            user=UserOut(
                id=user.id,
                email=user.email,
                name=user.name,
                created_at=user.created_at,
            ),
        )

    def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials | None = Depends(security),
    ) -> User:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )
        payload = self.decode_token(credentials.credentials)
        user = user_repository.get_by_id(payload.get("sub", ""))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return user


auth_service = AuthService()
