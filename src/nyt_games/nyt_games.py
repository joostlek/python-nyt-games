"""Asynchronous Python client for NYT Games."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from importlib import metadata
import socket
from typing import TYPE_CHECKING

from aiohttp import ClientError, ClientResponseError, ClientSession
from yarl import URL

from .exceptions import NYTGamesAuthenticationError, NYTGamesConnectionError
from .models import LatestData, LatestDataPlayer

if TYPE_CHECKING:
    from typing_extensions import Self


VERSION = metadata.version(__package__)


@dataclass
class NYTGamesClient:
    """Main class for handling connections with NYT Games."""

    token: str
    session: ClientSession | None = None
    request_timeout: int = 10
    _close_session: bool = False

    async def _request(self, uri: str) -> str:
        """Handle a request to NYT Games."""
        url = URL.build(
            scheme="https",
            host="nytimes.com",
            port=443,
        ).joinpath(uri)

        headers = {
            "User-Agent": f"PythonNYTGames/{VERSION}",
            "Accept": "application/json",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True
        self.session.cookie_jar.update_cookies({"NYT-S": self.token})

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.get(
                    url,
                    headers=headers,
                )
        except asyncio.TimeoutError as exception:
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

    async def get_latest_stats(self) -> LatestDataPlayer:
        """Get latest stats."""
        response = await self._request("svc/games/state/wordleV2/latests")
        data = LatestData.from_json(response)
        return data.player

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
