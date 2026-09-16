"""
PostgreSQL-backed helpers for users and JSON store items.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.db_models import UserRow, StoreRow
from app.models.user import User


def _session() -> Session:
    if SessionLocal is None:
        init_db()
    return SessionLocal()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class PgUserRepository:
    def get_by_email(self, email: str) -> Optional[User]:
        db = _session()
        try:
            row = db.query(UserRow).filter(UserRow.email == email.lower().strip()).first()
            if not row:
                return None
            return User(
                id=row.id,
                email=row.email,
                name=row.name,
                password_hash=row.password_hash,
                created_at=row.created_at,
            )
        finally:
            db.close()

    def get_by_id(self, user_id: str) -> Optional[User]:
        db = _session()
        try:
            row = db.query(UserRow).filter(UserRow.id == user_id).first()
            if not row:
                return None
            return User(
                id=row.id,
                email=row.email,
                name=row.name,
                password_hash=row.password_hash,
                created_at=row.created_at,
            )
        finally:
            db.close()

    def create(self, user: User) -> User:
        db = _session()
        try:
            row = UserRow(
                id=user.id,
                email=user.email.lower().strip(),
                name=user.name,
                password_hash=user.password_hash,
                created_at=user.created_at,
            )
            db.add(row)
            db.commit()
            return user
        finally:
            db.close()

    def exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None


class PgStore:
    """Save and load JSON documents by kind (chat, note, event, ...)."""

    def put(self, user_id: str, kind: str, data: dict, item_id: str | None = None) -> str:
        db = _session()
        try:
            iid = item_id or data.get("id") or str(uuid.uuid4())
            data = {**data, "id": iid}
            row = db.query(StoreRow).filter(StoreRow.id == iid).first()
            if row:
                row.data = data
                row.updated_at = _now()
            else:
                row = StoreRow(
                    id=iid,
                    user_id=user_id,
                    kind=kind,
                    data=data,
                    created_at=data.get("created_at") or _now(),
                    updated_at=_now(),
                )
                db.add(row)
            db.commit()
            return iid
        finally:
            db.close()

    def get(self, item_id: str) -> Optional[dict]:
        db = _session()
        try:
            row = db.query(StoreRow).filter(StoreRow.id == item_id).first()
            return dict(row.data) if row else None
        finally:
            db.close()

    def list(self, user_id: str, kind: str, limit: int = 100) -> List[dict]:
        db = _session()
        try:
            rows = (
                db.query(StoreRow)
                .filter(StoreRow.user_id == user_id, StoreRow.kind == kind)
                .order_by(StoreRow.created_at.desc())
                .limit(limit)
                .all()
            )
            return [dict(r.data) for r in rows]
        finally:
            db.close()

    def list_all_kind(self, kind: str, limit: int = 500) -> List[dict]:
        db = _session()
        try:
            rows = (
                db.query(StoreRow)
                .filter(StoreRow.kind == kind)
                .order_by(StoreRow.created_at.desc())
                .limit(limit)
                .all()
            )
            return [dict(r.data) for r in rows]
        finally:
            db.close()

    def delete(self, item_id: str, user_id: str) -> bool:
        db = _session()
        try:
            row = (
                db.query(StoreRow)
                .filter(StoreRow.id == item_id, StoreRow.user_id == user_id)
                .first()
            )
            if not row:
                return False
            db.delete(row)
            db.commit()
            return True
        finally:
            db.close()

    def upsert_singleton(self, user_id: str, kind: str, data: dict) -> dict:
        """One document per user per kind (e.g. settings, profile)."""
        db = _session()
        try:
            row = (
                db.query(StoreRow)
                .filter(StoreRow.user_id == user_id, StoreRow.kind == kind)
                .first()
            )
            data = {**data, "user_id": user_id}
            if row:
                data["id"] = row.id
                row.data = data
                row.updated_at = _now()
            else:
                iid = str(uuid.uuid4())
                data["id"] = iid
                row = StoreRow(
                    id=iid,
                    user_id=user_id,
                    kind=kind,
                    data=data,
                    created_at=_now(),
                    updated_at=_now(),
                )
                db.add(row)
            db.commit()
            return data
        finally:
            db.close()

    def get_singleton(self, user_id: str, kind: str) -> Optional[dict]:
        db = _session()
        try:
            row = (
                db.query(StoreRow)
                .filter(StoreRow.user_id == user_id, StoreRow.kind == kind)
                .first()
            )
            return dict(row.data) if row else None
        finally:
            db.close()


pg_users = PgUserRepository()
pg_store = PgStore()