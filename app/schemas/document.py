from __future__ import annotations
from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: str
    filename: str
    uploaded_at: str
    preview: str | None = None


class DocumentUploadResponse(BaseModel):
    document: DocumentOut
