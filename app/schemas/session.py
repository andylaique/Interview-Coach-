from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal


CurriculumTrack = Literal[
    "",
    "frontend",
    "backend",
    "data_ml",
    "iot",
    "mobile",
    "product_management",
    "qa",
    "cyber_security",
    "product_design",
    "ux_research",
]


class SessionCreate(BaseModel):
    title: str = Field(default="", max_length=200)
    job_role: str = Field(min_length=1, max_length=150)
    company: str = Field(min_length=1, max_length=150)
    interview_type: Literal["behavioral", "technical", "mixed", "case"] = "mixed"
    difficulty: Literal["beginner", "intermediate", "advanced"] = "intermediate"
    use_curriculum: bool = False
    curriculum_track: CurriculumTrack = ""
    document_ids: List[str] = Field(default_factory=list)


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    timestamp: str


class PerformanceReportOut(BaseModel):
    overall_score: int
    categories: List[Dict[str, Any]]
    strengths: List[str]
    areas_for_improvement: List[str]
    key_moments: List[Dict[str, str]]
    actionable_tips: List[str]
    summary: str
    generated_at: str


class SessionOut(BaseModel):
    id: str
    title: str
    job_role: str
    company: str
    interview_type: str
    difficulty: str
    use_curriculum: bool
    curriculum_track: str
    document_ids: List[str]
    messages: List[MessageOut]
    status: str
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    performance_report: Optional[PerformanceReportOut] = None
    created_at: str


class SessionListItem(BaseModel):
    id: str
    title: str
    job_role: str
    company: str
    interview_type: str
    difficulty: str
    status: str
    created_at: str
    overall_score: Optional[int] = None


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=1, max_length=8000)


class ChatResponse(BaseModel):
    reply: str
    message_id: str


class EndInterviewResponse(BaseModel):
    report: PerformanceReportOut
    session: SessionOut
