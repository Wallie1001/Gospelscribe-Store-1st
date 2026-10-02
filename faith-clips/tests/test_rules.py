from datetime import datetime, timedelta, timezone

import pytest

from faithclips import config
from faithclips.claude import Candidate, FixableProblem, Rejected, snap_segment, validate
from faithclips.feeds import YT_ID, search_query_from_headline
from faithclips.filters import channel_reject_reason, video_reject_reason
from faithclips.scoring import final_score, prescore
from faithclips.transcripts import Line, Transcript, for_prompt
from faithclips.util import fmt_ts, normalize, parse_duration, watch_url
from faithclips.youtube import names_match

NOW = datetime(2026, 10, 2, 14, 0, tzinfo=timezone.utc)
SINCE = NOW - timedelta(hours=72)


def transcript():
    words = [
        "good morning church", "i want to talk about storms today",
        "when peter stepped out of the boat", "he was fine until he looked at the wind",
        "and the moment he started sinking", "he cried out lord save me",
        "and immediately jesus stretched forth his hand", "listen to me",
        "your storm is not the end of your story", "the same jesus who caught peter",
        "is reaching for you right now", "so stop staring at the waves",
        "and start looking at the one who walks on them", "let's pray",
    ]
    # auto-captions overlap: each line lasts 5s but the next starts after 4s
    return Transcript([Line(100 + i * 4, 105 + i * 4, w) for i, w in enumerate(words)], "auto")


def cand(duration=1800, t=None):
    return Candidate(
        video_id="abcdefghijk", title="Lord Save Me | Pastor Jane", description="", channel_id="UC1",
        channel_title="Grace Church", channel_subscribers=250_000, published_at="2026-10-01T12:00:00Z",
        duration=duration, views=50_000, likes=3_000, origin="your channel list", approved="Yes",
        hours_old=26, transcript=t,
    )


def answer(**over):
    d = {
        "qualifies": True, "reject_reason": "", "speaker": "Pastor Jane Doe", "speaker_type": "pastor",
        "official_source": True, "segment_start_seconds": 116, "segment_end_seconds": 150,
        "key_line": "your storm is not the end of your story", "emotional_punch": 9, "stands_alone": 8,
        "hooks": ["When you feel like you're sinking, watch this",
                  "\"your storm is not the end of your story\"",
                  "Peter's 3-word prayer still works"],
        "caption_lines": ["Pastor Jane Doe on the night Peter sank. 🌊", "🎥 Pastor Jane Doe, Grace Church on YouTube"],
        "hashtags": ["#Jesus", "Faith", "#LordSaveMe", "#Matthew14", "#ChristianTikTok"],
        "piece": "Lord Save Me (Matt 14:30)", "how_to_use": "Ask permission first.",
        "permission_message": "Hi Grace Church! ... Bryant, Gospelscribe (gospelscribe.com)",
    }
    d.update(over)
    return d


# -- util -------------------------------------------------------------------
def test_duration_and_links():
    assert parse_duration("PT1H2M3S") == 3723
    assert parse_duration("PT45S") == 45
    assert parse_duration("P0D") == 0
    assert fmt_ts(3723) == "1:02:03" and fmt_ts(75) == "1:15"
    assert watch_url("abcdefghijk", 123.9) == "https://www.youtube.com/watch?v=abcdefghijk&t=123s"


def test_normalize_ignores_caption_punctuation():
    assert normalize("Lord, SAVE me!") == normalize("lord save me")
    assert normalize("don’t quit") == normalize("dont quit")


# -- quote / moment verification ---------------------------------------------
def test_valid_long_clip():
    clip = validate(cand(t=transcript()), answer())
    assert clip.start == 116 and 15 <= clip.end - clip.start <= 60
    assert "your storm is not the end of your story" in clip.segment_text
    assert clip.segment_text.startswith("and the moment he started sinking")
    assert len(clip.hooks) == 3
    assert clip.caption.splitlines()[-2] == config.CAPTION_SIGNOFF
    assert len(clip.caption.splitlines()[-1].split()) == 5
    assert all(t.startswith("#") for t in clip.caption.splitlines()[-1].split())
    assert any("Auto-captions" in n for n in clip.notes)


def test_invented_quote_is_never_accepted():
    with pytest.raises(FixableProblem, match="nowhere in the transcript"):
        validate(cand(t=transcript()), answer(key_line="God will make your storm your stage"))


def test_quote_outside_segment_is_flagged():
    with pytest.raises(FixableProblem, match="not inside your segment"):
        validate(cand(t=transcript()), answer(key_line="good morning church"))


def test_hook_with_fake_quote_is_dropped():
    clip = validate(cand(t=transcript()), answer(hooks=[
        "\"God never fails\" he said",            # not in transcript -> dropped
        "Watch this if you're sinking #faith 🙏",  # hashtag and emoji stripped
        "This one line will wreck you in the best way possible today friends",  # 13 words -> dropped
        "Gospelscribe presents: Lord save me",     # brand mention -> dropped
    ]))
    assert clip.hooks == ["Watch this if you're sinking"]


def test_all_hooks_bad_asks_for_fix():
    with pytest.raises(FixableProblem):
        validate(cand(t=transcript()), answer(hooks=["\"made up words here\""]))


def test_segment_too_long_asks_for_fix():
    with pytest.raises(FixableProblem, match="seconds long"):
        validate(cand(t=transcript()), answer(segment_start_seconds=116, segment_end_seconds=121))


def test_rejections():
    with pytest.raises(Rejected):
        validate(cand(t=transcript()), answer(qualifies=False, reject_reason="political"))
    with pytest.raises(Rejected, match="official"):
        validate(cand(t=transcript()), answer(official_source=False))
    with pytest.raises(Rejected, match="without a transcript"):
        validate(cand(t=None), answer())


def test_short_without_captions_is_flagged_not_quoted():
    clip = validate(cand(duration=40, t=None), answer(key_line="anything", hooks=[
        "\"I give all the glory to God\"", "He pointed straight up after the win"]))
    assert clip.start == 0 and clip.end == 40
    assert clip.key_line == ""
    assert clip.hooks == ["He pointed straight up after the win"]
    assert any("No captions" in n for n in clip.notes)


def test_snap_and_prompt_format():
    t = transcript()
    assert snap_segment(t, 117.3, 149.0) == (116.0, 152.0)
    assert for_prompt(t).startswith("[100s] good morning church")


# -- filters -----------------------------------------------------------------
def video(title="Lord Save Me | Sermon on faith", desc="", duration="PT35M", published="2026-10-01T12:00:00Z", **sn):
    return {
        "id": "abcdefghijk",
        "snippet": {"title": title, "description": desc, "publishedAt": published,
                    "channelId": "UC1", "channelTitle": "Grace Church", "liveBroadcastContent": "none", **sn},
        "contentDetails": {"duration": duration},
        "status": {"privacyStatus": "public", "madeForKids": False},
        "statistics": {"viewCount": "1000"},
    }


@pytest.mark.parametrize("v,expect", [
    (video(), None),
    (video(title="Pastor reacts to Trump speech about God"), "political"),
    (video(title="Megachurch pastor scandal: what the Bible says"), "drama"),
    (video(desc="Sow a seed of $58 today for your financial breakthrough. God bless"), "money"),
    (video(desc="Jesus sermon. No copyright infringement intended."), "repost"),
    (video(title="Morning vibes", desc="coffee"), "no faith words"),
    (video(duration="PT9S"), "shorter"),
    (video(published="2026-09-20T12:00:00Z"), "older"),
    (video(liveBroadcastContent="live"), "live"),
    (video(defaultAudioLanguage="es"), "not English"),
])
def test_video_filter(v, expect):
    reason = video_reject_reason(v, SINCE)
    assert (reason is None) if expect is None else (expect in reason)


def test_trusted_channel_music_credit_is_ok():
    v = video(desc="Jesus sermon. Music credit goes to our worship team.")
    assert video_reject_reason(v, SINCE, trusted=True) is None
    assert "repost" in video_reject_reason(v, SINCE, trusted=False)


def chan(title="Grace Church", subs=250_000, videos=400, created="2015-01-01T00:00:00Z", desc=""):
    return {"snippet": {"title": title, "publishedAt": created, "description": desc},
            "statistics": {"subscriberCount": str(subs), "videoCount": str(videos)}}


@pytest.mark.parametrize("c,expect", [
    (chan(), None),
    (chan(title="Jesus Christ Clips"), "repost"),
    (chan(title="God's Message Today"), "repost"),
    (chan(title="Christian Motivation"), "repost"),
    (chan(subs=900), "too small"),
    (chan(created="2026-06-01T00:00:00Z"), "less than a year"),
])
def test_discovered_channel_filter(c, expect):
    reason = channel_reject_reason(c, NOW)
    assert (reason is None) if expect is None else (expect in reason)


# -- feeds, matching, scoring ------------------------------------------------
def test_youtube_ids_from_feed_html():
    html = ('<iframe src="https://www.youtube.com/embed/AbC_def-123"></iframe> '
            '<a href="https://youtu.be/ZZZZZZZZZZZ">x</a> https://www.youtube.com/watch?v=YYYYYYYYYYY&t=4s '
            'https://www.youtube.com/shorts/XXXXXXXXXXX')
    assert YT_ID.findall(html) == ["AbC_def-123", "ZZZZZZZZZZZ", "YYYYYYYYYYY", "XXXXXXXXXXX"]


def test_headline_to_query():
    q = search_query_from_headline("Chiefs QB gives glory to God after Super Bowl win: 'Jesus is everything'")
    assert "glory" in q and "Super" in q and "after" not in q.split()


def test_names_match():
    assert names_match("Elevation Church (Steven Furtick)", "Elevation Church")
    assert names_match("Life.Church (Craig Groeschel)", "Life.Church")
    assert not names_match("Max Lucado", "Random Gaming Channel")


def test_scores_rank_sensibly():
    fresh_big = prescore(5, 2_000_000, 200_000, approved=True)
    old_small = prescore(70, 30_000, 2_000, approved=False)
    assert fresh_big > old_small
    assert final_score(9, 9, 10, 1_000_000, True) > final_score(5, 5, 60, 30_000, True)
    assert final_score(9, 9, 10, 1_000_000, False) == final_score(9, 9, 10, 1_000_000, True) - 10
