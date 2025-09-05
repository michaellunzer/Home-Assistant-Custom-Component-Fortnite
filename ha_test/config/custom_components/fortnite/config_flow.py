"""Config flow for Fortnite Stats integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from fortnite_python import Fortnite
from fortnite_python.domain import Mode, Platform

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_GAME_MODE,
    CONF_GAME_PLATFORM,
    CONF_PLAYER_ID,
    DEFAULT_MODE,
    DEFAULT_PLATFORM,
    DOMAIN,
    MODE_OPTIONS,
    PLATFORM_OPTIONS,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_API_KEY): str,
        vol.Required(CONF_PLAYER_ID): str,
        vol.Required(CONF_GAME_PLATFORM, default=DEFAULT_PLATFORM): vol.In(PLATFORM_OPTIONS),
        vol.Required(CONF_GAME_MODE, default=DEFAULT_MODE): vol.In(MODE_OPTIONS),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    
    try:
        # Test the API key and player data
        game = Fortnite(data[CONF_API_KEY])
        
        # Map Fortnite Tracker platform names to fortnite-python Platform enum
        platform_mapping = {
            "pc": Platform.PC,
            "xbox": Platform.XBOX,
            "psn": Platform.PSN,
            "switch": Platform.GAMEPAD,  # Nintendo Switch uses GAMEPAD in fortnite-python
            "kbm": Platform.KBM
        }
        
        platform = platform_mapping.get(data[CONF_GAME_PLATFORM], Platform.PC)
        mode = Mode[data[CONF_GAME_MODE]]
        
        # Try to get player data to validate
        player = game.player(data[CONF_PLAYER_ID], platform)
        stats = player.get_stats(mode)
        
        # Return info that you want to store in the config entry
        return {
            "title": f"{data[CONF_NAME]} ({data[CONF_PLAYER_ID]})",
            "player_id": data[CONF_PLAYER_ID],
            "platform": data[CONF_GAME_PLATFORM],
            "mode": data[CONF_GAME_MODE],
        }
    except Exception as ex:
        _LOGGER.error("Failed to validate Fortnite API connection: %s", ex)
        raise CannotConnect from ex


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fortnite Stats."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
