from fastapi import APIRouter, Depends, UploadFile, File
from app.schemas.document import DocumentUploadResponse
from app.services.auth_service import auth_service
from app.services.document_service import document_service
from app.models.user import User

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    user: User = Depends(auth_service.get_current_user),
):
    doc = await document_service.upload(user.id, file)
    return DocumentUploadResponse(document=doc)
