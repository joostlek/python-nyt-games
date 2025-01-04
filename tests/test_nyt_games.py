"""Tests for the client."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import aiohttp
from aiohttp import ClientError
from aiohttp.hdrs import METH_GET
from aioresponses import CallbackResult, aioresponses
import pytest

from nyt_games import NYTGamesClient, NYTGamesConnectionError, NYTGamesError
from nyt_games.exceptions import NYTGamesAuthenticationError
from tests import load_fixture
from tests.const import HEADERS, MOCK_URL

if TYPE_CHECKING:
    from syrupy import SnapshotAssertion


async def test_putting_in_own_session(
    responses: aioresponses,
) -> None:
    """Test putting in own session."""
    responses.get(
        f"{MOCK_URL}/svc/games/state/wordleV2/latests",
        status=200,
        body=load_fixture("latest.json"),
    )
    async with aiohttp.ClientSession() as session:
        client = NYTGamesClient(session=session, token="abc")
        await client.get_latest_stats()
        assert client.session is not None
        assert not client.session.closed
        await client.close()
        assert not client.session.closed


async def test_creating_own_session(
    responses: aioresponses,
) -> None:
    """Test creating own session."""
    responses.get(
        f"{MOCK_URL}/svc/games/state/wordleV2/latests",
        status=200,
        body=load_fixture("latest.json"),
    )
    client = NYTGamesClient(token="abc")
    await client.get_latest_stats()
    assert client.session is not None
    assert not client.session.closed
    await client.close()
    assert client.session.closed


async def test_unexpected_server_response(
    responses: aioresponses,
    client: NYTGamesClient,
) -> None:
    """Test handling unexpected response."""
    responses.get(
        f"{MOCK_URL}/svc/games/state/wordleV2/latests",
        status=404,
        headers={"Content-Type": "plain/text"},
        body="Yes",
    )
    with pytest.raises(NYTGamesError):
        await client.get_latest_stats()


async def test_unauthorized(
    responses: aioresponses,
    client: NYTGamesClient,
) -> None:
    """Test handling unauthorized response."""
    responses.get(
        f"{MOCK_URL}/svc/games/state/wordleV2/latests",
        status=403,
        body='{"error": "forbidden"}',
    )
    with pytest.raises(NYTGamesAuthenticationError):
        await client.get_latest_stats()


async def test_timeout(
    responses: aioresponses,
) -> None:
    """Test request timeout."""

    # Faking a timeout by sleeping
    async def response_handler(_: str, **_kwargs: Any) -> CallbackResult:
        """Response handler for this test."""
        await asyncio.sleep(2)
        return CallbackResult(body="Goodmorning!")

    responses.get(
        f"{MOCK_URL}/svc/games/state/wordleV2/latests",
        callback=response_handler,
    )
    async with NYTGamesClient(request_timeout=1, token="abc") as client:
        with pytest.raises(NYTGamesConnectionError):
            await client.get_latest_stats()


async def test_client_error(
    client: NYTGamesClient,
    responses: aioresponses,
) -> None:
    """Test client error."""

    async def response_handler(_: str, **_kwargs: Any) -> CallbackResult:
        """Response handler for this test."""
        raise ClientError

    responses.get(
        f"{MOCK_URL}/measures/current",
        callback=response_handler,
    )
    with pytest.raises(NYTGamesConnectionError):
        await client.get_latest_stats()


@pytest.mark.parametrize(
    "fixture", ["latest.json", "new_account.json", "no_spelling_bee.json"]
)
async def test_get_latest(
    responses: aioresponses,
    client: NYTGamesClient,
    snapshot: SnapshotAssertion,
    fixture: str,
) -> None:
    """Test status call."""
    responses.get(
        f"{MOCK_URL}/svc/games/state/wordleV2/latests",
        status=200,
        body=load_fixture(fixture),
    )
    assert await client.get_latest_stats() == snapshot
    responses.assert_called_once_with(
        f"{MOCK_URL}/svc/games/state/wordleV2/latests",
        METH_GET,
        headers=HEADERS,
        params=None,
    )


async def test_get_connections(
    responses: aioresponses,
    client: NYTGamesClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving connections."""
    responses.get(
        f"{MOCK_URL}/svc/games/state/connections/latests?puzzle_ids=0",
        status=200,
        body=load_fixture("connections.json"),
    )
    assert await client.get_connections() == snapshot
    responses.assert_called_once_with(
        f"{MOCK_URL}/svc/games/state/connections/latests",
        METH_GET,
        headers=HEADERS,
        params={"puzzle_ids": "0"},
    )


@pytest.mark.parametrize(
    "fixture", ["new_account_connections.json", "newer_account_connections.json"]
)
async def test_get_connections_new_player(
    responses: aioresponses, client: NYTGamesClient, fixture: str
) -> None:
    """Test retrieving connections."""
    responses.get(
        f"{MOCK_URL}/svc/games/state/connections/latests?puzzle_ids=0",
        status=200,
        body=load_fixture(fixture),
    )
    assert await client.get_connections() is None
    responses.assert_called_once_with(
        f"{MOCK_URL}/svc/games/state/connections/latests",
        METH_GET,
        headers=HEADERS,
        params={"puzzle_ids": "0"},
    )


async def test_get_user_id(
    responses: aioresponses,
    client: NYTGamesClient,
) -> None:
    """Test retrieving user_id."""
    responses.get(
        f"{MOCK_URL}/svc/games/state/wordleV2/latests",
        status=200,
        body=load_fixture("latest.json"),
    )
    assert await client.get_user_id() == 218886794


@pytest.mark.parametrize(
    "fixture",
    [
        "crossword_stats_existing_player.json",
        "crossword_stats_new_player.json",
    ],
)
async def test_crossword_stats(
    responses: aioresponses,
    client: NYTGamesClient,
    snapshot: SnapshotAssertion,
    fixture: str,
) -> None:
    """Test fetching crossword stats."""
    fixture_text = load_fixture(fixture)
    url = f"{MOCK_URL}/svc/crosswords/v3/10781499/stats-and-streaks.json"
    responses.get(
        f"{url}?date_start=1988-01-01&start_on_monday=true",
        body=fixture_text,
    )

    stats = await client.get_crossword_stats()

    assert stats == snapshot
