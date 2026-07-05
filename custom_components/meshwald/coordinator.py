"""DataUpdateCoordinator for MeshWald."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MeshWaldApiClient, MeshWaldAuthError, MeshWaldConnectionError
from .const import LOGGER, SCAN_INTERVAL


class MeshWaldCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Polls the MeshWald API and keeps the latest reading per node."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, client: MeshWaldApiClient
    ) -> None:
        super().__init__(
            hass,
            LOGGER,
            name=f"meshwald_{entry.entry_id}",
            update_interval=SCAN_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        try:
            nodes = await self.client.async_get_nodes()
            data: dict[str, dict[str, Any]] = {}
            for node in nodes:
                reading = await self.client.async_get_reading(node)
                if reading is not None:
                    data[node] = reading
            return data
        except MeshWaldAuthError as err:
            raise ConfigEntryAuthFailed("API-Key wurde abgelehnt oder widerrufen") from err
        except MeshWaldConnectionError as err:
            raise UpdateFailed(str(err)) from err
