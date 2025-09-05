"""Config flow for Fortnite Stats with API validation."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import PLATFORM_OPTIONS, MODE_OPTIONS

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("name"): str,
        vol.Required("api_key"): str,
        vol.Required("player_id"): str,
        vol.Required("game_platform"): vol.In(PLATFORM_OPTIONS),
        vol.Required("game_mode"): vol.In(MODE_OPTIONS),
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain="fortnite"):
    """Handle a config flow for Fortnite Stats."""
    
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
            )

        errors = {}

        # Validate the API key and player data
        try:
            await self._test_connection(user_input)
        except Exception as err:
            _LOGGER.error("API validation failed: %s", err)
            errors["base"] = "cannot_connect"

        if not errors:
            return self.async_create_entry(
                title=user_input["name"],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def _test_connection(self, user_input: dict[str, Any]) -> None:
        """Test the connection to the Fortnite API."""
        import aiohttp
        
        api_key = user_input["api_key"]
        player_id = user_input["player_id"]
        platform = user_input["game_platform"]
        
        # Test the API connection
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": api_key}
            url = f"https://fortniteapi.io/v1/stats?username={player_id}&platform={platform}"
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data.get("result"):
                        raise Exception("Invalid player data or API key")
                elif response.status == 401:
                    raise Exception("Invalid API key")
                elif response.status == 404:
                    raise Exception("Player not found")
                else:
                    raise Exception(f"API error: {response.status}")
