"""Thin async client for the MeshWald REST API."""
from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from .const import REQUEST_TIMEOUT


class MeshWaldError(Exception):
    """Base error for the MeshWald API client."""


class MeshWaldAuthError(MeshWaldError):
    """Raised when the API key is invalid or revoked."""


class MeshWaldConnectionError(MeshWaldError):
    """Raised when the API cannot be reached."""


class MeshWaldNotFoundError(MeshWaldError):
    """Raised when a node has no data yet (HTTP 404)."""


class MeshWaldApiClient:
    """Talks to the authenticated /api/v1/data/* endpoints of a MeshWald backend."""

    def __init__(self, session: aiohttp.ClientSession, base_url: str, api_key: str) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._headers = {"X-API-Key": api_key, "Accept": "application/json"}

    async def _get(self, path: str) -> Any:
        try:
            async with self._session.get(
                f"{self._base_url}{path}",
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            ) as resp:
                if resp.status in (401, 403):
                    raise MeshWaldAuthError(f"API-Key abgelehnt ({resp.status})")
                if resp.status == 404:
                    raise MeshWaldNotFoundError(path)
                resp.raise_for_status()
                return await resp.json()
        except asyncio.TimeoutError as err:
            raise MeshWaldConnectionError("Zeitüberschreitung bei der Anfrage") from err
        except aiohttp.ClientError as err:
            raise MeshWaldConnectionError(str(err)) from err

    async def async_get_nodes(self) -> list[str]:
        """Return the list of known node IDs."""
        data = await self._get("/api/v1/data/nodes")
        return data.get("nodes", [])

    async def async_get_reading(self, node: str) -> dict[str, Any] | None:
        """Return the latest reading for a node, or None if it has no data yet."""
        try:
            return await self._get(f"/api/v1/data/sensors/{node}")
        except MeshWaldNotFoundError:
            return None
