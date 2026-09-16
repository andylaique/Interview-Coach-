import json
import google.generativeai as genai
from fastapi import HTTPException, status

from app.config import get_settings
from app.models.session import Message, PerformanceReport
from app.services.curriculum import get_curriculum_context

SYSTEM_PROMPT = """You are a friendly, professional AI interview coach.

How you talk:
- Use simple, clear English.
- You can use everyday phrases and light slang when it fits.
- Understand informal speech from the candidate (um, like, you know).
- Do not correct their grammar mid-interview unless they ask.

How you interview:
1. Stay in interviewer mode. Ask one clear question at a time.
2. Listen, then ask a useful follow-up when needed.
3. Do not share scoring rules during the interview.
4. Keep answers short: a few sentences, then the next question.
5. If they ask to pause or end, respect that.
6. Use any document context (resume, job notes) to personalize questions.
7. Be kind but honest. Ask for examples, numbers, and trade-offs when useful.

Difficulty rules (follow the chosen level):
- beginner: Simple questions. Basic concepts. Gentle follow-ups. Explain terms if needed.
- intermediate: Realistic job questions. Some depth. Expect clearer structure (e.g. STAR for stories).
- advanced: Harder questions. Edge cases, system design, trade-offs, and deeper reasoning.

If a curriculum track is provided, base technical questions on those topics.
"""


DIFFICULTY_HINTS = {
    "beginner": (
        "Level: BEGINNER. Ask simple, clear questions. "
        "Focus on basics and understanding. Be encouraging."
    ),
    "intermediate": (
        "Level: INTERMEDIATE. Ask realistic job-style questions. "
        "Expect structured answers and some depth."
    ),
    "advanced": (
        "Level: ADVANCED. Ask challenging questions. "
        "Push on edge cases, trade-offs, and deeper reasoning."
    ),
}


class GeminiService:
    def _get_model(self, temperature: float = 0.85, max_tokens: int = 1024):
        settings = get_settings()
        if not settings.gemini_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GEMINI_API_KEY is not set. Add it to the backend .env file.",
            )
        genai.configure(api_key=settings.gemini_api_key)
        return genai.GenerativeModel(
            model_name="gemini-3.6-flash",
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            },
        )

    def generate_reply(
        self,
        history,
        document_context: str,
        job_role: str,
        company: str,
        interview_type: str,
        difficulty: str = "intermediate",
        use_curriculum: bool = False,
        curriculum_track: str = "",
    ) -> str:
        model = self._get_model(temperature=0.85)

        context_block = ""
        if document_context:
            context_block = (
                f"\n\n--- CANDIDATE & COMPANY CONTEXT ---\n"
                f"{document_context[:12000]}\n--- END CONTEXT ---"
            )

        difficulty_block = DIFFICULTY_HINTS.get(
            difficulty, DIFFICULTY_HINTS["intermediate"]
        )

        curriculum_block = ""
        if use_curriculum and curriculum_track:
            text = get_curriculum_context(curriculum_track)
            if text:
                curriculum_block = (
                    f"\n\n--- CODEHIVE CURRICULUM ---\n{text}\n--- END CURRICULUM ---"
                )

        system = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Current interview: {interview_type} interview for {job_role} at {company}.\n"
            f"{difficulty_block}"
            f"{curriculum_block}"
            f"{context_block}"
        )

        chat_history = []
        for msg in history:
            if msg.role == "system":
                continue
            role = "model" if msg.role == "assistant" else "user"
            chat_history.append({"role": role, "parts": [msg.content]})

        contents = [
            {"role": "user", "parts": [system]},
            {
                "role": "model",
                "parts": [
                    "Understood. I will run a clear interview at the given level, "
                    "ask one question at a time, and use the context when it helps."
                ],
            },
            *chat_history,
        ]

        result = model.generate_content(contents)
        return (result.text or "").strip()

    def generate_performance_report(
        self,
        history,
        document_context: str,
        job_role: str,
        company: str,
        interview_type: str,
        difficulty: str = "intermediate",
        use_curriculum: bool = False,
        curriculum_track: str = "",
    ) -> PerformanceReport:
        model = self._get_model(temperature=0.4, max_tokens=2048)

        transcript = "\n\n".join(
            f"{m.role.upper()}: {m.content}"
            for m in history
            if m.role != "system"
        )

        curriculum_note = ""
        if use_curriculum and curriculum_track:
            curriculum_note = (
                f"\nCurriculum track: {curriculum_track}\n"
                f"{get_curriculum_context(curriculum_track)}"
            )

        prompt = f"""You are an expert interview coach. Review this mock interview and write a clear, honest performance report.

Interview type: {interview_type}
Level: {difficulty}
Role: {job_role}
Company: {company}
{curriculum_note}

Document context:
{document_context[:8000]}

TRANSCRIPT:
{transcript}

Return ONLY valid JSON with this shape (no markdown):
{{
  "overall_score": number (0-100),
  "categories": [
    {{ "name": string, "score": number (0-100), "feedback": string }}
  ],
  "strengths": string[],
  "areas_for_improvement": string[],
  "key_moments": [
    {{ "question": string, "answer_summary": string, "feedback": string }}
  ],
  "actionable_tips": string[],
  "summary": string
}}

Include categories like: Communication, Structure & Clarity, Relevance & Depth, Confidence & Presence, Role Fit.
Judge the candidate fairly for the chosen difficulty level.
Use simple English. Be specific and practical.
"""

        result = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.4,
                "max_output_tokens": 2048,
                "response_mime_type": "application/json",
            },
        )
        raw = (result.text or "").strip()
        cleaned = (
            raw.removeprefix("```json")
            .removeprefix("```")
            .removesuffix("```")
            .strip()
        )

        try:
            data = json.loads(cleaned)
            key_moments = []
            for km in data.get("key_moments", []):
                key_moments.append(
                    {
                        "question": km.get("question", ""),
                        "answer_summary": km.get(
                            "answer_summary", km.get("answerSummary", "")
                        ),
                        "feedback": km.get("feedback", ""),
                    }
                )
            return PerformanceReport(
                overall_score=int(data.get("overall_score", 65)),
                categories=data.get("categories", []),
                strengths=data.get("strengths", []),
                areas_for_improvement=data.get("areas_for_improvement", []),
                key_moments=key_moments,
                actionable_tips=data.get("actionable_tips", []),
                summary=data.get("summary", ""),
            )
        except (json.JSONDecodeError, TypeError, ValueError):
            return PerformanceReport(
                overall_score=65,
                categories=[
                    {
                        "name": "Overall",
                        "score": 65,
                        "feedback": "Could not fully parse the report. Try ending the interview again.",
                    }
                ],
                strengths=["Completed the interview session"],
                areas_for_improvement=["Try the report again if needed"],
                key_moments=[],
                actionable_tips=["Practice answering with clear examples"],
                summary=cleaned[:500],
            )


gemini_service = GeminiService()
