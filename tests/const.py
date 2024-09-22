"""Constants for tests."""

from importlib import metadata

MOCK_URL = "https://nytimes.com"
version = metadata.version("nyt_games")

HEADERS = {
    "User-Agent": f"PythonNYTGames/{version}",
    "Accept": "application/json",
}
