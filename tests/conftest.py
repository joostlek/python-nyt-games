"""Asynchronous Python client for NYT Games."""

from collections.abc import AsyncGenerator, Generator

import aiohttp
from aioresponses import aioresponses
import pytest

from nyt_games.nyt_games import NYTGamesClient
from syrupy import SnapshotAssertion

from .syrupy import NYTGamesSnapshotExtension


@pytest.fixture(name="snapshot")
def snapshot_assertion(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture with the NYT Games extension."""
    return snapshot.use_extension(NYTGamesSnapshotExtension)


@pytest.fixture
async def client() -> AsyncGenerator[NYTGamesClient, None]:
    """Return a NYT Games client."""
    async with (
        aiohttp.ClientSession() as session,
        NYTGamesClient(
            "token",
            session=session,
        ) as nyt_games_client,
    ):
        yield nyt_games_client


@pytest.fixture(name="responses")
def aioresponses_fixture() -> Generator[aioresponses, None, None]:
    """Return aioresponses fixture."""
    with aioresponses() as mocked_responses:
        yield mocked_responses
