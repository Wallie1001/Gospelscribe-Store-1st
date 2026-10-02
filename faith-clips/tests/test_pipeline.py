"""A whole morning run against fakes: fake YouTube, fake Sheet, fake feeds, and a
local stand-in for the Anthropic API (so the real SDK request is exercised)."""
import json
import threading
from datetime import timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from faithclips import __main__ as cli
from faithclips import config, emailer, finder
from faithclips.feeds import FeedItem
from faithclips.sheet import CLIP_HEADERS
from faithclips.transcripts import Line, Transcript
from faithclips.util import now_utc

from test_rules import answer


# -- fake Anthropic API ------------------------------------------------------
class FakeAnthropic(BaseHTTPRequestHandler):
    answers: dict = {}
    requests: list = []

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        FakeAnthropic.requests.append({"path": self.path, "headers": dict(self.headers), "body": body})
        prompt = body["messages"][0]["content"]
        vid = next((v for v in self.answers if v in prompt), None)
        data = self.answers.get(vid) or answer(qualifies=False, reject_reason="not relevant")
        if isinstance(data, list):
            data = data.pop(0)
        out = {
            "id": "msg_test", "type": "message", "role": "assistant", "model": body["model"],
            "content": [{"type": "text", "text": json.dumps(data)}],
            "stop_reason": "end_turn", "stop_sequence": None,
            "usage": {"input_tokens": 1200, "output_tokens": 400,
                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0},
        }
        raw = json.dumps(out).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, *a):
        pass


@pytest.fixture
def fake_anthropic(monkeypatch):
    server = HTTPServer(("127.0.0.1", 0), FakeAnthropic)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setenv("ANTHROPIC_BASE_URL", f"http://127.0.0.1:{server.server_port}")
    FakeAnthropic.requests = []
    yield FakeAnthropic
    server.shutdown()


# -- fake YouTube --------------------------------------------------------------
def iso(hours_ago):
    return (now_utc() - timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


def vid(vid_id, title, channel, hours_ago=10, duration="PT30M", desc="", views=80_000):
    return {
        "id": vid_id,
        "snippet": {"title": title, "description": desc, "publishedAt": iso(hours_ago), "channelId": channel,
                    "channelTitle": {"UCapproved": "Grace Church", "UCnew": "Real Faith Sports",
                                     "UCspam": "Jesus Clips Daily"}[channel], "liveBroadcastContent": "none"},
        "contentDetails": {"duration": duration},
        "status": {"privacyStatus": "public", "madeForKids": False},
        "statistics": {"viewCount": str(views), "likeCount": "5000"},
    }


VIDEOS = {
    "sermon00001": vid("sermon00001", "Lord Save Me | Sermon on faith in the storm", "UCapproved"),
    "short000001": vid("short000001", "He gave God the glory after the win", "UCnew", duration="PT42S", hours_ago=5),
    "spam0000001": vid("spam0000001", "Jesus says this to you today", "UCspam", duration="PT50S"),
    "politic0001": vid("politic0001", "Pastor on the election and God", "UCapproved"),
    "oldclip0001": vid("oldclip0001", "Already in the sheet - Jesus", "UCapproved"),
}
CHANNELS = {
    "UCapproved": {"id": "UCapproved", "snippet": {"title": "Grace Church", "publishedAt": "2012-01-01T00:00:00Z", "description": ""},
                   "statistics": {"subscriberCount": "800000", "videoCount": "900"}},
    "UCnew": {"id": "UCnew", "snippet": {"title": "Real Faith Sports", "publishedAt": "2014-01-01T00:00:00Z", "description": ""},
              "statistics": {"subscriberCount": "300000", "videoCount": "1200"}},
    "UCspam": {"id": "UCspam", "snippet": {"title": "Jesus Clips Daily", "publishedAt": "2025-01-01T00:00:00Z", "description": ""},
               "statistics": {"subscriberCount": "90000", "videoCount": "3000"}},
}


class FakeYouTube:
    def __init__(self, key):
        self.units_used = 0

    def channel_by_handle(self, handle):
        self.units_used += 1
        return CHANNELS["UCapproved"] if handle == "@gracechurch" else None

    def resolve_channel(self, name, handle):
        return self.channel_by_handle(handle)

    def recent_uploads(self, cid, since, limit=15):
        self.units_used += 1
        return ["sermon00001", "politic0001", "oldclip0001"] if cid == "UCapproved" else []

    def search_videos(self, q, since, duration=None, max_results=25):
        self.units_used += 100
        return ["short000001", "spam0000001"]

    def videos(self, ids):
        self.units_used += 1
        return [VIDEOS[i] for i in ids if i in VIDEOS]

    def channels(self, ids):
        self.units_used += 1
        return [CHANNELS[i] for i in ids if i in CHANNELS]


# -- fake Sheet ----------------------------------------------------------------
class FakeSheet:
    instance = None

    def __init__(self, *a):
        FakeSheet.instance = self
        self.url = "https://docs.google.com/spreadsheets/d/test"
        self.channel_rows = [{"Name": "Grace Church", "Handle": "@gracechurch", "Type": "pastor", "Approved": "Yes",
                              "Channel ID": "", "_row": 2}]
        self.clips, self.seen, self.log, self.new_channels = [], [], [], []

    def setup(self):
        return []

    def channels(self):
        return self.channel_rows

    def add_channels(self, rows):
        self.new_channels += rows

    def update_channel(self, row, values):
        self.channel_rows[row - 2].update(values)

    def known_video_ids(self):
        return {"oldclip0001"}

    def known_quotes(self):
        return set()

    def add_seen(self, rows):
        self.seen += rows

    def add_clips(self, rows):
        self.clips = rows + self.clips

    def clips_for_date(self, date):
        return [dict(zip(CLIP_HEADERS, r)) for r in self.clips if r[0] == date]

    def log_run(self, row):
        self.log.append(row)

    def runs_on(self, date):
        return [{"Date": r[0], "Run Type": r[2]} for r in self.log if r[0] == date]


def sermon_transcript():
    return Transcript([
        Line(100, 105, "i want to talk about storms today"),
        Line(104, 109, "when peter stepped out of the boat"),
        Line(108, 113, "he was fine until he looked at the wind"),
        Line(112, 117, "and the moment he started sinking"),
        Line(116, 121, "he cried out lord save me"),
        Line(120, 125, "and immediately jesus stretched forth his hand"),
        Line(124, 129, "listen to me"),
        Line(128, 133, "your storm is not the end of your story"),
        Line(132, 137, "the same jesus who caught peter"),
        Line(136, 141, "is reaching for you right now"),
        Line(140, 145, "so stop staring at the waves"),
    ], "manual")


@pytest.fixture
def wired(monkeypatch, fake_anthropic):
    monkeypatch.setattr(finder, "YouTube", FakeYouTube)
    monkeypatch.setattr(finder, "Sheet", FakeSheet)
    monkeypatch.setattr("faithclips.sheet.Sheet", FakeSheet)
    news = FeedItem("Sports Spectrum", "QB gives glory to God", "https://x", now_utc(), ["short000001"])
    monkeypatch.setattr(finder, "fetch_feed", lambda s, u, since: ([news], None) if s == "Sports Spectrum"
                        else ([], f"{s} feed failed (test)"))
    monkeypatch.setattr(finder.TranscriptFetcher, "fetch",
                        lambda self, v: sermon_transcript() if v == "sermon00001" else None)
    sent = []
    monkeypatch.setattr(emailer, "send", lambda *a: sent.append(a))
    fake_anthropic.answers = {
        "sermon00001": answer(),
        "short000001": answer(speaker="Jalen Example", speaker_type="athlete", key_line="",
                              hooks=["He pointed to heaven before anyone else", "Watch what he said first"],
                              piece="He Is Not Here / He Has Risen (Matt 28:6)"),
    }
    settings = cli.Settings("yt", "sk-test", "{}", "sheet", "me@gmail.com", "app pw", "me@gmail.com", "", "", "")
    return settings, sent, fake_anthropic


def test_full_morning_run(wired):
    settings, sent, api = wired
    result = finder.run(settings, "manual")
    sheet = FakeSheet.instance

    # Channel was looked up and its ID saved
    assert sheet.channel_rows[0]["Channel ID"] == "UCapproved"

    # Spam channel, politics and the already-seen video never reached Claude
    prompts = " ".join(r["body"]["messages"][0]["content"] for r in api.requests)
    assert "sermon00001" in prompts and "short000001" in prompts
    assert "spam0000001" not in prompts and "politic0001" not in prompts and "oldclip0001" not in prompts
    assert result.reviewed == 2 == len(api.requests)

    # The real SDK request: model, fallbacks, structured output, beta header
    req = api.requests[0]
    assert req["path"].startswith("/v1/messages")
    assert req["body"]["model"] == config.CLAUDE_MODEL
    assert req["body"]["fallbacks"] == "default"
    assert "server-side-fallback-2026-07-01" in req["headers"].get("anthropic-beta", "")
    assert req["body"]["output_config"]["format"]["type"] == "json_schema"
    assert req["body"]["output_config"]["effort"] == config.CLAUDE_EFFORT
    assert "thinking" not in req["body"]

    # Two clips, best first, with timestamped links and verified quotes
    assert len(sheet.clips) == 2
    top = dict(zip(CLIP_HEADERS, sheet.clips[0]))
    assert top["Speaker"] == "Pastor Jane Doe"
    assert top["Video Link (timestamped)"] == "https://www.youtube.com/watch?v=sermon00001&t=116s"
    assert (top["Start"], top["End"]) == ("1:56", "2:25")
    assert top["Segment Transcript"].startswith("he cried out lord save me")
    assert top["Exact Quote"] == "your storm is not the end of your story"
    assert top["Status"] == "New"
    short = dict(zip(CLIP_HEADERS, sheet.clips[1]))
    assert short["Video Link (timestamped)"].endswith("&t=0s")
    assert "NEW CHANNEL" in short["Notes"] and "No captions" in short["Notes"]

    # Discovered channel added to the Channels tab as New
    assert sheet.new_channels[0][0] == "Real Faith Sports" and sheet.new_channels[0][3] == "New"

    # Run logged, with the broken feeds noted
    assert sheet.log[-1][2] == "manual" and "feed failed" in sheet.log[-1][-1]


def test_rejected_clips_are_remembered(wired):
    settings, sent, api = wired
    api.answers["short000001"] = answer(qualifies=False, reject_reason="vague, no clear faith message")
    finder.run(settings, "manual")
    sheet = FakeSheet.instance
    assert ["short000001", sheet.log[-1][0], "rejected: vague, no clear faith message"] in sheet.seen
    assert len(sheet.clips) == 1


def test_manual_run_emails_top_clips(wired, monkeypatch):
    settings, sent, api = wired
    monkeypatch.delenv("GITHUB_EVENT_NAME", raising=False)
    assert cli.cmd_run(settings) == 0
    assert len(sent) == 1
    subject, html_body = sent[0][3], sent[0][4]
    assert "top 2" in subject and "Pastor Jane Doe" in subject
    assert "watch?v=sermon00001&amp;t=" in html_body and "your storm is not the end of your story" in html_body


def test_scheduled_email_waits_for_search_then_sends_once(wired, monkeypatch):
    settings, sent, api = wired
    monkeypatch.setenv("GITHUB_EVENT_NAME", "schedule")
    from datetime import datetime
    from faithclips.util import PACIFIC
    clock = {"t": datetime(2026, 10, 2, 7, 1, tzinfo=PACIFIC)}
    monkeypatch.setattr(cli, "now_pacific", lambda: clock["t"])
    monkeypatch.setattr(cli, "today_pacific", lambda: "2026-10-02")

    sheet = FakeSheet()
    monkeypatch.setattr("faithclips.sheet.Sheet", lambda *a: sheet)
    assert cli.cmd_email(settings) == 0 and sent == []       # search not done yet: wait
    sheet.log.append(["2026-10-02", "06:05", "daily", 5, 2, 2, 300, "$0.10", ""])
    assert cli.cmd_email(settings) == 0 and len(sent) == 1   # now it sends
    assert cli.cmd_email(settings) == 0 and len(sent) == 1   # and only once


def test_scheduled_search_skips_wrong_hour(wired, monkeypatch):
    settings, sent, api = wired
    monkeypatch.setenv("GITHUB_EVENT_NAME", "schedule")
    from datetime import datetime
    from faithclips.util import PACIFIC
    monkeypatch.setattr(cli, "now_pacific", lambda: datetime(2026, 12, 2, 5, 5, tzinfo=PACIFIC))
    assert cli.cmd_run(settings) == 0
    assert api.requests == []


def test_bad_quote_gets_one_retry_with_the_problem_explained(wired):
    settings, sent, api = wired
    api.answers["sermon00001"] = [answer(key_line="God turns every storm into a stage"), answer()]
    finder.run(settings, "manual")
    sermon_calls = [r for r in api.requests if "sermon00001" in r["body"]["messages"][0]["content"]]
    assert len(sermon_calls) == 2
    retry = sermon_calls[1]["body"]["messages"]
    assert [m["role"] for m in retry] == ["user", "assistant", "user"]
    assert retry[1]["content"][0]["type"] == "text"
    assert "nowhere in the transcript" in retry[2]["content"]
    top = dict(zip(CLIP_HEADERS, FakeSheet.instance.clips[0]))
    assert top["Exact Quote"] == "your storm is not the end of your story"


def test_invented_quote_twice_is_thrown_out(wired):
    settings, sent, api = wired
    api.answers["sermon00001"] = [answer(key_line="made up line"), answer(key_line="still made up")]
    finder.run(settings, "manual")
    sheet = FakeSheet.instance
    assert all(r[-1] != "sermon00001" for r in sheet.clips)
    assert any(r[0] == "sermon00001" and "nowhere in the transcript" in r[2] for r in sheet.seen)
