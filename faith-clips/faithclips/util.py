import math
import re
import unicodedata
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from . import config

PACIFIC = ZoneInfo(config.TIMEZONE)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def now_pacific() -> datetime:
    return now_utc().astimezone(PACIFIC)


def today_pacific() -> str:
    return now_pacific().strftime("%Y-%m-%d")


def at_or_after(now: datetime, hm: tuple[int, int]) -> bool:
    return (now.hour, now.minute) >= hm


def parse_rfc3339(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


_DURATION_RE = re.compile(
    r"P(?:(?P<d>\d+)D)?(?:T(?:(?P<h>\d+)H)?(?:(?P<m>\d+)M)?(?:(?P<s>\d+)S)?)?$"
)


def parse_duration(iso: str) -> int:
    """YouTube's ISO 8601 duration ("PT1H2M3S") to seconds."""
    m = _DURATION_RE.match(iso or "")
    if not m:
        return 0
    d, h, mi, s = (int(m.group(k) or 0) for k in ("d", "h", "m", "s"))
    return ((d * 24 + h) * 60 + mi) * 60 + s


def fmt_ts(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def watch_url(video_id: str, start: float = 0) -> str:
    return f"https://www.youtube.com/watch?v={video_id}&t={int(start)}s"


def normalize(text: str) -> str:
    """Lowercase, strip accents/punctuation, collapse spaces. Used to check that a
    quote really appears in a transcript, ignoring caption punctuation."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower().replace("’", "'").replace("‘", "'")
    text = text.replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def word_count(text: str) -> int:
    return len((text or "").split())


_EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F900-\U0001F9FF⬀-⯿️‍]"
)


def strip_emoji(text: str) -> str:
    return _EMOJI_RE.sub("", text or "").strip()


def has_emoji(text: str) -> bool:
    return bool(_EMOJI_RE.search(text or ""))


def log_scale(value: float, top: float) -> float:
    """0..1 on a log scale where `top` maps to 1."""
    if value <= 1:
        return 0.0
    return min(1.0, math.log10(value) / math.log10(top))
