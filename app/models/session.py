from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import uuid


@dataclass
class Message:
    role: str
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class PerformanceReport:
    overall_score: int
    categories: List[Dict[str, Any]]
    strengths: List[str]
    areas_for_improvement: List[str]
    key_moments: List[Dict[str, str]]
    actionable_tips: List[str]
    summary: str
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class InterviewSession:
    user_id: str
    title: str
    job_role: str
    company: str
    interview_type: str
    difficulty: str
    use_curriculum: bool
    curriculum_track: str
    document_ids: List[str]
    document_context: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = field(default_factory=list)
    status: str = "setup"
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    performance_report: Optional[PerformanceReport] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
