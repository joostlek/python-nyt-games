"""Asynchronous Python client for NYT Games."""

from __future__ import annotations

import asyncio
import base64
from dataclasses import dataclass
import datetime as dt
from importlib import metadata
import json
from pathlib import Path
import socket
from typing import TYPE_CHECKING

from aiohttp import ClientError, ClientResponseError, ClientSession
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from yarl import URL

from .exceptions import NYTGamesAuthenticationError, NYTGamesConnectionError
from .models import (
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
    Strands,
    StrandsStats,
    WordleFriendsStats,
    WordleStats,
)

if TYPE_CHECKING:
    from typing import Self


VERSION = metadata.version(__package__)


@dataclass
class NYTGamesClient:
    """Main class for handling connections with NYT Games."""

    token: str
    session: ClientSession | None = None
    request_timeout: int = 10
    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        host: str,
        headers: dict[str, str],
        params: dict[str, str] | None = None,
    ) -> str:
        """Handle a request to NYT Games."""
        url = URL.build(
            scheme="https",
            host=host,
            port=443,
        ).joinpath(uri)

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True
        self.session.cookie_jar.update_cookies({"NYT-S": self.token})

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.get(url, headers=headers, params=params)
        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to NYT Games"
            raise NYTGamesConnectionError(msg) from exception
        except (
            ClientError,
            ClientResponseError,
            socket.gaierror,
        ) as exception:
            msg = "Error occurred while communicating with NYT Games"
            raise NYTGamesConnectionError(msg) from exception

        if response.status == 403:
            msg = "Unauthenticated"
            raise NYTGamesAuthenticationError(msg)

        if response.status != 200:
            content_type = response.headers.get("Content-Type", "")
            text = await response.text()
            msg = "Unexpected response from NYT Games"
            raise NYTGamesConnectionError(
                msg,
                {"Content-Type": content_type, "response": text},
            )

        return await response.text()

    async def _get_wordle_stats(self) -> WordleStats:
        response = await self._request(
            "svc/games/state/wordleV2/latests",
            "nytimes.com",
            headers={
                "User-Agent": f"PythonNYTGames/{VERSION}",
                "Accept": "application/json",
            },
        )
        return WordleStats.from_json(response)

    async def get_user_id(self) -> int:
        """Get user identifier."""
        return (await self._get_wordle_stats()).player.user_id

    async def get_latest_stats(self) -> LatestDataStats:
        """Get latest stats."""
        return (await self._get_wordle_stats()).player.stats

    async def get_crossword_stats(self) -> CrosswordStatsAndStreaks:
        """Get crossword stats."""
        response = await self._request(
            "svc/crosswords/v3/10781499/stats-and-streaks.json",
            "nytimes.com",
            params={
                "date_start": "1988-01-01",  # nyt.com uses this date
                "start_on_monday": "true",
            },
            headers={
                "User-Agent": f"PythonNYTGames/{VERSION}",
                "Accept": "application/json",
            },
        )
        return CrosswordStatsInfo.from_json(response).results

    async def get_connections(self) -> Connections | None:
        """Get connections stats."""
        response = await self._request(
            "svc/games/state/connections/latests",
            "nytimes.com",
            params={"puzzle_ids": "0"},
            headers={
                "User-Agent": f"PythonNYTGames/{VERSION}",
                "Accept": "application/json",
            },
        )
        data = json.loads(response)
        if (
            "player" not in data
            or not data["player"]["stats"]["connections"]["last_played_print_date"]
        ):
            return None
        return ConnectionsStats.from_dict(data).player.stats

    async def get_strands(self) -> Strands | None:
        """Get strands stats."""
        response = await self._request(
            uri="svc/games/state/strands/latests",
            host="nytimes.com",
            params={"puzzle_ids": "0"},
            headers={
                "User-Agent": f"PythonNYTGames/{VERSION}",
                "Accept": "application/json",
            },
        )
        data = json.loads(response)
        if (
            "player" not in data
            or not data["player"]["stats"]["strands"]["last_played_print_date"]
        ):
            return None
        return StrandsStats.from_dict(data).player.stats

    async def friends(self, operation: str, sha: str) -> str:  # response
        """General function for getting friends' game stats."""
        timestamp = str(int(dt.datetime.now().timestamp()))
        iso_date = str(dt.datetime.now()).split(" ", maxsplit=1)[
            0
        ]  # YYYY-MM-DD fetches data for any day
        p = Path(__file__).with_name("private_key.txt")
        with p.open("rb") as f:
            key_bytes = f.read()

        private_key = serialization.load_pem_private_key(key_bytes, password=None)

        payload = f"{timestamp}\n/graphql/v2\nNYT-Android-Crossword\n6.20.0\n"

        # Sign using SHA256withRSA
        signature = private_key.sign(
            payload.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256()
        )
        encoded_signature = base64.b64encode(signature).decode("utf-8")

        return await self._request(
            "graphql/v2",
            "samizdat-graphql.nytimes.com",
            params={
                "operationName": operation,
                "variables": '{"date":"' + iso_date + '"}',
                "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"'
                + sha
                + '"}}',
            },
            headers={
                "User-Agent": f"PythonNYTGames/{VERSION}",
                "Accept": "application/json",
                "NYT-App-Type": "NYT-Android-Crossword",
                "NYT-App-Version": "6.20.0",
                "NYT-Signature": encoded_signature,
                "NYT-Timestamp": timestamp,
            },
        )

    async def get_connections_friends(self) -> FriendStats | None:
        """Get friends' connection stats."""
        response = await self.friends(
            "ConnectionsLeaderboardQuery",
            "a97d5f6a5636062db6270262a0a99f3667daefccc3041e26e0586580da65c603",
        )

        if "data" not in response or 'last_played_print_date": ""' in response:
            return None
        return ConnectionsFriendsStats.from_json(response).data.user.friends

    async def get_wordle_friends(self) -> FriendStats | None:
        """Get friends' Wordle stats."""
        response = await self.friends(
            "WordleLeaderboardQuery",
            "e52296849c8216da033745e64b18401a773930e63049f7039ca384f9c5eab5fe",
        )
        if "data" not in response or 'last_played_print_date": ""' in response:
            return None
        return WordleFriendsStats.from_json(response).data.user.friends

    async def get_bee_friends(self) -> FriendStats | None:
        """Get friends' Spelling Bee stats."""
        response = await self.friends(
            "SpellingBeeLeaderboardQuery",
            "eb9e98bf42792576071829ef4d7eb9e04db2265da9d9cb4a79f234f78affd74d",
        )
        if "data" not in response or 'last_played_print_date": ""' in response:
            return None
        return BeeFriendsStats.from_json(response).data.user.friends

    async def get_mini_friends(self) -> FriendStats | None:
        """Get friends' Mini Crossword stats."""
        response = await self.friends(
            "MiniCrosswordLeaderboardQuery",
            "641632a3454c8e6dad7a9dd49c5cfde9fd7868345eef0d02b4215085955dad68",
        )
        if "data" not in response or 'last_played_print_date": ""' in response:
            return None
        return MiniFriendsStats.from_json(response).data.user.friends

    async def get_midi_friends(self) -> FriendStats | None:
        """Get friends' Midi cross stats."""
        response = await self.friends(
            "MidiLeaderboardQuery",
            "db3a507e9ea456b56f8191c9e410772674d1f01268f81ea2162be42b34b42248",
        )
        if "data" not in response or 'last_played_print_date": ""' in response:
            return None
        return MidiFriendsStats.from_json(response).data.user.friends

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The NYTGamesClient object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
