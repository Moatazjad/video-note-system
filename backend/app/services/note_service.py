from typing import Optional
from groq import Groq
from app.core.config import settings
from app.utils.templates import get_template


class NoteService:
    _client: Optional[Groq] = None

    @classmethod
    def _get_client(cls) -> Groq:
        if cls._client is None:
            if not settings.GROQ_API_KEY:
                raise RuntimeError(
                    "GROQ_API_KEY is not set. Note generation cannot run."
                )
            cls._client = Groq(api_key=settings.GROQ_API_KEY)
        return cls._client

    @staticmethod
    def generate_notes(
        transcript: str,
        template_type: str = "educational",
        language: str = "en",
    ) -> str:
        if not transcript or not transcript.strip():
            raise ValueError("Transcript cannot be empty")

        valid_templates = {"educational", "business", "research"}
        if template_type not in valid_templates:
            raise ValueError(
                f"Invalid template_type: {template_type}. "
                f"Must be one of: {', '.join(valid_templates)}"
            )

        try:
            client = NoteService._get_client()
            template = get_template(template_type, language)

            prompt = f"{template}\n\nTranscript:\n{transcript}"

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an elite technical note generator.\n"
                            "Generate deeply structured, highly condensed, high-signal Markdown notes.\n"
                            "- Use clear heading hierarchy (# ## ###)\n"
                            "- Extract core insights, not surface summaries\n"
                            "- Remove filler language\n"
                            "- Highlight key principles and patterns\n"
                            "- Use bullet points for logic steps\n"
                            "- Use bold for key ideas\n"
                            "- Avoid repetition\n"
                            "- No commentary\n"
                            "- Output only the final notes"
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.6,
                max_tokens=4096,
            )

            notes = response.choices[0].message.content

            if not notes or not notes.strip():
                raise RuntimeError("Empty response from LLM")

            return notes.strip()

        except Exception as exc:
            raise RuntimeError(f"Note generation failed: {exc}") from exc
