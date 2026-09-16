from typing import List
import logging

from app.services.groq_client import get_groq_client, with_rate_limit_retry
from app.services.note_service import collapse_repetition
from app.models.database_schema import ChatMessage

logger = logging.getLogger(__name__)

MODEL = "openai/gpt-oss-120b"
MAX_HISTORY_MESSAGES = 10

# Same shared, tight tokens-per-minute budget as note_service.py -- the
# raw transcript of a real video can alone exceed the ENTIRE per-minute
# quota (observed: a 53k-character Arabic transcript requested ~19,400
# tokens on a single call, against an 8000 TPM limit). The generated
# notes are already a distilled, structured summary of the same content
# and are far shorter, so they're used as chat grounding instead of the
# raw transcript -- better token economy AND arguably better grounding
# (same content the user is looking at). A hard cap is kept as a safety
# net regardless of source for unusually long videos.
MAX_CONTEXT_CHARS = 6000


def _system_prompt(context_text: str, language: str) -> str:
    language_instruction = (
        "Respond in Arabic unless the user writes in another language."
        if language == "ar"
        else "Respond in English unless the user writes in another language."
    )

    if len(context_text) > MAX_CONTEXT_CHARS:
        context_text = context_text[:MAX_CONTEXT_CHARS] + " …"

    return (
        "You are a focused assistant that answers questions about ONE "
        "specific video, using ONLY the notes provided below (a structured "
        "summary of the video's content). "
        "If the user asks something unrelated to this video's content, "
        "politely say you can only answer questions about this video and "
        "do not answer the unrelated question. Never invent information "
        "that isn't in the notes. "
        "Format every answer clearly in Markdown: short paragraphs (a blank "
        "line between them), and a bullet list when you're covering more "
        "than one point -- never one dense run-on block of text. "
        f"{language_instruction}\n\n"
        f"--- VIDEO NOTES ---\n{context_text}\n--- END NOTES ---"
    )


def answer(
    context_text: str,
    language: str,
    history: List[ChatMessage],
    user_message: str,
) -> str:
    client = get_groq_client()

    recent_history = history[-MAX_HISTORY_MESSAGES:]
    messages = [{"role": "system", "content": _system_prompt(context_text, language)}]
    for msg in recent_history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": user_message})

    response = with_rate_limit_retry(lambda: client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3,
        frequency_penalty=0.4,
        max_tokens=1024,
    ))

    content = response.choices[0].message.content
    if not content or not content.strip():
        raise RuntimeError("Empty response from chat model")

    return collapse_repetition(content.strip())
