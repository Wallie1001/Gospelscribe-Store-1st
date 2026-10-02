"""Caption text for a video (text only; the video itself is never downloaded)."""
import html
import logging
import re
from dataclasses import dataclass

from youtube_transcript_api import (
    CouldNotRetrieveTranscript,
    IpBlocked,
    RequestBlocked,
    YouTubeTranscriptApi,
)
from youtube_transcript_api.proxies import GenericProxyConfig, WebshareProxyConfig

log = logging.getLogger(__name__)
LANGS = ["en", "en-US", "en-GB", "en-CA", "en-AU"]
_NOISE = re.compile(r"\[(?:music|applause|laughter|cheering|inaudible|__)\]|>>", re.I)


@dataclass
class Line:
    start: float
    end: float
    text: str


@dataclass
class Transcript:
    lines: list[Line]
    kind: str  # "manual" or "auto"

    def lines_between(self, start: float, end: float) -> list[Line]:
        """Caption lines that START inside [start, end). Auto-captions overlap in
        time, so we go by start time only (half a second of slack)."""
        return [l for l in self.lines if start - 0.5 <= l.start < end]

    def text_between(self, start: float, end: float) -> str:
        return " ".join(l.text for l in self.lines_between(start, end)).strip()

    def line_end(self, line: Line) -> float:
        """When a line really ends: the next line's start (captions overlap)."""
        i = self.lines.index(line)
        return min(line.end, self.lines[i + 1].start) if i + 1 < len(self.lines) else line.end

    def full_text(self) -> str:
        return " ".join(l.text for l in self.lines)


class TranscriptsBlocked(Exception):
    """YouTube is refusing transcript requests from this server's IP."""


class TranscriptFetcher:
    def __init__(self, proxy_url: str = "", webshare_user: str = "", webshare_pass: str = ""):
        proxy = None
        if webshare_user and webshare_pass:
            proxy = WebshareProxyConfig(proxy_username=webshare_user, proxy_password=webshare_pass)
        elif proxy_url:
            proxy = GenericProxyConfig(http_url=proxy_url, https_url=proxy_url)
        self.api = YouTubeTranscriptApi(proxy_config=proxy)
        self.blocked_count = 0

    def fetch(self, video_id: str) -> Transcript | None:
        try:
            listing = self.api.list(video_id)
            try:
                t, kind = listing.find_manually_created_transcript(LANGS), "manual"
            except CouldNotRetrieveTranscript:
                t, kind = listing.find_generated_transcript(LANGS), "auto"
            fetched = t.fetch()
        except (RequestBlocked, IpBlocked) as e:
            self.blocked_count += 1
            raise TranscriptsBlocked(str(e).splitlines()[0] if str(e) else "blocked") from e
        except CouldNotRetrieveTranscript as e:
            log.info("no transcript for %s: %s", video_id, type(e).__name__)
            return None
        except Exception as e:  # network hiccups etc.
            log.warning("transcript error for %s: %s", video_id, e)
            return None

        lines = []
        for s in fetched:
            text = _NOISE.sub(" ", html.unescape(s.text.replace("\n", " ")))
            text = " ".join(text.split())
            if text:
                lines.append(Line(start=float(s.start), end=float(s.start) + float(s.duration), text=text))
        return Transcript(lines=lines, kind=kind) if lines else None


def for_prompt(t: Transcript, group_seconds: float = 10.0) -> str:
    """Compact timestamped transcript for Claude: one line per ~10 seconds."""
    out, buf, buf_start = [], [], None
    for line in t.lines:
        if buf_start is None:
            buf_start = line.start
        buf.append(line.text)
        if line.end - buf_start >= group_seconds:
            out.append(f"[{buf_start:.0f}s] {' '.join(buf)}")
            buf, buf_start = [], None
    if buf:
        out.append(f"[{buf_start:.0f}s] {' '.join(buf)}")
    return "\n".join(out)
