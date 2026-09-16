from fastapi import APIRouter, Depends
from app.schemas.session import ChatRequest, ChatResponse, EndInterviewResponse
from app.services.auth_service import auth_service
from app.services.interview_service import interview_service
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()


class EndRequest(BaseModel):
    session_id: str


@router.post("/chat", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    user: User = Depends(auth_service.get_current_user),
):
    return interview_service.chat(user.id, body.session_id, body.message)


@router.post("/end", response_model=EndInterviewResponse)
def end_interview(
    body: EndRequest,
    user: User = Depends(auth_service.get_current_user),
):
    return interview_service.end_interview(user.id, body.session_id)
