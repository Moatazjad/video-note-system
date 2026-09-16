import re
from typing import List, Dict

_TIMING_RE = re.compile(
    r"(\d{1,2}:)?(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(\d{1,2}:)?(\d{2}):(\d{2})\.(\d{3})"
)
_TAG_RE = re.compile(r"<[^>]*>")


def _parse_timestamp(hours: str, minutes: str, seconds: str, millis: str) -> float:
    h = int(hours[:-1]) if hours else 0
    m = int(minutes)
    s = int(seconds)
    ms = int(millis)
    return h * 3600 + m * 60 + s + ms / 1000.0


def _clean_text(raw_lines: List[str]) -> str:
    text = " ".join(raw_lines)
    text = _TAG_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


MAX_OVERLAP_WORDS = 20


def _remove_overlap(prev_words: List[str], words: List[str]) -> List[str]:
    """Return only the words in `words` that don't overlap with the tail of
    `prev_words`. YouTube auto-captions are "rolling": consecutive cues
    commonly overlap either as a growing prefix (new cue = old cue + a few
    more words) OR as a sliding window (new cue drops some leading words
    and adds new trailing ones, so its start overlaps the old cue's END,
    not its full text) -- a real, observed pattern, not just the simpler
    growing-prefix case. Checking every possible overlap length (longest
    first) against a suffix-of-prev/prefix-of-new match handles both."""
    if not prev_words or not words:
        return words

    max_overlap = min(len(prev_words), len(words), MAX_OVERLAP_WORDS)
    for overlap_len in range(max_overlap, 0, -1):
        if [w.lower() for w in prev_words[-overlap_len:]] == [w.lower() for w in words[:overlap_len]]:
            return words[overlap_len:]

    return words


def parse_vtt(raw_text: str) -> List[Dict]:
    """Parse WEBVTT content into a list of {start, end, text} segments,
    with each cue's text reduced to only the words that don't overlap with
    the previous cue -- collapses YouTube's rolling/duplicated auto-caption
    cues regardless of whether the overlap is a growing prefix or a
    sliding window."""
    lines = raw_text.splitlines()
    segments: List[Dict] = []
    prev_words: List[str] = []

    i = 0
    n = len(lines)

    while i < n:
        line = lines[i].strip()
        match = _TIMING_RE.search(line)

        if not match:
            i += 1
            continue

        start = _parse_timestamp(match.group(1), match.group(2), match.group(3), match.group(4))
        end = _parse_timestamp(match.group(5), match.group(6), match.group(7), match.group(8))

        i += 1
        text_lines = []
        while i < n and lines[i].strip():
            text_lines.append(lines[i])
            i += 1

        text = _clean_text(text_lines)
        if not text:
            continue

        words = text.split()
        new_words = _remove_overlap(prev_words, words)
        prev_words = words

        if new_words:
            segments.append({"start": start, "end": end, "text": " ".join(new_words)})

    return segments


def segments_to_text(segments: List[Dict]) -> str:
    return " ".join(seg["text"] for seg in segments if seg["text"])
