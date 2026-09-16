import re
import time
import random
import logging
from typing import Optional, Callable, TypeVar

from groq import Groq, RateLimitError
from app.core.config import settings

logger = logging.getLogger(__name__)

_client: Optional[Groq] = None
T = TypeVar("T")

RETRY_AFTER_RE = re.compile(r"try again in ([\d.]+)s", re.IGNORECASE)


def get_groq_client() -> Groq:
    global _client
    if _client is None:
        if not settings.GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Get a free key at https://console.groq.com"
            )
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client


def with_rate_limit_retry(fn: Callable[[], T], max_retries: int = 4) -> T:
    """Retry a Groq call on 429 rate-limit errors with backoff. Groq's
    tokens-per-minute quota is shared across ALL calls to a given model
    (topic segmentation, section generation, overview, translate, chat all
    compete for the same small per-minute budget on a free/on-demand tier),
    so transient 429s from concurrent calls are expected and recoverable
    within the same minute -- worth retrying rather than failing the job."""
    last_exc: Optional[Exception] = None

    for attempt in range(max_retries):
        try:
            return fn()
        except RateLimitError as exc:
            last_exc = exc
            match = RETRY_AFTER_RE.search(str(exc))
            delay = float(match.group(1)) + 1 if match else (2 ** attempt) * 2
            delay = min(delay, 60) + random.uniform(0, 1)
            logger.warning(
                f"Groq rate limit hit (attempt {attempt + 1}/{max_retries}), "
                f"retrying in {delay:.1f}s"
            )
            time.sleep(delay)

    raise last_exc
