"""Options flow for Fortnite Stats - allows users to customize platforms and game modes."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

_LOGGER = logging.getLogger(__name__)

# Platform and game mode options
PLATFORM_OPTIONS = ["pc", "xbox", "psn", "gamepad", "kbm"]
GAME_MODE_OPTIONS = ["solo", "duo", "squad"]

class FortniteOptionsFlowHandler(OptionsFlow):
    """Handle options flow for Fortnite Stats."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Update the config entry with new options
            return self.async_create_entry(title="", data=user_input)

        # Pre-populate with current values
        current_platforms = self.config_entry.data.get("platforms", ["pc", "xbox", "psn", "gamepad", "kbm"])
        current_modes = self.config_entry.data.get("game_modes", ["solo", "duo", "squad"])

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("platforms", default=current_platforms): vol.In(PLATFORM_OPTIONS),
                vol.Optional("game_modes", default=current_modes): vol.In(GAME_MODE_OPTIONS),
            }),
        )

async def async_setup_options_flow(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> None:
    """Set up options flow."""
    config_entry.async_on_unload(
        config_entry.add_update_listener(async_update_options)
    )

async def async_update_options(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(config_entry.entry_id)
