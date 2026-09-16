from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class User:
    email: str
    name: str
    password_hash: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
