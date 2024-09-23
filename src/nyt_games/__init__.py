"""Asynchronous Python client for NYT Games."""

from nyt_games.exceptions import (
    NYTGamesAuthenticationError,
    NYTGamesConnectionError,
    NYTGamesError,
    NYTGamesParseError,
)
from nyt_games.models import (
    Connections,
    ConnectionsStats,
    LatestDataStats,
    SpellingBee,
    SpellingBeeRanks,
    Wordle,
    WordleStats,
)
from nyt_games.nyt_games import NYTGamesClient

__all__ = [
    "NYTGamesClient",
    "NYTGamesError",
    "NYTGamesConnectionError",
    "NYTGamesAuthenticationError",
    "NYTGamesParseError",
    "LatestDataStats",
    "Connections",
    "SpellingBee",
    "SpellingBeeRanks",
    "WordleStats",
    "ConnectionsStats",
    "Wordle",
]
