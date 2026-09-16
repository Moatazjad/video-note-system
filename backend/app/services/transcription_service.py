from pathlib import Path
from typing import Optional, Tuple, List, Dict
import logging

from app.services.groq_client import get_groq_client

logger = logging.getLogger(__name__)


def _normalize_segments(raw_segments) -> List[Dict]:
    segments = []
    for seg in raw_segments or []:
        start = seg.get("start") if isinstance(seg, dict) else getattr(seg, "start", None)
        end = seg.get("end") if isinstance(seg, dict) else getattr(seg, "end", None)
        text = seg.get("text") if isinstance(seg, dict) else getattr(seg, "text", None)
        if start is None or end is None or text is None:
            continue
        segments.append({"start": float(start), "end": float(end), "text": text.strip()})
    return segments


class TranscriptionService:
    @staticmethod
    def transcribe(
        audio_path: Path,
        language: Optional[str] = None,
    ) -> Tuple[str, str, List[Dict]]:
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if language == "en":
            language = None

        try:
            client = get_groq_client()

            logger.info(f"Transcribing: {audio_path.name} (language: {language or 'auto'})")

            with audio_path.open("rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=(audio_path.name, audio_file.read()),
                    language=language,
                    response_format="verbose_json",
                )

            transcript = response.text
            detected_language = getattr(response, "language", None) or (
                language if language else "unknown"
            )
            segments = _normalize_segments(getattr(response, "segments", None))

            logger.info(f"Transcribed {len(transcript)} characters from {audio_path.name}")

            return transcript, detected_language, segments

        except Exception as exc:
            logger.error(f"Transcription failed for {audio_path.name}: {exc}")
            raise RuntimeError(f"Transcription failed: {exc}") from exc
