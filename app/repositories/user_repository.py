from typing import Optional
from app.database import SessionLocal, get_engine
from app.models_db import UserRow
from app.models.user import User

class UserRepository:
    def get_by_email(self, email: str) -> Optional[User]:
        get_engine()
        db = SessionLocal()
        try:
            row = db.query(UserRow).filter(UserRow.email == email.lower().strip()).first()
            return self._to(row) if row else None
        finally:
            db.close()

    def get_by_id(self, user_id: str) -> Optional[User]:
        get_engine()
        db = SessionLocal()
        try:
            row = db.query(UserRow).filter(UserRow.id == user_id).first()
            return self._to(row) if row else None
        finally:
            db.close()

    def create(self, user: User) -> User:
        get_engine()
        db = SessionLocal()
        try:
            db.add(UserRow(id=user.id, email=user.email.lower().strip(), name=user.name, password_hash=user.password_hash))
            db.commit()
            return user
        finally:
            db.close()

    def exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None

    def _to(self, row: UserRow) -> User:
        return User(id=row.id, email=row.email, name=row.name, password_hash=row.password_hash,
                    created_at=row.created_at.isoformat() if row.created_at else None)
