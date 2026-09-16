from typing import Optional, List, Dict
from app.models.document import Document


class DocumentRepository:
    def __init__(self) -> None:
        self._docs: Dict[str, Document] = {}

    def create(self, document: Document) -> Document:
        self._docs[document.id] = document
        return document

    def get(self, doc_id: str) -> Optional[Document]:
        return self._docs.get(doc_id)

    def list_by_user(self, user_id: str) -> List[Document]:
        return [d for d in self._docs.values() if d.user_id == user_id]
