from typing import Optional, List, Dict
from app.models.session import InterviewSession, Message


class SessionRepository:
    def __init__(self) -> None:
        self._sessions: Dict[str, InterviewSession] = {}

    def create(self, session: InterviewSession) -> InterviewSession:
        self._sessions[session.id] = session
        return session

    def get(self, session_id: str) -> Optional[InterviewSession]:
        return self._sessions.get(session_id)

    def list_by_user(self, user_id: str) -> List[InterviewSession]:
        items = [s for s in self._sessions.values() if s.user_id == user_id]
        return sorted(items, key=lambda s: s.created_at, reverse=True)

    def update(self, session: InterviewSession) -> InterviewSession:
        self._sessions[session.id] = session
        return session

    def add_message(self, session_id: str, message: Message) -> Optional[Message]:
        session = self._sessions.get(session_id)
        if not session:
            return None
        session.messages.append(message)
        self._sessions[session_id] = session
        return message
