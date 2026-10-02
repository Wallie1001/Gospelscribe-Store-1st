"""The daily run: find candidates, filter, let Claude review the best 20, keep the top 10."""
import logging
from dataclasses import dataclass, field
from datetime import timedelta

import anthropic

from . import config
from .channels import STARTER_CHANNELS
from .claude import Candidate, ClaudeReviewer, Clip, Rejected
from .feeds import fetch_feed, is_people_faith_story, search_query_from_headline
from .filters import channel_reject_reason, video_reject_reason
from .scoring import final_score, prescore
from .sheet import CLIP_HEADERS, Sheet
from .transcripts import TranscriptFetcher, TranscriptsBlocked
from .util import fmt_ts, normalize, now_pacific, now_utc, parse_duration, parse_rfc3339, watch_url
from .youtube import QuotaExceeded, YouTube

log = logging.getLogger(__name__)

FATAL_CLAUDE_ERRORS = (anthropic.AuthenticationError, anthropic.PermissionDeniedError, anthropic.NotFoundError)


@dataclass
class RunResult:
    date: str
    clips: list[dict] = field(default_factory=list)   # rows as {header: value}
    candidates: int = 0
    reviewed: int = 0
    notes: list[str] = field(default_factory=list)


def is_active(row: dict) -> bool:
    return row.get("Approved", "").strip().lower() in ("yes", "new", "y")


def is_blocked(row: dict) -> bool:
    return row.get("Approved", "").strip().lower() in ("no", "n")


def sync_channels(sheet: Sheet, yt: YouTube, today: str, notes: list[str]) -> list[dict]:
    """Fill the Channels tab on the first run; look up IDs for rows that lack one."""
    rows = sheet.channels()
    if not rows:
        sheet.add_channels([[n, h, t, "Yes", "", "", "", "", "starter list", today] for n, h, t in STARTER_CHANNELS])
        rows = sheet.channels()

    for r in rows:
        if r.get("Channel ID") or is_blocked(r) or not (r.get("Name") or r.get("Handle")):
            continue
        not_found_before = r.get("YouTube Title", "").startswith("NOT FOUND")
        try:
            if not_found_before:  # only the cheap handle lookup on later days
                chan = yt.channel_by_handle(r.get("Handle", "")) if r.get("Handle") else None
            else:
                chan = yt.resolve_channel(r.get("Name", ""), r.get("Handle", ""))
        except QuotaExceeded:
            notes.append("YouTube quota ran out while looking up channels")
            break
        if chan:
            cid = chan["id"]
            values = {
                "Channel ID": cid,
                "YouTube Title": chan["snippet"]["title"],
                "Subscribers": int(chan.get("statistics", {}).get("subscriberCount", 0) or 0),
                "Link": f"https://www.youtube.com/channel/{cid}",
            }
            if not r.get("Approved"):
                values["Approved"] = "Yes"
            sheet.update_channel(r["_row"], values)
            r.update(values)
        elif not not_found_before:
            sheet.update_channel(r["_row"], {"YouTube Title": "NOT FOUND: fix the Handle (e.g. @name)"})
            notes.append(f"Channel not found: {r.get('Name') or r.get('Handle')}")
    return rows


def collect(yt: YouTube, rows: list[dict], since, notes: list[str]) -> dict[str, str]:
    """Video ID -> where it was found."""
    origins: dict[str, str] = {}

    def add(ids, origin):
        for vid in ids:
            origins.setdefault(vid, origin)

    try:
        for r in rows:
            if is_active(r) and r.get("Channel ID"):
                add(yt.recent_uploads(r["Channel ID"], since), "your channel list")
        for query, duration in config.DISCOVERY_SEARCHES:
            add(yt.search_videos(query, since, duration), f"YouTube search: {query}")
    except QuotaExceeded:
        notes.append("YouTube daily quota ran out during search (results so far were still used)")
        return origins

    feed_searches = 0
    for source, urls in config.FEEDS.items():
        items, error = fetch_feed(source, urls, since)
        if error:
            notes.append(error)
        for item in items:
            if item.youtube_ids:
                add(item.youtube_ids, f"{source} story: {item.title}")
            elif is_people_faith_story(item) and feed_searches < config.MAX_FEED_SEARCHES:
                feed_searches += 1
                try:
                    found = yt.search_videos(search_query_from_headline(item.title), since, max_results=5)
                except QuotaExceeded:
                    notes.append("YouTube quota ran out during news searches")
                    return origins
                add(found, f"{source} story: {item.title}")
    return origins


def build_candidates(yt: YouTube, origins: dict[str, str], rows: list[dict], known: set[str],
                     since, now) -> tuple[list[Candidate], dict[str, int]]:
    rows_by_id = {r["Channel ID"]: r for r in rows if r.get("Channel ID")}
    ids = [v for v in origins if v not in known]
    videos = yt.videos(ids) if ids else []
    chan_ids = sorted({v["snippet"]["channelId"] for v in videos})
    chans = {c["id"]: c for c in yt.channels(chan_ids)} if chan_ids else {}

    reasons: dict[str, int] = {}
    out = []
    for v in videos:
        sn, stats = v["snippet"], v.get("statistics", {})
        cid = sn["channelId"]
        row = rows_by_id.get(cid)
        ch = chans.get(cid, {})
        if row and is_blocked(row):
            reason = "channel switched off in your Channels tab"
        else:
            reason = video_reject_reason(v, since, trusted=bool(row))
            if not reason and not row:
                reason = channel_reject_reason(ch, now) if ch else "channel info missing"
        if reason:
            key = reason.split(" (")[0]
            reasons[key] = reasons.get(key, 0) + 1
            continue
        subs = int(ch.get("statistics", {}).get("subscriberCount", 0) or 0)
        hours = max(0.0, (now - parse_rfc3339(sn["publishedAt"])).total_seconds() / 3600)
        views = int(stats.get("viewCount", 0) or 0)
        c = Candidate(
            video_id=v["id"],
            title=sn.get("title", ""),
            description=sn.get("description", ""),
            channel_id=cid,
            channel_title=sn.get("channelTitle", ""),
            channel_subscribers=subs,
            published_at=sn["publishedAt"],
            duration=parse_duration(v["contentDetails"]["duration"]),
            views=views,
            likes=int(stats.get("likeCount", 0) or 0),
            origin=origins[v["id"]],
            approved=(row or {}).get("Approved", ""),
            channel_type=(row or {}).get("Type", ""),
            hours_old=hours,
        )
        c.prescore = prescore(hours, subs, views, approved=bool(row))
        out.append(c)
    out.sort(key=lambda c: c.prescore, reverse=True)
    return out, reasons


def clip_row(clip: Clip, date: str) -> list:
    c = clip.candidate
    hooks = clip.hooks + [""] * (3 - len(clip.hooks))
    return [
        date, clip.speaker, clip.speaker_type, c.channel_title, watch_url(c.video_id, clip.start),
        fmt_ts(clip.start), fmt_ts(clip.end), clip.key_line, clip.segment_text, clip.score,
        hooks[0], hooks[1], hooks[2], clip.caption, clip.piece, clip.how_to_use,
        clip.permission_message, "New", " ".join(clip.notes), c.title, c.video_id,
    ]


def run(settings, run_type: str) -> RunResult:
    now = now_utc()
    today = now_pacific().strftime("%Y-%m-%d")
    since = now - timedelta(hours=config.LOOKBACK_HOURS)
    result = RunResult(date=today)
    notes = result.notes

    sheet = Sheet(settings.google_service_account_json, settings.sheet_id)
    sheet.setup()
    yt = YouTube(settings.youtube_api_key)

    rows = sync_channels(sheet, yt, today, notes)
    origins = collect(yt, rows, since, notes)
    known = sheet.known_video_ids()
    known_quotes = sheet.known_quotes()
    candidates, reasons = build_candidates(yt, origins, rows, known, since, now)
    result.candidates = len(candidates)
    log.info("found %d new videos, %d passed the free filters", len([o for o in origins if o not in known]), len(candidates))
    if reasons:
        log.info("skipped: %s", ", ".join(f"{k}: {n}" for k, n in sorted(reasons.items(), key=lambda x: -x[1])))

    reviewer = ClaudeReviewer(settings.anthropic_api_key)
    fetcher = TranscriptFetcher(settings.transcript_proxy_url, settings.webshare_user, settings.webshare_pass)
    clips: list[Clip] = []
    seen: list[list] = []
    tries, blocked, api_errors = 0, False, 0

    for c in candidates:
        if result.reviewed >= config.MAX_CLAUDE_CALLS:
            break
        long_video = c.duration > config.SHORT_MAX_SECONDS
        if not blocked and tries < config.MAX_TRANSCRIPT_TRIES:
            tries += 1
            try:
                c.transcript = fetcher.fetch(c.video_id)
            except TranscriptsBlocked as e:
                if fetcher.blocked_count >= 3:
                    blocked = True
                    notes.append(f"YouTube blocked transcript requests ({e}); long sermons were skipped. "
                                 "See README: 'Transcripts blocked'.")
        if long_video and not c.transcript:
            continue  # can't pick a moment without words; may work another day

        result.reviewed += 1
        try:
            clip = reviewer.review(c)
        except Rejected as e:
            seen.append([c.video_id, today, f"rejected: {e}"])
            continue
        except FATAL_CLAUDE_ERRORS:
            raise
        except anthropic.APIError as e:
            api_errors += 1
            log.warning("Claude error on %s: %s", c.video_id, e)
            if api_errors >= 3:
                notes.append(f"Claude API kept failing ({type(e).__name__}); stopped early")
                break
            continue

        if clip.key_line and normalize(clip.key_line) in known_quotes:
            seen.append([c.video_id, today, "duplicate of a quote already in the sheet"])
            continue
        clip.score = final_score(clip.emotional_punch, clip.stands_alone, c.hours_old,
                                 c.channel_subscribers, has_transcript=c.transcript is not None)
        clips.append(clip)
        if clip.key_line:
            known_quotes.add(normalize(clip.key_line))

    clips.sort(key=lambda x: x.score, reverse=True)
    keep, rest = clips[: config.CLIPS_PER_DAY], clips[config.CLIPS_PER_DAY:]
    seen += [[x.candidate.video_id, today, f"passed (score {x.score}) but not in today's top 10"] for x in rest]

    # Channels the finder discovered on its own: add them, labeled, so you can switch them off.
    listed = {r.get("Channel ID") for r in rows}
    new_channel_rows = []
    for clip in keep:
        c = clip.candidate
        if c.channel_id not in listed:
            listed.add(c.channel_id)
            new_channel_rows.append([
                c.channel_title, "", clip.speaker_type, "New", c.channel_id, c.channel_title,
                c.channel_subscribers, f"https://www.youtube.com/channel/{c.channel_id}",
                "found automatically", today,
            ])
        if not c.approved:
            clip.notes.insert(0, "NEW CHANNEL: found automatically and added to your Channels tab as New. "
                                 "Type No there to block it, Yes to keep it.")
        elif c.approved.strip().lower() == "new":
            clip.notes.insert(0, "Channel found automatically (still marked New in the Channels tab).")

    rows_out = [clip_row(x, today) for x in keep]
    sheet.add_clips(rows_out)
    sheet.add_seen(seen)
    sheet.add_channels(new_channel_rows)
    result.clips = [dict(zip(CLIP_HEADERS, r)) for r in rows_out]
    for r in result.clips:
        r["Score"] = str(r["Score"])

    sheet.log_run([
        today, now_pacific().strftime("%H:%M"), run_type, result.candidates, result.reviewed,
        len(keep), yt.units_used, f"${reviewer.cost_estimate():.2f}", " | ".join(notes),
    ])
    log.info("added %d clips (YouTube units %d, Claude ~$%.2f)", len(keep), yt.units_used, reviewer.cost_estimate())
    return result
