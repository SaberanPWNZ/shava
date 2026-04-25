"""Level configuration and pure helpers.

Levels are derived from the cumulative point balance. The mapping is
intentionally kept in a small, easy-to-tune list so that designers can
re-balance the game without touching code paths.

Index of the threshold == level. ``LEVEL_TITLES[i]`` is the title for
level ``i``. The threshold at index ``i`` is the *minimum* points
required to be at level ``i``.
"""

from __future__ import annotations

from typing import NamedTuple

LEVEL_THRESHOLDS: list[int] = [0, 50, 150, 400, 1000, 2500]
LEVEL_TITLES: list[str] = [
    "Newbie",
    "Foodie",
    "Critic",
    "Expert",
    "Master",
    "Legend",
]


class LevelInfo(NamedTuple):
    level: int
    title: str
    next_threshold: int | None
    progress_pct: int


def level_for(points: int) -> LevelInfo:
    """Return the level information for a given number of points.

    ``next_threshold`` is ``None`` when the user has reached the last
    configured level. ``progress_pct`` is an integer in ``[0, 100]``
    representing how far the user is between the current and the next
    threshold (``100`` when there is no next level).
    """

    points = max(0, int(points))
    level = 0
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if points >= threshold:
            level = i
        else:
            break

    title = LEVEL_TITLES[level]

    if level + 1 < len(LEVEL_THRESHOLDS):
        current = LEVEL_THRESHOLDS[level]
        nxt = LEVEL_THRESHOLDS[level + 1]
        span = max(1, nxt - current)
        progress = int(((points - current) / span) * 100)
        progress = max(0, min(100, progress))
        return LevelInfo(level=level, title=title, next_threshold=nxt, progress_pct=progress)

    return LevelInfo(level=level, title=title, next_threshold=None, progress_pct=100)
