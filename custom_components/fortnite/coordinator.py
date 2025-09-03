"""Data update coordinator for Fortnite Stats."""
from __future__ import annotations

import logging
from datetime import timedelta

from fortnite_python import Fortnite
from fortnite_python.domain import Mode, Platform

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_API_KEY,
    CONF_GAME_MODE,
    CONF_GAME_PLATFORM,
    CONF_PLAYER_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class FortniteDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Fortnite API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.api_key = entry.data[CONF_API_KEY]
        self.player_id = entry.data[CONF_PLAYER_ID]
        
        # Map Fortnite Tracker platform names to fortnite-python Platform enum
        platform_mapping = {
            "pc": Platform.PC,
            "xbox": Platform.XBOX,
            "psn": Platform.PSN,
            "switch": Platform.GAMEPAD,  # Nintendo Switch uses GAMEPAD in fortnite-python
            "kbm": Platform.KBM
        }
        
        self.platform = platform_mapping.get(entry.data[CONF_GAME_PLATFORM], Platform.PC)
        self.mode = Mode[entry.data[CONF_GAME_MODE]]
        
        # Initialize Fortnite API
        self.game = Fortnite(self.api_key)
        self.player = self.game.player(self.player_id, self.platform)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            # Run the API call in an executor since it's synchronous
            stats = await self.hass.async_add_executor_job(
                self.player.get_stats, self.mode
            )
            
            # Transform stats into a dict
            return {
                "top1": stats.top1,
                "top3": stats.top3,
                "top5": stats.top5,
                "top6": stats.top6,
                "top10": stats.top10,
                "top12": stats.top12,
                "top25": stats.top25,
                "kills": stats.kills,
                "kd": stats.kd,
                "kpg": stats.kpg,
                "matches": stats.matches,
                "score": stats.score,
                "score_per_match": stats.score_per_match,
                "id": stats.id,
                "win_ratio": stats.win_ratio,
            }
        except Exception as err:
            _LOGGER.error("Error communicating with Fortnite API: %s", err)
            raise UpdateFailed(f"Error communicating with Fortnite API: {err}") from err
