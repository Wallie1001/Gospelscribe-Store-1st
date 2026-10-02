"""YouTube Data API v3 (official API, read-only, API key)."""
import logging
from datetime import datetime

import requests

from .util import normalize

log = logging.getLogger(__name__)
API = "https://www.googleapis.com/youtube/v3/"

# Quota cost per call (https://developers.google.com/youtube/v3/determine_quota_cost)
COST = {"search": 100, "videos": 1, "channels": 1, "playlistItems": 1}


class QuotaExceeded(Exception):
    pass


class YouTubeError(Exception):
    pass


class YouTube:
    def __init__(self, api_key: str, session: requests.Session | None = None):
        self.key = api_key
        self.http = session or requests.Session()
        self.units_used = 0

    def _get(self, endpoint: str, **params) -> dict:
        params = {k: v for k, v in params.items() if v is not None}
        params["key"] = self.key
        r = self.http.get(API + endpoint, params=params, timeout=30)
        self.units_used += COST.get(endpoint, 1)
        if r.status_code == 200:
            return r.json()
        try:
            err = r.json().get("error", {})
            reason = (err.get("errors") or [{}])[0].get("reason", "")
            message = err.get("message", r.text[:200])
        except ValueError:
            reason, message = "", r.text[:200]
        if reason in ("quotaExceeded", "dailyLimitExceeded", "rateLimitExceeded"):
            raise QuotaExceeded(message)
        if r.status_code == 404 or reason in ("playlistNotFound", "channelNotFound"):
            return {"items": []}
        raise YouTubeError(f"{endpoint} {r.status_code} {reason}: {message}")

    # -- channels -----------------------------------------------------------
    def channels(self, ids: list[str]) -> list[dict]:
        out = []
        for i in range(0, len(ids), 50):
            data = self._get(
                "channels",
                part="snippet,statistics,contentDetails",
                id=",".join(ids[i:i + 50]),
                maxResults=50,
            )
            out.extend(data.get("items", []))
        return out

    def channel_by_handle(self, handle: str) -> dict | None:
        handle = handle.strip()
        if not handle:
            return None
        if not handle.startswith("@"):
            handle = "@" + handle
        data = self._get("channels", part="snippet,statistics,contentDetails", forHandle=handle)
        items = data.get("items", [])
        return items[0] if items else None

    def find_channel(self, name: str) -> dict | None:
        """Search channels by name (100 units) and pick the biggest close match."""
        data = self._get("search", part="snippet", q=name, type="channel", maxResults=5)
        ids = [it["id"]["channelId"] for it in data.get("items", []) if it.get("id", {}).get("channelId")]
        if not ids:
            return None
        chans = [c for c in self.channels(ids) if names_match(name, c["snippet"]["title"])]
        if not chans:
            return None
        return max(chans, key=lambda c: int(c.get("statistics", {}).get("subscriberCount", 0) or 0))

    def resolve_channel(self, name: str, handle: str) -> dict | None:
        if handle:
            chan = self.channel_by_handle(handle)
            if chan and (not name or names_match(name, chan["snippet"]["title"], handle)):
                return chan
        if name:
            return self.find_channel(name)
        return None

    # -- videos -------------------------------------------------------------
    def recent_uploads(self, channel_id: str, since: datetime, limit: int = 15) -> list[str]:
        """Newest uploads from a channel's uploads playlist (1 unit)."""
        if not channel_id.startswith("UC"):
            return []
        data = self._get(
            "playlistItems",
            part="contentDetails",
            playlistId="UU" + channel_id[2:],
            maxResults=limit,
        )
        ids = []
        for it in data.get("items", []):
            cd = it.get("contentDetails", {})
            published = cd.get("videoPublishedAt")
            if published and datetime.fromisoformat(published.replace("Z", "+00:00")) >= since:
                ids.append(cd["videoId"])
        return ids

    def search_videos(self, query: str, since: datetime, duration: str | None = None,
                      max_results: int = 25) -> list[str]:
        """Keyword search for recent videos (100 units)."""
        data = self._get(
            "search",
            part="id",
            q=query,
            type="video",
            order="relevance",
            publishedAfter=since.strftime("%Y-%m-%dT%H:%M:%SZ"),
            relevanceLanguage="en",
            regionCode="US",
            safeSearch="strict",
            videoDuration=duration,
            maxResults=max_results,
        )
        return [it["id"]["videoId"] for it in data.get("items", []) if it.get("id", {}).get("videoId")]

    def videos(self, ids: list[str]) -> list[dict]:
        out = []
        for i in range(0, len(ids), 50):
            data = self._get(
                "videos",
                part="snippet,contentDetails,statistics,status",
                id=",".join(ids[i:i + 50]),
                maxResults=50,
            )
            out.extend(data.get("items", []))
        return out


_STOP = {"the", "and", "church", "ministries", "ministry", "official", "channel", "with", "tv"}


def names_match(name: str, title: str, handle: str = "") -> bool:
    """Loose check that a found channel is the one we meant."""
    a = {w for w in normalize(name).split() if len(w) >= 3 and w not in _STOP}
    b = set(normalize(title).split())
    if a & b:
        return True
    squashed_title = normalize(title).replace(" ", "")
    squashed_handle = normalize(handle).replace(" ", "")
    return any(w in squashed_title or (squashed_handle and w in squashed_handle) for w in a)
