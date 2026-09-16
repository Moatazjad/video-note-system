import logging
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.services import caption_service
from app.services.video_service import VideoService
from app.services.audio_chunker import AudioChunker, CHUNK_DURATION
from app.services.transcription_service import TranscriptionService

logger = logging.getLogger(__name__)

LANGUAGE_MAP = {"en": "english", "ar": "arabic"}


def _whisper_fallback(
    url: str,
    language: str,
    start_time: Optional[float],
    end_time: Optional[float],
) -> Tuple[str, List[Dict], Optional[str], Path]:
    audio_path, _duration = VideoService.download_audio_only(
        url, start_time=start_time, end_time=end_time
    )

    chunk_paths = AudioChunker.split_audio(Path(audio_path))
    n = len(chunk_paths)

    transcripts: List[Optional[str]] = [None] * n
    detected_langs: List[Optional[str]] = [None] * n
    segments_by_chunk: List[List[Dict]] = [[] for _ in range(n)]

    try:
        with ThreadPoolExecutor(max_workers=min(n, 5)) as executor:
            future_to_index = {
                executor.submit(TranscriptionService.transcribe, Path(p), language): i
                for i, p in enumerate(chunk_paths)
            }
            for future in as_completed(future_to_index):
                i = future_to_index[future]
                text, lang, segs = future.result()
                transcripts[i] = text
                detected_langs[i] = lang

                # Each chunk's segments are timestamped relative to that
                # chunk, not the full audio -- rebase onto the full timeline.
                offset = i * CHUNK_DURATION if n > 1 else 0
                segments_by_chunk[i] = [
                    {"start": s["start"] + offset, "end": s["end"] + offset, "text": s["text"]}
                    for s in segs
                ]
    finally:
        if n > 1:
            AudioChunker.cleanup_chunks(chunk_paths)

    full_transcript = " ".join(t for t in transcripts if t)
    all_segments = [seg for chunk_segs in segments_by_chunk for seg in chunk_segs]
    detected_language = next((l for l in detected_langs if l and l != "unknown"), None)

    return full_transcript, all_segments, detected_language, audio_path


def acquire(
    url: str,
    language: str,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
) -> Tuple[str, List[Dict], str, str, Optional[Path]]:
    """Acquire a timestamped transcript for a video: try YouTube captions
    first (zero video/audio download), fall back to audio-only download +
    Whisper only when no caption track exists at all.

    Returns (transcript, segments, transcript_source, detected_language, audio_path).
    audio_path is None when the captions path was used (nothing downloaded).
    """
    captions_result = caption_service.get_captions(url, language, start_time, end_time)
    if captions_result:
        transcript, segments = captions_result
        detected_language = LANGUAGE_MAP.get(language, language)
        logger.info("Transcript acquired via captions (no download)")
        return transcript, segments, "captions", detected_language, None

    logger.info("No captions available; falling back to audio download + Whisper")
    transcript, segments, detected_language, audio_path = _whisper_fallback(
        url, language, start_time, end_time
    )
    if not full_transcript_ok(transcript):
        raise RuntimeError("Empty transcription result")

    return (
        transcript,
        segments,
        "whisper",
        detected_language or LANGUAGE_MAP.get(language, language),
        audio_path,
    )


def full_transcript_ok(transcript: str) -> bool:
    return bool(transcript and transcript.strip())
