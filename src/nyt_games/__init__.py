"""Asynchronous Python client for NYT Games."""

from nyt_games.exceptions import (
    NYTGamesAuthenticationError,
    NYTGamesConnectionError,
    NYTGamesError,
    NYTGamesParseError,
)
from nyt_games.models import (
    BeeFriendsStats,
    Connections,
    ConnectionsFriendsStats,
    ConnectionsStats,
    CrosswordStatsAndStreaks,
    CrosswordStatsInfo,
    FriendStats,
    LatestDataStats,
    MidiFriendsStats,
    MiniFriendsStats,
    SpellingBee,
    SpellingBeeRanks,
    Strands,
    StrandsStats,
    Wordle,
    WordleFriendsStats,
    WordleStats,
)
from nyt_games.nyt_games import NYTGamesClient

__all__ = [
    "BeeFriendsStats",
    "Connections",
    "ConnectionsFriendsStats",
    "ConnectionsStats",
    "CrosswordStatsAndStreaks",
    "CrosswordStatsInfo",
    "FriendStats",
    "LatestDataStats",
    "MidiFriendsStats",
    "MiniFriendsStats",
    "NYTGamesAuthenticationError",
    "NYTGamesClient",
    "NYTGamesConnectionError",
    "NYTGamesError",
    "NYTGamesParseError",
    "SpellingBee",
    "SpellingBeeRanks",
    "Strands",
    "StrandsStats",
    "Wordle",
    "WordleFriendsStats",
    "WordleStats",
]
