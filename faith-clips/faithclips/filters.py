"""Cheap first-pass filters, run before anything is sent to Claude.

Claude runs the strict judgment on every clip (Christian only, no politics,
no scandal, official source). These rules just throw out obvious misses for
free, so Claude's 20 daily looks go to real candidates.
"""
import re
from datetime import datetime

from . import config
from .util import parse_duration, parse_rfc3339


def _rx(words: list[str]) -> re.Pattern:
    return re.compile(r"\b(?:" + "|".join(words) + r")\b", re.I)


FAITH = _rx([
    "jesus", "christ", "god", "gods", "god's", "lord", "faith", "scripture", "bible",
    "biblical", "gospel", "pray", "prayer", "praying", "church", "sermon", "pastor",
    "worship", "testimony", "holy spirit", "grace", "salvation", "saved", "baptized",
    "baptism", "blessed", "glory", "amen", "heaven", "cross", "resurrection", "psalm",
    "proverbs", "matthew", "romans", "philippians", "isaiah", "hallelujah", "savior",
    "christian", "ministry", "devotional", "preach", "preaching", "believer", "kingdom",
])

# Title or description: politics, culture war, divisive topics
POLITICS = _rx([
    "trump", "biden", "kamala", "obama", "election", "elections", "democrat", "democrats",
    "republican", "republicans", "gop", "maga", "liberal", "liberals", "leftist",
    "conservatives", "woke", "abortion", "pro-life", "pro-choice", "roe", "lgbt",
    "lgbtq", "transgender", "trans", "gay", "homosexual", "homosexuality", "pride month",
    "immigration", "immigrants", "deport", "deportation", "vaccine", "vaccines",
    "gun control", "second amendment", "critical race", "dei", "congress", "senate",
    "supreme court", "white house", "president", "politics", "political", "culture war",
    "christian nationalism", "antichrist", "end times", "hamas", "gaza", "palestine",
])

# Title only: scandal, drama, attacks, reaction content
DRAMA = _rx([
    "scandal", "allegation", "allegations", "accused", "lawsuit", "sued", "arrested",
    "resigns", "resignation", "fired", "affair", "exposed", "exposing", "controversy",
    "controversial", "heresy", "heretic", "heretical", "false teacher", "false prophet",
    "cult", "reacts", "reaction", "reacting", "debunk", "debunked", "drama", "beef",
    "slams", "rips", "destroys", "rant", "roast", "cancelled",
    "canceled", "apology", "apologizes", "backlash", "under fire",
])

# Title or description: prosperity / money pitches
MONEY = _rx([
    "seed offering", "sow a seed", "sow your seed", "financial breakthrough",
    "send money", "cash app", "cashapp", "prosperity gospel", "money miracle",
    "first fruits offering", "debt cancellation",
])

# Title or description: repost / fake / AI / edited content
FAKE = _rx([
    "compilation", "ai generated", "ai-generated", "ai voice", "lip sync", "lipsync",
    "fan edit", "edit audio", "deepfake", "parody", "satire",
    "no copyright infringement intended", "all rights belong", "credit goes to",
    "rights go to", "fair use", "copyright disclaimer", "i do not own",
])

# Channel names that are usually anonymous repost or AI "message" channels
SPAM_CHANNEL = _rx([
    "clips", "clip", "compilation", "compilations", "edits", "edit", "reposts",
    "motivation", "motivational", "message today", "god says", "jesus says",
    "god's message", "gods message", "message from god", "god is speaking",
    "god wants you", "jesus message", "chosen ones", "chosen one", "fan page",
    "fanpage", "highlights", "daily prayer", "daily bible", "prayers for you",
    "angel", "angels", "universe", "manifest", "tarot", "shorts",
])


def is_faith(text: str) -> bool:
    return bool(FAITH.search(text or ""))


def video_reject_reason(video: dict, since: datetime, trusted: bool = False) -> str | None:
    """Reason to skip this video, or None if it may continue. `trusted` = the
    channel is on your approved list, so repost wording in descriptions (music
    credits etc.) is not held against it."""
    sn = video.get("snippet", {})
    st = video.get("status", {})
    title = sn.get("title", "")
    desc = sn.get("description", "")[:3000]
    tags = " ".join(sn.get("tags", []))

    if sn.get("liveBroadcastContent") in ("live", "upcoming"):
        return "live or upcoming stream"
    if st.get("madeForKids"):
        return "made for kids"
    if st.get("privacyStatus") not in (None, "public"):
        return "not public"
    if parse_rfc3339(sn.get("publishedAt", "1970-01-01T00:00:00Z")) < since:
        return "older than 72 hours"
    lang = (sn.get("defaultAudioLanguage") or sn.get("defaultLanguage") or "en").lower()
    if not lang.startswith("en"):
        return f"not English ({lang})"
    seconds = parse_duration(video.get("contentDetails", {}).get("duration", ""))
    if seconds < config.MIN_VIDEO_SECONDS:
        return "shorter than 15 seconds"
    if not is_faith(f"{title} {desc[:1500]} {tags}"):
        return "no faith words in title/description"
    if m := POLITICS.search(f"{title} {tags}"):
        return f"political/divisive topic ({m.group(0)})"
    if m := DRAMA.search(title):
        return f"drama/scandal/reaction ({m.group(0)})"
    if m := MONEY.search(f"{title} {desc}"):
        return f"money pitch ({m.group(0)})"
    if m := FAKE.search(f"{title} {tags}" if trusted else f"{title} {desc} {tags}"):
        return f"repost/edited/AI signal ({m.group(0)})"
    return None


def channel_reject_reason(channel: dict, now: datetime) -> str | None:
    """Rules for channels the finder discovered on its own (not on your list)."""
    sn = channel.get("snippet", {})
    stats = channel.get("statistics", {})
    title = sn.get("title", "")
    if m := SPAM_CHANNEL.search(title):
        return f"channel name looks like a repost account ({m.group(0)})"
    if stats.get("hiddenSubscriberCount"):
        return "channel hides its subscriber count"
    subs = int(stats.get("subscriberCount", 0) or 0)
    if subs < config.DISCOVERED_MIN_SUBSCRIBERS:
        return f"channel too small ({subs:,} subscribers)"
    if int(stats.get("videoCount", 0) or 0) < config.DISCOVERED_MIN_VIDEOS:
        return "channel has too few videos"
    created = parse_rfc3339(sn.get("publishedAt", "2100-01-01T00:00:00Z"))
    if (now - created).days < config.DISCOVERED_MIN_AGE_DAYS:
        return "channel is less than a year old"
    if m := FAKE.search(sn.get("description", "")):
        return f"channel description looks like a repost account ({m.group(0)})"
    return None
