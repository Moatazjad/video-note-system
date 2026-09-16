import logging
from typing import Optional, Tuple, List, Dict

import yt_dlp

from app.utils.vtt_parser import parse_vtt, segments_to_text

logger = logging.getLogger(__name__)


def _find_track_url(tracks_by_lang: Dict, language: str) -> Optional[str]:
    """Look for a vtt-format track for `language`, trying an exact key match
    first, then any key that starts with or contains the language code
    (covers auto-translated tracks like 'ar-en' = Arabic from English, whose
    exact naming can vary)."""
    candidates = []

    if language in tracks_by_lang:
        candidates.append(language)

    for key in tracks_by_lang:
        if key == language:
            continue
        if key.startswith(f"{language}-") or key.startswith(f"{language}_"):
            candidates.append(key)

    for key in candidates:
        for fmt in tracks_by_lang[key]:
            if fmt.get("ext") == "vtt" and fmt.get("url"):
                return fmt["url"]

    return None


def get_captions(
    url: str,
    language: str,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
) -> Optional[Tuple[str, List[Dict]]]:
    """Fetch a caption track for `url` in `language` (manual, then
    auto-generated, then auto-translated) with NO video/audio download.
    Returns (full_text, segments) or None if no usable track exists."""

    ydl_opts = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        "writeautomaticsub": True,
        "subtitleslangs": [language],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            subtitles = info.get("subtitles") or {}
            automatic_captions = info.get("automatic_captions") or {}

            track_url = (
                _find_track_url(subtitles, language)
                or _find_track_url(automatic_captions, language)
            )

            if not track_url:
                logger.info(f"No caption track found for language '{language}'")
                return None

            raw_vtt = ydl.urlopen(track_url).read().decode("utf-8", errors="replace")

    except Exception as exc:
        logger.warning(f"Caption fetch failed: {exc}")
        return None

    segments = parse_vtt(raw_vtt)
    if not segments:
        return None

    if start_time is not None or end_time is not None:
        lo = start_time if start_time is not None else 0.0
        hi = end_time if end_time is not None else float("inf")
        segments = [s for s in segments if s["end"] >= lo and s["start"] <= hi]
        if not segments:
            return None

    return segments_to_text(segments), segments
