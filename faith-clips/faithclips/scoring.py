"""Ranking.

prescore: free, from YouTube numbers. Decides which candidates Claude sees.
final score (0-100): emotional punch 35%, stands alone in 30s 30%,
reach 20%, recency 15%.
"""
from . import config
from .util import log_scale


def recency(hours_old: float) -> float:
    return max(0.0, 1.0 - hours_old / config.LOOKBACK_HOURS)


def reach(subscribers: int) -> float:
    return log_scale(subscribers, 10_000_000)  # 10M subscribers = full marks


def prescore(hours_old: float, subscribers: int, views: int, approved: bool) -> float:
    views_per_hour = views / max(hours_old, 1.0)
    momentum = log_scale(views_per_hour, 10_000)  # 10k views/hour = full marks
    trust = 1.0 if approved else 0.5
    return 0.30 * recency(hours_old) + 0.25 * reach(subscribers) + 0.25 * momentum + 0.20 * trust


def final_score(punch: int, stands_alone: int, hours_old: float, subscribers: int,
                has_transcript: bool) -> float:
    s = 100 * (
        0.35 * punch / 10
        + 0.30 * stands_alone / 10
        + 0.20 * reach(subscribers)
        + 0.15 * recency(hours_old)
    )
    if not has_transcript:
        s -= 10  # words can't be verified yet
    return round(max(0.0, s), 1)
