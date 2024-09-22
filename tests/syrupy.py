"""Asynchronous Python client for NYTGames."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import TYPE_CHECKING, Any

from syrupy.extensions import AmberSnapshotExtension
from syrupy.extensions.amber import AmberDataSerializer

if TYPE_CHECKING:
    from syrupy.types import (
        PropertyFilter,
        PropertyMatcher,
        PropertyPath,
        SerializableData,
    )


class NYTGamesSnapshotSerializer(AmberDataSerializer):
    """NYT Games snapshot serializer for Syrupy.

    Handles special cases for NYT Games data structures.
    """

    @classmethod
    def _serialize(  # pylint: disable=too-many-arguments
        cls,
        data: SerializableData,
        *,
        depth: int = 0,
        exclude: PropertyFilter | None = None,
        include: PropertyFilter | None = None,
        matcher: PropertyMatcher | None = None,
        path: PropertyPath = (),
        visited: set[Any] | None = None,
    ) -> str:
        """Pre-process data before serializing.

        This allows us to handle specific cases for
        NYT Games data structures.
        """
        serializable_data = data
        if is_dataclass(type(data)):
            serializable_data = asdict(data)

        return super()._serialize(
            serializable_data,
            depth=depth,
            exclude=exclude,
            include=include,
            matcher=matcher,
            path=path,
            visited=visited,
        )


class NYTGamesSnapshotExtension(AmberSnapshotExtension):
    """NYT Games extension for Syrupy."""

    VERSION = "1"
    """Current version of serialization format.

    Need to be bumped when we change the NYTGamesSnapshotSerializer.
    """

    serializer_class: type[AmberDataSerializer] = NYTGamesSnapshotSerializer
