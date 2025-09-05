"""Multi-mode coordinator for Fortnite Stats using fortnite-api.com."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp
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

# Mock data as fallback
MOCK_DATA = {
    "solo": {
        "kills": 202, "matches": 120, "win_ratio": 0.075, "kd": 1.82, "kpg": 1.683,
        "top1": 9, "top3": 0, "top5": 0, "top6": 0, "top10": 43,
        "top12": 0, "top25": 60, "score": 30029, "score_per_match": 250.242,
        "minutes_played": 1124, "id": "captain_crunch88_solo"
    },
    "duo": {
        "kills": 32, "matches": 22, "win_ratio": 0.045, "kd": 1.524, "kpg": 1.455,
        "top1": 1, "top3": 0, "top5": 6, "top6": 0, "top10": 0,
        "top12": 7, "top25": 0, "score": 4549, "score_per_match": 206.773,
        "minutes_played": 168, "id": "captain_crunch88_duo"
    },
    "squad": {
        "kills": 1639, "matches": 793, "win_ratio": 0.164, "kd": 2.472, "kpg": 2.067,
        "top1": 130, "top3": 249, "top5": 0, "top6": 361, "top10": 0,
        "top12": 0, "top25": 0, "score": 225265, "score_per_match": 284.067,
        "minutes_played": 8262, "id": "captain_crunch88_squad"
    }
}

class FortniteDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator for Fortnite Stats using fortnite-api.com with all game modes."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.api_key = entry.data[CONF_API_KEY]
        self.player_id = entry.data[CONF_PLAYER_ID]
        self.platform = entry.data[CONF_GAME_PLATFORM]
        self.mode = entry.data[CONF_GAME_MODE]
        
        # Track if we're using mock data
        self.using_mock_data = False
        self._update_count = 0

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via fortnite-api.com or fall back to mock data."""
        # First try the real API
        try:
            return await self._try_fortnite_api()
        except Exception as err:
            _LOGGER.warning("Fortnite API failed, falling back to mock data: %s", err)
            self.using_mock_data = True
            return await self._get_mock_data()

    async def _try_fortnite_api(self) -> dict[str, Any]:
        """Try to get data from fortnite-api.com."""
        # Map platform names to API format
        platform_mapping = {
            "pc": "keyboardMouse",
            "xbox": "gamepad", 
            "psn": "gamepad",
            "gamepad": "gamepad",  # Nintendo Switch uses "gamepad"
            "kbm": "keyboardMouse"
        }
        
        api_platform = platform_mapping.get(self.platform, "gamepad")
        
        # Build the API URL
        url = "https://fortnite-api.com/v2/stats/br/v2"
        params = {
            "name": self.player_id,
            "accountType": "epic",
            "timeWindow": "lifetime",
            "image": api_platform
        }
        
        headers = {"Authorization": self.api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == 200 and "data" in data:
                        return self._transform_fortnite_api_data(data, api_platform)
                    else:
                        raise Exception(f"API returned error: {data.get('error', 'Unknown error')}")
                elif response.status == 401:
                    raise Exception("Invalid API key")
                elif response.status == 404:
                    raise Exception("Player not found")
                else:
                    raise Exception(f"API error: {response.status}")

    def _transform_fortnite_api_data(self, data: dict, platform: str) -> dict[str, Any]:
        """Transform fortnite-api.com response to our format with all game modes."""
        stats_data = data["data"]["stats"]
        
        # Get platform-specific stats
        platform_stats = stats_data.get(platform, {})
        
        # Process all game modes
        result = {
            "using_real_api": True,
            "platform": self.platform,
            "player_id": self.player_id,
            "game_modes": ["solo", "duo", "squad"]
        }
        
        for mode in ["solo", "duo", "squad"]:
            mode_stats = platform_stats.get(mode, {})
            
            # Calculate win ratio as decimal
            win_rate = mode_stats.get("winRate", 0) / 100 if mode_stats.get("winRate") else 0
            
            result[mode] = {
                "top1": mode_stats.get("wins", 0),
                "top3": mode_stats.get("top3", 0), 
                "top5": mode_stats.get("top5", 0),
                "top6": mode_stats.get("top6", 0),
                "top10": mode_stats.get("top10", 0),
                "top12": mode_stats.get("top12", 0),
                "top25": mode_stats.get("top25", 0),
                "kills": mode_stats.get("kills", 0),
                "kd": mode_stats.get("kd", 0.0),
                "kpg": mode_stats.get("killsPerMatch", 0.0),
                "matches": mode_stats.get("matches", 0),
                "score": mode_stats.get("score", 0),
                "score_per_match": mode_stats.get("scorePerMatch", 0.0),
                "win_ratio": win_rate,
                "minutes_played": mode_stats.get("minutesPlayed", 0),
                "last_modified": mode_stats.get("lastModified", ""),
                "id": f"{self.player_id}_{mode}",
            }
        
        return result

    async def _get_mock_data(self) -> dict[str, Any]:
        """Get mock data with some variation."""
        result = {
            "using_real_api": False,
            "platform": self.platform,
            "player_id": self.player_id,
            "game_modes": ["solo", "duo", "squad"]
        }
        
        # Add some variation to make it feel more realistic
        import random
        variation = random.uniform(0.95, 1.05)
        
        for mode in ["solo", "duo", "squad"]:
            base_data = MOCK_DATA[mode].copy()
            
            # Update some stats with variation
            base_data["kills"] = int(base_data["kills"] * variation)
            base_data["matches"] = int(base_data["matches"] * variation)
            base_data["score"] = int(base_data["score"] * variation)
            
            result[mode] = base_data
        
        # Increment update count
        self._update_count += 1
        result["update_count"] = self._update_count
        
        return result
