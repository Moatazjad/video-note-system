from pathlib import Path
from typing import Optional, Tuple
from app.core.config import settings
import logging
from groq import Groq

logger = logging.getLogger(__name__)


class TranscriptionService:
    _client: Optional[Groq] = None

    @classmethod
    def _get_client(cls) -> Groq:
        if cls._client is None:
            api_key = settings.GROQ_API_KEY
            if not api_key:
                raise RuntimeError(
                    "GROQ_API_KEY is not set. Get a free key at https://console.groq.com"
                )
            cls._client = Groq(api_key=api_key)
            logger.info("Groq client initialized")
        return cls._client

    @staticmethod
    def transcribe(
        audio_path: Path,
        language: Optional[str] = None,
    ) -> Tuple[str, str]:
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if language == "en":
            language = None

        try:
            client = TranscriptionService._get_client()

            logger.info(f"Transcribing: {audio_path.name} (language: {language or 'auto'})")

            with audio_path.open("rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=(audio_path.name, audio_file.read()),
                    language=language,
                    response_format="text",
                )

            transcript = response if isinstance(response, str) else response.text
            detected_language = language if language else "unknown"

            logger.info(f"Transcribed {len(transcript)} characters from {audio_path.name}")

            return transcript, detected_language

        except Exception as exc:
            logger.error(f"Transcription failed for {audio_path.name}: {exc}")
            raise RuntimeError(f"Transcription failed: {exc}") from exc
