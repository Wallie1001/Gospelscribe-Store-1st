"""Faith news RSS feeds: catch athlete/celebrity faith moments, then find the
original official video on YouTube."""
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

import feedparser
import requests

from . import config
from .filters import POLITICS, is_faith

log = logging.getLogger(__name__)
UA = "Mozilla/5.0 (compatible; GospelscribeFaithClips/1.0; +https://gospelscribe.com)"
YT_ID = re.compile(r"(?:youtube\.com/(?:watch\?(?:[^\"'\s<>]*&)?v=|embed/|shorts/|live/)|youtu\.be/)([A-Za-z0-9_-]{11})")
PEOPLE = re.compile(r"\b(?:" + "|".join(re.escape(w) for w in config.FEED_PEOPLE_WORDS) + r")\b", re.I)


@dataclass
class FeedItem:
    source: str
    title: str
    link: str
    published: datetime
    youtube_ids: list[str] = field(default_factory=list)


def _published(entry) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            return datetime(*t[:6], tzinfo=timezone.utc)
    return None


def fetch_feed(source: str, urls: list[str], since: datetime) -> tuple[list[FeedItem], str | None]:
    """Items newer than `since` from the first working URL, plus an error note."""
    last_error = None
    for url in urls:
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
            r.raise_for_status()
            parsed = feedparser.parse(r.content)
            if not parsed.entries:
                last_error = f"{url}: no entries"
                continue
        except Exception as e:
            last_error = f"{url}: {e}"
            continue

        items = []
        for e in parsed.entries:
            when = _published(e)
            if not when or when < since:
                continue
            blob = " ".join(
                [e.get("link", ""), e.get("summary", "")]
                + [c.get("value", "") for c in e.get("content", [])]
            )
            ids = list(dict.fromkeys(YT_ID.findall(blob)))
            items.append(FeedItem(source, e.get("title", "").strip(), e.get("link", ""), when, ids))
        return items, None
    return [], f"{source} feed failed ({last_error})"


def is_people_faith_story(item: FeedItem) -> bool:
    """Athlete/celebrity faith moment, not politics."""
    return bool(is_faith(item.title) and PEOPLE.search(item.title) and not POLITICS.search(item.title))


def search_query_from_headline(title: str) -> str:
    """Trim a headline into a YouTube search: keep names and key words."""
    title = re.sub(r"[‘’“”\"':|,!?().]", " ", title)
    drop = {"the", "a", "an", "of", "to", "in", "on", "for", "and", "after", "his", "her",
            "their", "is", "was", "says", "said", "shares", "reveals", "how", "why", "who",
            "with", "about", "at", "as", "be", "it", "that", "this", "from", "by"}
    words = [w for w in title.split() if w.lower() not in drop]
    return " ".join(words[:9])
