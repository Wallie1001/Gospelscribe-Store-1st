"""Every setting you might want to change lives in this file.

Edit it right on github.com (pencil icon), commit, and the next run uses it.
"""

# ---------------------------------------------------------------------------
# Claude
# ---------------------------------------------------------------------------
# Latest Claude model (checked Oct 2026). Swap to "claude-sonnet-5-5" to cut
# the Claude bill roughly in half.
CLAUDE_MODEL = "claude-opus-5-5"
CLAUDE_EFFORT = "medium"  # low | medium | high

# ---------------------------------------------------------------------------
# Daily limits (these keep costs low)
# ---------------------------------------------------------------------------
LOOKBACK_HOURS = 72          # only videos posted in the last 72 hours
MAX_CLAUDE_CALLS = 20        # Claude looks at the top 20 candidates per day
MAX_TRANSCRIPT_TRIES = 40    # transcript fetches are free, but slow
CLIPS_PER_DAY = 10           # rows added to the Sheet each day
EMAIL_TOP = 5                # clips in the morning email

# Clip length rules (seconds)
MIN_VIDEO_SECONDS = 15       # anything shorter is skipped
SHORT_MAX_SECONDS = 60       # 15-60s videos are used as-is
MOMENT_MIN_SECONDS = 20      # longer videos: pick a 20-45s moment
MOMENT_MAX_SECONDS = 45
MOMENT_HARD_MAX_SECONDS = 60

# ---------------------------------------------------------------------------
# Schedule guards (GitHub's clock is UTC, so we check Pacific time ourselves)
# ---------------------------------------------------------------------------
TIMEZONE = "America/Los_Angeles"
FINDER_EARLIEST = (5, 45)    # scheduled finder runs at/after 5:45 AM Pacific
EMAIL_AT = (7, 0)            # email goes out at/after 7:00 AM Pacific
EMAIL_EARLIEST = (6, 45)     # the 7 AM job may start a little early
EMAIL_WAIT_UNTIL = (9, 0)    # if the finder is late, email waits until 9 AM

# ---------------------------------------------------------------------------
# New channels found automatically must look like a real, established source
# ---------------------------------------------------------------------------
DISCOVERED_MIN_SUBSCRIBERS = 20_000
DISCOVERED_MIN_AGE_DAYS = 365
DISCOVERED_MIN_VIDEOS = 25

# ---------------------------------------------------------------------------
# YouTube discovery searches (each search costs 100 of the 10,000 free daily
# units). "short" = Shorts-length results only, None = any length.
# ---------------------------------------------------------------------------
DISCOVERY_SEARCHES = [
    # pastors / preachers
    ("powerful sermon jesus hope", None),
    ("sermon perseverance faith god", None),
    ("sermon purpose god plan", None),
    ("sermon grace of god", None),
    ("pastor encouragement jesus", "short"),
    ("preacher faith motivation jesus", "short"),
    # athletes / celebrities
    ("postgame interview glory to god", None),
    ("thank you jesus postgame interview", "short"),
    ("athlete gives glory to god", None),
    ("athlete baptized jesus", None),
    ("award speech thank god jesus", None),
    ("athlete testimony jesus christ", None),
    ("celebrity testimony jesus faith", None),
    # creators / influencers
    ("christian testimony jesus changed my life", "short"),
    ("jesus faith message", "short"),
    ("bible verse encouragement jesus", "short"),
]

# Searches made from news headlines (athlete/celebrity faith stories)
MAX_FEED_SEARCHES = 5

# ---------------------------------------------------------------------------
# Faith news RSS feeds. Each site lists backup addresses; the first one that
# works is used. A broken feed is noted in the Log tab and skipped.
# ---------------------------------------------------------------------------
FEEDS = {
    "Sports Spectrum": [
        "https://sportsspectrum.com/feed/",
    ],
    "CBN News": [
        "https://www2.cbn.com/rss-cbn-news-all",
        "https://www2.cbn.com/rss/news",
        "https://www.cbn.com/cbnnews/us/feed/",
    ],
    "Christian Post": [
        "https://www.christianpost.com/rss",
        "https://www.christianpost.com/category/sports/rss",
    ],
    "ChurchLeaders": [
        "https://churchleaders.com/feed",
    ],
}

# Headlines must mention faith AND an athlete/celebrity-type word to trigger a
# YouTube search for the original video.
FEED_PEOPLE_WORDS = [
    "nfl", "nba", "mlb", "nhl", "wnba", "ufc", "olympic", "olympian", "coach",
    "quarterback", "pitcher", "player", "athlete", "champion", "championship",
    "super bowl", "world series", "playoff", "golfer", "pga", "tennis", "boxer",
    "fighter", "soccer", "college football", "actor", "actress", "singer",
    "rapper", "star", "grammy", "oscar", "emmy", "dove award", "celebrity",
    "influencer", "artist", "musician", "host",
]

# ---------------------------------------------------------------------------
# Your pieces (Claude picks the best fit for each clip)
# ---------------------------------------------------------------------------
PIECES = {
    "Lord Save Me (Matt 14:30)":
        "Peter sinking in the storm cries 'Lord, save me' and Jesus catches him. "
        "Fear, storms, sinking, crying out, rescue, doubt turned to faith.",
    "It Is Written (Matt 4:4)":
        "Jesus in the wilderness: 'Man shall not live by bread alone, but by every word "
        "that proceedeth out of the mouth of God.' Temptation, discipline, the Word, "
        "spiritual warfare, standing firm.",
    "Go and Make Disciples (Matt 28:19)":
        "The Great Commission: 'Go ye therefore, and teach all nations.' Mission, purpose, "
        "boldness, sharing your faith, calling.",
    "A Savior Is Born (Matt 1-2)":
        "Emmanuel, God with us (Matt 1:23). Hope, new beginnings, God showing up, "
        "the gift of Jesus, worship.",
    "He Is Not Here / He Has Risen (Matt 28:6)":
        "The empty tomb: 'He is not here: for he is risen.' Resurrection, comebacks, "
        "victory, death defeated, second chances, new life.",
    "Book of Matthew pants":
        "The whole Book of Matthew. Use when the clip is about the Gospel or the life of "
        "Jesus broadly and no single verse fits better.",
}

CAPTION_SIGNOFF = "Book of Matthew collection, link in bio"
DEFAULT_HASHTAGS = ["#Jesus", "#Faith", "#ChristianTikTok", "#BookOfMatthew", "#Gospelscribe"]

BRAND = "Gospelscribe"
BRAND_SITE = "gospelscribe.com"
