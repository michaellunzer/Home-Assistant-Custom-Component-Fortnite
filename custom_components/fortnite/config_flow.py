"""Config flow for Fortnite Stats."""
from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_STATS_URL,
    CONF_AGGREGATED_SENSORS,
    CONF_API_KEY,
    CONF_PLAYER_ID,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class InvalidAuth(Exception):
    """Raised when the API key is rejected."""


class PlayerNotFound(Exception):
    """Raised when the player name is not found."""


class CannotConnect(Exception):
    """Raised when the API cannot be reached."""


class FortniteConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fortnite Stats."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            player_id = user_input[CONF_PLAYER_ID]
            try:
                await self._validate(user_input[CONF_API_KEY], player_id)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except PlayerNotFound:
                errors[CONF_PLAYER_ID] = "player_not_found"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error validating Fortnite Stats")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(player_id.lower())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Fortnite Stats - {player_id}",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Required(CONF_PLAYER_ID): str,
                    vol.Optional(CONF_AGGREGATED_SENSORS, default=True): bool,
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Handle re-authentication when the API key becomes invalid."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm a new API key during re-authentication."""
        errors: dict[str, str] = {}
        reauth_entry = self._get_reauth_entry()

        if user_input is not None:
            player_id = reauth_entry.data[CONF_PLAYER_ID]
            try:
                await self._validate(user_input[CONF_API_KEY], player_id)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except PlayerNotFound:
                errors["base"] = "player_not_found"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during Fortnite Stats reauth")
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data_updates={CONF_API_KEY: user_input[CONF_API_KEY]},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            description_placeholders={CONF_PLAYER_ID: reauth_entry.data[CONF_PLAYER_ID]},
            errors=errors,
        )

    async def _validate(self, api_key: str, player_id: str) -> None:
        """Validate credentials against fortnite-api.com."""
        session = async_get_clientsession(self.hass)
        params = {
            "name": player_id,
            "accountType": "epic",
            "timeWindow": "lifetime",
        }
        headers = {"Authorization": api_key}

        try:
            response = await session.get(
                API_STATS_URL,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            )
        except (aiohttp.ClientError, TimeoutError) as err:
            raise CannotConnect from err

        if response.status in (401, 403):
            raise InvalidAuth
        if response.status == 404:
            raise PlayerNotFound
        if response.status != 200:
            raise CannotConnect

        try:
            data = await response.json()
        except (aiohttp.ClientError, ValueError) as err:
            raise CannotConnect from err

        if data.get("status") == 404:
            raise PlayerNotFound
        if data.get("status") != 200:
            raise CannotConnect
