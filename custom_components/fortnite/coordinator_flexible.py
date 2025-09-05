"""Flexible coordinator for Fortnite Stats - handles multiple platforms and game modes."""
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
    CONF_PLAYER_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

# Mock data as fallback
MOCK_DATA = {
    "pc": {
        "solo": {"kills": 150, "matches": 80, "win_ratio": 0.12, "kd": 1.5, "kpg": 1.9, "top1": 6, "top10": 25, "top25": 40, "score": 20000, "score_per_match": 250.0, "minutes_played": 800, "id": "captain_crunch88_pc_solo"},
        "duo": {"kills": 100, "matches": 50, "win_ratio": 0.08, "kd": 1.2, "kpg": 2.0, "top1": 2, "top10": 15, "top25": 25, "score": 12000, "score_per_match": 240.0, "minutes_played": 500, "id": "captain_crunch88_pc_duo"},
        "squad": {"kills": 800, "matches": 400, "win_ratio": 0.15, "kd": 1.8, "kpg": 2.0, "top1": 30, "top10": 100, "top25": 150, "score": 100000, "score_per_match": 250.0, "minutes_played": 4000, "id": "captain_crunch88_pc_squad"}
    },
    "xbox": {
        "solo": {"kills": 120, "matches": 70, "win_ratio": 0.10, "kd": 1.3, "kpg": 1.7, "top1": 4, "top10": 20, "top25": 35, "score": 15000, "score_per_match": 214.3, "minutes_played": 700, "id": "captain_crunch88_xbox_solo"},
        "duo": {"kills": 80, "matches": 45, "win_ratio": 0.07, "kd": 1.1, "kpg": 1.8, "top1": 1, "top10": 12, "top25": 20, "score": 10000, "score_per_match": 222.2, "minutes_played": 450, "id": "captain_crunch88_xbox_duo"},
        "squad": {"kills": 600, "matches": 300, "win_ratio": 0.12, "kd": 1.6, "kpg": 2.0, "top1": 20, "top10": 80, "top25": 120, "score": 75000, "score_per_match": 250.0, "minutes_played": 3000, "id": "captain_crunch88_xbox_squad"}
    },
    "psn": {
        "solo": {"kills": 110, "matches": 65, "win_ratio": 0.09, "kd": 1.2, "kpg": 1.7, "top1": 3, "top10": 18, "top25": 30, "score": 14000, "score_per_match": 215.4, "minutes_played": 650, "id": "captain_crunch88_psn_solo"},
        "duo": {"kills": 70, "matches": 40, "win_ratio": 0.06, "kd": 1.0, "kpg": 1.8, "top1": 1, "top10": 10, "top25": 18, "score": 9000, "score_per_match": 225.0, "minutes_played": 400, "id": "captain_crunch88_psn_duo"},
        "squad": {"kills": 500, "matches": 250, "win_ratio": 0.10, "kd": 1.4, "kpg": 2.0, "top1": 15, "top10": 70, "top25": 100, "score": 60000, "score_per_match": 240.0, "minutes_played": 2500, "id": "captain_crunch88_psn_squad"}
    },
    "gamepad": {
        "solo": {"kills": 202, "matches": 120, "win_ratio": 0.075, "kd": 1.82, "kpg": 1.683, "top1": 9, "top10": 43, "top25": 60, "score": 30029, "score_per_match": 250.242, "minutes_played": 1124, "id": "captain_crunch88_gamepad_solo"},
        "duo": {"kills": 32, "matches": 22, "win_ratio": 0.045, "kd": 1.524, "kpg": 1.455, "top1": 1, "top10": 0, "top25": 0, "score": 4549, "score_per_match": 206.773, "minutes_played": 168, "id": "captain_crunch88_gamepad_duo"},
        "squad": {"kills": 1639, "matches": 793, "win_ratio": 0.164, "kd": 2.472, "kpg": 2.067, "top1": 130, "top10": 0, "top25": 0, "score": 225265, "score_per_match": 284.067, "minutes_played": 8262, "id": "captain_crunch88_gamepad_squad"}
    },
    "kbm": {
        "solo": {"kills": 180, "matches": 90, "win_ratio": 0.11, "kd": 1.6, "kpg": 2.0, "top1": 7, "top10": 30, "top25": 50, "score": 18000, "score_per_match": 200.0, "minutes_played": 900, "id": "captain_crunch88_kbm_solo"},
        "duo": {"kills": 90, "matches": 55, "win_ratio": 0.09, "kd": 1.4, "kpg": 1.6, "top1": 3, "top10": 20, "top25": 30, "score": 11000, "score_per_match": 200.0, "minutes_played": 550, "id": "captain_crunch88_kbm_duo"},
        "squad": {"kills": 700, "matches": 350, "win_ratio": 0.13, "kd": 1.7, "kpg": 2.0, "top1": 25, "top10": 90, "top25": 130, "score": 85000, "score_per_match": 242.9, "minutes_played": 3500, "id": "captain_crunch88_kbm_squad"}
    }
}

class FortniteDataUpdateCoordinator(DataUpdateCoordinator):
    """Flexible coordinator for Fortnite Stats handling multiple platforms and game modes."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.api_key = entry.data[CONF_API_KEY]
        self.player_id = entry.data[CONF_PLAYER_ID]
        
        # Get configured platforms and game modes, with defaults
        self.platforms = entry.data.get("platforms", ["pc", "xbox", "psn", "gamepad", "kbm"])
        self.game_modes = entry.data.get("game_modes", ["solo", "duo", "squad"])
        
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
        """Try to get data from fortnite-api.com for all configured platforms."""
        result = {
            "using_real_api": True,
            "player_id": self.player_id,
            "platforms": self.platforms,
            "game_modes": self.game_modes
        }
        
        # Map platform names to API format
        platform_mapping = {
            "pc": "keyboardMouse",
            "xbox": "gamepad", 
            "psn": "gamepad",
            "gamepad": "gamepad",  # Nintendo Switch uses "gamepad"
            "kbm": "keyboardMouse"
        }
        
        # Get data for each platform
        for platform in self.platforms:
            api_platform = platform_mapping.get(platform, "gamepad")
            
            try:
                platform_data = await self._get_platform_data(api_platform)
                result[platform] = platform_data
            except Exception as e:
                _LOGGER.warning("Failed to get data for platform %s: %s", platform, e)
                # Use mock data for this platform
                result[platform] = self._get_mock_platform_data(platform)
        
        return result

    async def _get_platform_data(self, api_platform: str) -> dict[str, Any]:
        """Get data for a specific platform from the API."""
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
                        return self._transform_platform_data(data, api_platform)
                    else:
                        raise Exception(f"API returned error: {data.get('error', 'Unknown error')}")
                else:
                    raise Exception(f"API error: {response.status}")

    def _transform_platform_data(self, data: dict, platform: str) -> dict[str, Any]:
        """Transform API response for a specific platform."""
        stats_data = data["data"]["stats"]
        platform_stats = stats_data.get(platform, {})
        
        result = {}
        for mode in self.game_modes:
            mode_stats = platform_stats.get(mode, {})
            
            # Calculate win ratio as decimal
            win_rate = mode_stats.get("winRate", 0) / 100 if mode_stats.get("winRate") else 0
            
            result[mode] = {
                "kills": mode_stats.get("kills", 0),
                "matches": mode_stats.get("matches", 0),
                "win_ratio": win_rate,
                "kd": mode_stats.get("kd", 0.0),
                "kpg": mode_stats.get("killsPerMatch", 0.0),
                "top1": mode_stats.get("wins", 0),
                "top3": mode_stats.get("top3", 0),
                "top5": mode_stats.get("top5", 0),
                "top6": mode_stats.get("top6", 0),
                "top10": mode_stats.get("top10", 0),
                "top12": mode_stats.get("top12", 0),
                "top25": mode_stats.get("top25", 0),
                "score": mode_stats.get("score", 0),
                "score_per_match": mode_stats.get("scorePerMatch", 0.0),
                "minutes_played": mode_stats.get("minutesPlayed", 0),
                "last_modified": mode_stats.get("lastModified", ""),
                "id": f"{self.player_id}_{platform}_{mode}",
            }
        
        return result

    def _get_mock_platform_data(self, platform: str) -> dict[str, Any]:
        """Get mock data for a specific platform."""
        return MOCK_DATA.get(platform, MOCK_DATA["gamepad"])

    async def _get_mock_data(self) -> dict[str, Any]:
        """Get mock data for all platforms."""
        result = {
            "using_real_api": False,
            "player_id": self.player_id,
            "platforms": self.platforms,
            "game_modes": self.game_modes
        }
        
        # Add some variation to make it feel more realistic
        import random
        variation = random.uniform(0.95, 1.05)
        
        for platform in self.platforms:
            platform_data = {}
            for mode in self.game_modes:
                base_data = MOCK_DATA.get(platform, MOCK_DATA["gamepad"]).get(mode, {}).copy()
                
                # Update some stats with variation
                base_data["kills"] = int(base_data["kills"] * variation)
                base_data["matches"] = int(base_data["matches"] * variation)
                base_data["score"] = int(base_data["score"] * variation)
                
                platform_data[mode] = base_data
            
            result[platform] = platform_data
        
        # Increment update count
        self._update_count += 1
        result["update_count"] = self._update_count
        
        return result
