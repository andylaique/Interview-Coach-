from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class Document:
    user_id: str
    filename: str
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    uploaded_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
