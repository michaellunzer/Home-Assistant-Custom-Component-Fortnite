"""Simple config flow for Fortnite Stats - shows all data by default."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_AGGREGATED_SENSORS

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("api_key"): str,
        vol.Required("player_id"): str,
        vol.Optional(CONF_AGGREGATED_SENSORS, default=True): bool,
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain="fortnite"):
    """Handle a config flow for Fortnite Stats with all platforms and game modes by default."""
    
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

        # Try to validate the API key and player data
        try:
            await self._test_connection(user_input)
        except Exception as err:
            _LOGGER.warning("API validation failed (will use fallback data): %s", err)
            # Don't show error - just log it and continue with fallback data

        # Add default platforms and game modes (consolidated by API endpoint)
        user_input["platforms"] = ["gamepad", "keyboardMouse"]
        user_input["game_modes"] = ["solo", "duo", "squad"]
        
        return self.async_create_entry(
            title=f"Fortnite Stats - {user_input['player_id']}",
            data=user_input,
        )

    async def _test_connection(self, user_input: dict[str, Any]) -> None:
        """Test the connection to fortnite-api.com."""
        api_key = user_input["api_key"]
        player_id = user_input["player_id"]
        
        # Test with gamepad platform (Switch)
        url = "https://fortnite-api.com/v2/stats/br/v2"
        params = {
            "name": player_id,
            "accountType": "epic",
            "timeWindow": "lifetime",
            "image": "gamepad"
        }
        headers = {"Authorization": api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") != 200:
                        raise Exception(f"API error: {data.get('error', 'Unknown error')}")
                elif response.status == 401:
                    raise Exception("Invalid API key")
                elif response.status == 404:
                    raise Exception("Player not found")
                else:
                    raise Exception(f"API error: {response.status}")
