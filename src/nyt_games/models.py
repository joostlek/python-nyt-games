"""Models for NYT Games."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date  # noqa: TCH003
from typing import Any

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass
class LatestData(DataClassORJSONMixin):
    """LatestData model."""

    player: LatestDataPlayer


@dataclass
class LatestDataPlayer(DataClassORJSONMixin):
    """LatestData model."""

    stats: LatestDataStats
    user_id: int


@dataclass
class LatestDataStats(DataClassORJSONMixin):
    """LatestData model."""

    wordle: Wordle


@dataclass
class Wordle(DataClassORJSONMixin):
    """Wordle model."""

    games_played: int = field(metadata=field_options(alias="gamesPlayed"))
    games_won: int = field(metadata=field_options(alias="gamesWon"))
    guesses: dict[str, int]
    current_streak: int = field(metadata=field_options(alias="currentStreak"))
    max_streak: int = field(metadata=field_options(alias="maxStreak"))
    last_won: date = field(metadata=field_options(alias="lastWonPrintDate"))
    last_completed: date = field(metadata=field_options(alias="lastCompletedPrintDate"))

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """Pre deserialization hook."""
        return d["calculatedStats"]
