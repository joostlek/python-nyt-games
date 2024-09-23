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
    spelling_bee: SpellingBee


@dataclass
class Wordle(DataClassORJSONMixin):
    """Wordle model."""

    games_played: int = field(metadata=field_options(alias="gamesPlayed"))
    games_won: int = field(metadata=field_options(alias="gamesWon"))
    guesses: dict[str, int]
    current_streak: int = field(metadata=field_options(alias="currentStreak"))
    max_streak: int = field(metadata=field_options(alias="maxStreak"))
    last_won: date = field(metadata=field_options(alias="lastWonPrintDate"))

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """Pre deserialization hook."""
        return d["calculatedStats"]


@dataclass
class SpellingBee(DataClassORJSONMixin):
    """SpellingBee mode."""

    puzzles_started: int
    total_words: int
    total_pangrams: int
    ranks: SpellingBeeRanks


@dataclass
class SpellingBeeRanks(DataClassORJSONMixin):
    """SpellingBeeRanks mode."""

    beginner: int = field(metadata=field_options(alias="Beginner"))
    good: int = field(metadata=field_options(alias="Good"))
    good_start: int = field(metadata=field_options(alias="Good Start"))
    moving_up: int = field(metadata=field_options(alias="Moving Up"))
    nice: int = field(metadata=field_options(alias="Nice"))
    solid: int = field(metadata=field_options(alias="Solid"))
