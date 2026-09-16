import json
import math
import re
import time
import logging
from typing import List, Dict, Tuple

from app.services.groq_client import get_groq_client, with_rate_limit_retry
from app.utils.templates import get_section_template, get_overview_template

logger = logging.getLogger(__name__)

MODEL = "openai/gpt-oss-120b"
COARSE_CHUNK_SECONDS = 20
VALID_TEMPLATES = {"educational", "business", "research"}

# This Groq account tier shares a small tokens-per-minute (TPM) budget
# ACROSS every call to this model (topic segmentation, section generation,
# overview, translate, chat all compete for the same pool). Two things
# follow: (1) never fire concurrent calls for one video -- parallel calls
# stack their token usage within the same rolling window and trip the
# limit even when each call alone would fit; (2) cap the input sent to any
# single call, since a single oversized prompt (e.g. a long video's full
# transcript, or Arabic text which tokenizes to more tokens per character
# than English) can exceed the ENTIRE per-minute budget by itself, which a
# retry cannot fix -- only a smaller request can.
MAX_TOPIC_INPUT_CHARS = 4000
MAX_SECTION_EXCERPT_CHARS = 3000
SEQUENTIAL_CALL_DELAY_SECONDS = 1.5

_REPEATED_CHAR_RE = re.compile(r"(.)\1{9,}")


def collapse_repetition(text: str) -> str:
    """Safety net against LLM repetition-loop failures (e.g. degenerating on
    repetitive input like onomatopoeia): cap any run of 10+ identical
    characters down to 5, well below what any legitimate text would use."""
    return _REPEATED_CHAR_RE.sub(lambda m: m.group(1) * 5, text)


def _format_seconds(seconds: float) -> str:
    total = int(seconds)
    minutes, sec = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{sec:02d}"
    return f"{minutes:02d}:{sec:02d}"


def _coarsen_segments(segments: List[Dict], chunk_seconds: float = COARSE_CHUNK_SECONDS) -> List[Dict]:
    """Merge fine-grained segments into ~chunk_seconds buckets for a compact,
    LLM-friendly timestamped transcript."""
    if not segments:
        return []

    coarse = []
    bucket_start = segments[0]["start"]
    bucket_end = segments[0]["end"]
    bucket_texts = []

    for seg in segments:
        if seg["start"] - bucket_start >= chunk_seconds and bucket_texts:
            coarse.append({"start": bucket_start, "end": bucket_end, "text": " ".join(bucket_texts)})
            bucket_start = seg["start"]
            bucket_texts = []

        bucket_texts.append(seg["text"])
        bucket_end = seg["end"]

    if bucket_texts:
        coarse.append({"start": bucket_start, "end": bucket_end, "text": " ".join(bucket_texts)})

    return coarse


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + " …"


def _transcript_with_markers(coarse_segments: List[Dict], max_chars: int = MAX_TOPIC_INPUT_CHARS) -> str:
    full = "\n".join(
        f"[{_format_seconds(seg['start'])}] {seg['text']}" for seg in coarse_segments
    )
    return _truncate(full, max_chars)


def _slice_transcript(
    segments: List[Dict], start: float, end: float, max_chars: int = MAX_SECTION_EXCERPT_CHARS
) -> str:
    texts = [seg["text"] for seg in segments if seg["start"] < end and seg["end"] > start]
    return _truncate(" ".join(texts), max_chars)


def _strip_json_fence(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _deterministic_sections(duration: float, part_seconds: float = 900) -> Tuple[str, List[Dict]]:
    n_parts = max(1, math.ceil(duration / part_seconds))
    boundaries = [i * duration / n_parts for i in range(n_parts + 1)]
    return "Video Notes", [
        {"title": f"Part {i + 1}", "start": boundaries[i], "end": boundaries[i + 1]}
        for i in range(n_parts)
    ]


def _segment_topics(segments: List[Dict], duration: float) -> Tuple[str, List[Dict]]:
    coarse = _coarsen_segments(segments)
    transcript_text = _transcript_with_markers(coarse)

    system_prompt = (
        "You segment a timestamped video transcript into coherent topic "
        'sections. Respond with ONLY a JSON object: {"video_title": string, '
        '"sections": [{"title": string, "start": number, "end": number}, ...]}. '
        "Sections must be contiguous, non-overlapping, and cover the "
        "transcript from its first to its last timestamp. Every start/end "
        "MUST be one of the timestamps (in seconds) already present in the "
        "transcript below -- never invent a timestamp. Prefer real semantic "
        "topic boundaries over fixed-length slices. No prose, no markdown "
        "fences, JSON only."
    )

    client = get_groq_client()
    sections = None
    video_title = "Video Notes"

    for attempt in range(2):
        try:
            resp = with_rate_limit_retry(lambda: client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": transcript_text},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=1024,
            ))
            content = _strip_json_fence(resp.choices[0].message.content or "")
            data = json.loads(content)

            if isinstance(data, dict):
                raw_sections = data.get("sections")
                video_title = data.get("video_title") or video_title
            else:
                raw_sections = data

            if isinstance(raw_sections, list) and raw_sections:
                sections = raw_sections
                break
        except Exception as exc:
            logger.warning(f"Topic segmentation attempt {attempt + 1} failed: {exc}")

    if not sections:
        logger.warning("Topic segmentation failed after retries; using equal-split fallback")
        return _deterministic_sections(duration)

    cleaned = []
    for s in sections:
        try:
            start = max(0.0, float(s["start"]))
            end = min(duration, float(s["end"]))
            title = str(s.get("title") or "Section").strip()
        except (KeyError, TypeError, ValueError):
            continue
        if end > start:
            cleaned.append({"title": title, "start": start, "end": end})

    if not cleaned:
        return _deterministic_sections(duration)

    cleaned.sort(key=lambda s: s["start"])
    cleaned[-1]["end"] = max(cleaned[-1]["end"], duration)

    return video_title, cleaned


def _generate_section(section: Dict, segments: List[Dict], template_type: str, language: str) -> str:
    client = get_groq_client()
    instructions = get_section_template(template_type, language)
    section_text = _slice_transcript(segments, section["start"], section["end"]) or section["title"]

    prompt = f"{instructions}\n\nTranscript excerpt:\n{section_text}"

    response = with_rate_limit_retry(lambda: client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an elite technical note generator producing one "
                    "section of a larger structured note document. Output only "
                    "the section's Markdown body -- no top-level title."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.6,
        frequency_penalty=0.4,
        max_tokens=900,
    ))

    body = response.choices[0].message.content
    if not body or not body.strip():
        raise RuntimeError(f"Empty response from LLM for section '{section['title']}'")
    return collapse_repetition(body.strip())


def _generate_overview(video_title: str, sections: List[Dict], language: str) -> str:
    client = get_groq_client()
    instructions = get_overview_template(language)
    titles_list = "\n".join(f"- {s['title']}" for s in sections)
    prompt = f"{instructions}\n\nVideo title: {video_title}\nSection titles:\n{titles_list}"

    try:
        response = with_rate_limit_retry(lambda: client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You write concise video overviews."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            frequency_penalty=0.4,
            max_tokens=400,
        ))
        content = response.choices[0].message.content
        return collapse_repetition(content.strip()) if content else ""
    except Exception as exc:
        logger.warning(f"Overview generation failed, skipping: {exc}")
        return ""


def _assemble(
    video_title: str,
    overview: str,
    sections: List[Dict],
    section_bodies: List[str],
    language: str,
) -> str:
    toc_label = "الفهرس" if language == "ar" else "Table of Contents"
    overview_label = "نظرة عامة" if language == "ar" else "Overview"

    lines = [f"# {video_title}", ""]

    if overview:
        lines += [f"## {overview_label}", overview, ""]

    lines.append(f"## {toc_label}")
    for s in sections:
        lines.append(f"- {s['title']} ({_format_seconds(s['start'])}–{_format_seconds(s['end'])})")
    lines.append("")

    for s, body in zip(sections, section_bodies):
        lines.append(f"## {s['title']}")
        lines.append(f"*{_format_seconds(s['start'])}–{_format_seconds(s['end'])}*")
        lines.append("")
        lines.append(body)
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def translate_notes(content: str, target_language: str) -> str:
    client = get_groq_client()
    lang_name = "Arabic" if target_language == "ar" else "English"

    system_prompt = (
        f"Translate the following Markdown document into natural, fluent "
        f"{lang_name}. Preserve the Markdown structure (headings, bullet "
        "points, bold) exactly. Output only the translated Markdown, no "
        "commentary."
    )

    response = with_rate_limit_retry(lambda: client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
        temperature=0.3,
        frequency_penalty=0.4,
        max_tokens=4096,
    ))

    translated = response.choices[0].message.content
    if not translated or not translated.strip():
        raise RuntimeError("Empty response from translation model")
    return collapse_repetition(translated.strip())


class NoteService:
    @staticmethod
    def generate_structured_notes(
        segments: List[Dict],
        template_type: str,
        language: str,
        duration: float,
    ) -> Tuple[str, List[Dict]]:
        if not segments:
            raise ValueError("No transcript segments to generate notes from")

        if template_type not in VALID_TEMPLATES:
            raise ValueError(
                f"Invalid template_type: {template_type}. "
                f"Must be one of: {', '.join(VALID_TEMPLATES)}"
            )

        video_title, sections = _segment_topics(segments, duration)

        # Sequential, not concurrent: this Groq tier's tokens-per-minute
        # budget is shared across all calls to this model, so parallel
        # section calls would stack their usage within the same window and
        # trip the rate limit even when each call alone fits comfortably.
        section_bodies: List[str] = []
        for i, section in enumerate(sections):
            section_bodies.append(_generate_section(section, segments, template_type, language))
            if i < len(sections) - 1:
                time.sleep(SEQUENTIAL_CALL_DELAY_SECONDS)

        overview = _generate_overview(video_title, sections, language)
        markdown = _assemble(video_title, overview, sections, section_bodies, language)

        return markdown, sections
