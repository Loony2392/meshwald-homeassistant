"""Config flow for MeshWald."""
from __future__ import annotations

import hashlib
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MeshWaldApiClient, MeshWaldAuthError, MeshWaldConnectionError
from .const import CONF_API_KEY, CONF_BASE_URL, DEFAULT_BASE_URL, DOMAIN

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
        vol.Required(CONF_API_KEY): str,
    }
)


class MeshWaldConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MeshWald."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        errors: dict[str, str] = {}

        if user_input is not None:
            base_url = user_input[CONF_BASE_URL].rstrip("/")
            api_key = user_input[CONF_API_KEY].strip()

            # Eindeutigkeit über den Key selbst (nicht im Klartext), damit derselbe
            # Account nicht zweimal als Config Entry angelegt werden kann.
            await self.async_set_unique_id(hashlib.sha256(api_key.encode()).hexdigest())
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            client = MeshWaldApiClient(session, base_url, api_key)
            try:
                await client.async_get_nodes()
            except MeshWaldAuthError:
                errors["base"] = "invalid_auth"
            except MeshWaldConnectionError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title="MeshWald",
                    data={CONF_BASE_URL: base_url, CONF_API_KEY: api_key},
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors
        )
