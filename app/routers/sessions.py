from fastapi import APIRouter, Depends
from typing import List
from app.schemas.session import SessionCreate, SessionOut, SessionListItem
from app.services.auth_service import auth_service
from app.services.interview_service import interview_service
from app.models.user import User

router = APIRouter()


@router.get("", response_model=List[SessionListItem])
def list_sessions(user: User = Depends(auth_service.get_current_user)):
    return interview_service.list_sessions(user.id)


@router.post("", response_model=SessionOut)
def create_session(
    body: SessionCreate,
    user: User = Depends(auth_service.get_current_user),
):
    return interview_service.create_session(user.id, body)


@router.get("/{session_id}", response_model=SessionOut)
def get_session(
    session_id: str,
    user: User = Depends(auth_service.get_current_user),
):
    return interview_service.get_session(user.id, session_id)
