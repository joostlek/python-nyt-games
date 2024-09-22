"""Asynchronous Python client for NYT Games."""


class NYTGamesError(Exception):
    """Generic exception."""


class NYTGamesAuthenticationError(NYTGamesError):
    """NYT Games authentication exception."""


class NYTGamesConnectionError(NYTGamesError):
    """NYT Games connection exception."""


class NYTGamesParseError(NYTGamesError):
    """NYT Games parse exception."""
