from .user_repository import UserRepository
from .document_repository import DocumentRepository
from .session_repository import SessionRepository

user_repository = UserRepository()
document_repository = DocumentRepository()
session_repository = SessionRepository()

__all__ = [
    "UserRepository",
    "DocumentRepository",
    "SessionRepository",
    "user_repository",
    "document_repository",
    "session_repository",
]
