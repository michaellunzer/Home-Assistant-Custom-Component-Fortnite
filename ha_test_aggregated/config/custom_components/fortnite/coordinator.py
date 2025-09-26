"""Consolidated coordinator for Fortnite Stats - groups platforms by API endpoint."""
from __future__ import annotations

import asyncio
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

# Rate limiting constants
MAX_REQUESTS_PER_SECOND = 2  # Stay under the 3 requests/second limit
REQUEST_DELAY = 1.0 / MAX_REQUESTS_PER_SECOND  # 0.5 seconds between requests

class FortniteDataUpdateCoordinator(DataUpdateCoordinator):
    """Consolidated coordinator for Fortnite Stats - groups platforms by API endpoint."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.api_key = entry.data[CONF_API_KEY]
        self.player_id = entry.data[CONF_PLAYER_ID]
        
        # Get configured platforms and game modes, with defaults
        self.platforms = entry.data.get("platforms", ["gamepad", "keyboardMouse"])
        self.game_modes = entry.data.get("game_modes", ["solo", "duo", "squad"])
        
        # Rate limiting
        self._last_request_time = 0.0
        self._request_lock = asyncio.Lock()

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via fortnite-api.com with proper rate limiting."""
        try:
            return await self._try_fortnite_api()
        except Exception as err:
            _LOGGER.error("Fortnite API failed: %s", err)
            raise UpdateFailed(f"Failed to update Fortnite data: {err}")

    async def _enforce_rate_limit(self) -> None:
        """Enforce rate limiting between API requests."""
        async with self._request_lock:
            current_time = asyncio.get_event_loop().time()
            time_since_last_request = current_time - self._last_request_time
            
            if time_since_last_request < REQUEST_DELAY:
                sleep_time = REQUEST_DELAY - time_since_last_request
                _LOGGER.debug("Rate limiting: sleeping for %.2f seconds", sleep_time)
                await asyncio.sleep(sleep_time)
            
            self._last_request_time = asyncio.get_event_loop().time()

    async def _try_fortnite_api(self) -> dict[str, Any]:
        """Try to get data from fortnite-api.com for all configured platforms."""
        result = {
            "using_real_api": True,
            "player_id": self.player_id,
            "platforms": self.platforms,
            "game_modes": self.game_modes
        }
        
        # Get data for each API endpoint with rate limiting
        for api_platform in self.platforms:
            try:
                await self._enforce_rate_limit()
                platform_data = await self._get_platform_data(api_platform)
                result[api_platform] = platform_data
                _LOGGER.debug("Successfully fetched data for platform %s", api_platform)
            except Exception as e:
                _LOGGER.error("Failed to get data for platform %s: %s", api_platform, e)
                raise
        
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
                elif response.status == 429:
                    # Rate limited - wait longer and retry
                    retry_after = int(response.headers.get('Retry-After', 60))
                    _LOGGER.warning("Rate limited (429). Waiting %d seconds before retry", retry_after)
                    await asyncio.sleep(retry_after)
                    # Retry the request
                    async with session.get(url, params=params, headers=headers, timeout=10) as retry_response:
                        if retry_response.status == 200:
                            data = await retry_response.json()
                            if data.get("status") == 200 and "data" in data:
                                return self._transform_platform_data(data, api_platform)
                        raise Exception(f"API retry failed with status: {retry_response.status}")
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
