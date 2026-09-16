from datetime import datetime, timezone
from fastapi import HTTPException, status

from app.models.session import InterviewSession, Message, PerformanceReport
from app.repositories import document_repository, session_repository
from app.schemas.session import (
    SessionCreate,
    SessionOut,
    SessionListItem,
    MessageOut,
    PerformanceReportOut,
    ChatResponse,
    EndInterviewResponse,
)
from app.services.gemini_service import gemini_service


def _report_to_out(report: PerformanceReport) -> PerformanceReportOut:
    return PerformanceReportOut(
        overall_score=report.overall_score,
        categories=report.categories,
        strengths=report.strengths,
        areas_for_improvement=report.areas_for_improvement,
        key_moments=report.key_moments,
        actionable_tips=report.actionable_tips,
        summary=report.summary,
        generated_at=report.generated_at,
    )


def _session_to_out(session: InterviewSession) -> SessionOut:
    return SessionOut(
        id=session.id,
        title=session.title,
        job_role=session.job_role,
        company=session.company,
        interview_type=session.interview_type,
        difficulty=session.difficulty,
        use_curriculum=session.use_curriculum,
        curriculum_track=session.curriculum_track,
        document_ids=session.document_ids,
        messages=[
            MessageOut(
                id=m.id,
                role=m.role,
                content=m.content,
                timestamp=m.timestamp,
            )
            for m in session.messages
        ],
        status=session.status,
        started_at=session.started_at,
        ended_at=session.ended_at,
        performance_report=(
            _report_to_out(session.performance_report)
            if session.performance_report
            else None
        ),
        created_at=session.created_at,
    )


class InterviewService:
    def create_session(self, user_id: str, data: SessionCreate) -> SessionOut:
        docs_text_parts = []
        for doc_id in data.document_ids:
            doc = document_repository.get(doc_id)
            if doc and doc.user_id == user_id:
                docs_text_parts.append(f"=== {doc.filename} ===\n{doc.content}")

        title = data.title.strip() or f"{data.job_role} at {data.company}"
        track = data.curriculum_track if data.use_curriculum else ""

        session = InterviewSession(
            user_id=user_id,
            title=title,
            job_role=data.job_role.strip(),
            company=data.company.strip(),
            interview_type=data.interview_type,
            difficulty=data.difficulty,
            use_curriculum=data.use_curriculum,
            curriculum_track=track or "",
            document_ids=data.document_ids,
            document_context="\n\n".join(docs_text_parts),
        )
        session_repository.create(session)
        return _session_to_out(session)

    def list_sessions(self, user_id: str):
        sessions = session_repository.list_by_user(user_id)
        return [
            SessionListItem(
                id=s.id,
                title=s.title,
                job_role=s.job_role,
                company=s.company,
                interview_type=s.interview_type,
                difficulty=getattr(s, "difficulty", "intermediate"),
                status=s.status,
                created_at=s.created_at,
                overall_score=(
                    s.performance_report.overall_score
                    if s.performance_report
                    else None
                ),
            )
            for s in sessions
        ]

    def get_session(self, user_id: str, session_id: str) -> SessionOut:
        session = session_repository.get(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )
        return _session_to_out(session)

    def chat(self, user_id: str, session_id: str, message: str) -> ChatResponse:
        session = session_repository.get(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )
        if session.status == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview already completed",
            )

        if session.status == "setup":
            session.status = "in_progress"
            session.started_at = datetime.now(timezone.utc).isoformat()
            session_repository.update(session)

        user_msg = Message(role="user", content=message)
        session_repository.add_message(session_id, user_msg)

        session = session_repository.get(session_id)
        reply_text = gemini_service.generate_reply(
            history=session.messages,
            document_context=session.document_context,
            job_role=session.job_role,
            company=session.company,
            interview_type=session.interview_type,
            difficulty=getattr(session, "difficulty", "intermediate"),
            use_curriculum=getattr(session, "use_curriculum", False),
            curriculum_track=getattr(session, "curriculum_track", "") or "",
        )

        assistant_msg = Message(role="assistant", content=reply_text)
        session_repository.add_message(session_id, assistant_msg)

        return ChatResponse(reply=reply_text, message_id=assistant_msg.id)

    def end_interview(self, user_id: str, session_id: str) -> EndInterviewResponse:
        session = session_repository.get(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )
        if len(session.messages) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview too short to generate a report",
            )

        report = gemini_service.generate_performance_report(
            history=session.messages,
            document_context=session.document_context,
            job_role=session.job_role,
            company=session.company,
            interview_type=session.interview_type,
            difficulty=getattr(session, "difficulty", "intermediate"),
            use_curriculum=getattr(session, "use_curriculum", False),
            curriculum_track=getattr(session, "curriculum_track", "") or "",
        )

        session.status = "completed"
        session.ended_at = datetime.now(timezone.utc).isoformat()
        session.performance_report = report
        session_repository.update(session)

        return EndInterviewResponse(
            report=_report_to_out(report),
            session=_session_to_out(session),
        )


interview_service = InterviewService()
