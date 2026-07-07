"""DataUpdateCoordinator for Fortnite Stats."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_GAME_MODES,
    API_PLATFORMS,
    API_STATS_URL,
    CONF_API_KEY,
    CONF_PLAYER_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=15)


class FortniteDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch lifetime stats for one player from fortnite-api.com.

    A single request returns stats for every input type (all, gamepad,
    keyboardMouse, touch) and game mode, so one poll serves all sensors.
    """

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.api_key: str = entry.data[CONF_API_KEY]
        self.player_id: str = entry.data[CONF_PLAYER_ID]

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN} {self.player_id}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch and normalize stats from fortnite-api.com."""
        session = async_get_clientsession(self.hass)
        params = {
            "name": self.player_id,
            "accountType": "epic",
            "timeWindow": "lifetime",
        }
        headers = {"Authorization": self.api_key}

        try:
            response = await session.get(
                API_STATS_URL, params=params, headers=headers, timeout=REQUEST_TIMEOUT
            )
        except (aiohttp.ClientError, TimeoutError) as err:
            raise UpdateFailed(f"Error communicating with fortnite-api.com: {err}") from err

        if response.status == 401:
            raise ConfigEntryAuthFailed("Invalid fortnite-api.com API key")
        if response.status == 403:
            body = await self._safe_json(response)
            error_text = str(body.get("error", ""))
            if "private" in error_text.lower():
                raise UpdateFailed(
                    f"Stats for {self.player_id} are private; enable 'Show on career "
                    "leaderboard' in Fortnite settings"
                )
            raise ConfigEntryAuthFailed(f"fortnite-api.com rejected the API key: {error_text}")
        if response.status == 404:
            raise UpdateFailed(f"Player {self.player_id} not found")
        if response.status == 429:
            raise UpdateFailed("fortnite-api.com rate limit reached, will retry")
        if response.status != 200:
            raise UpdateFailed(f"fortnite-api.com returned HTTP {response.status}")

        payload = await self._safe_json(response)
        if payload.get("status") != 200 or "data" not in payload:
            raise UpdateFailed(f"fortnite-api.com error: {payload.get('error', 'unknown')}")

        return self._transform(payload["data"])

    @staticmethod
    async def _safe_json(response: aiohttp.ClientResponse) -> dict[str, Any]:
        """Parse a JSON body, returning an empty dict on failure."""
        try:
            return await response.json()
        except (aiohttp.ClientError, ValueError):
            return {}

    def _transform(self, data: dict[str, Any]) -> dict[str, Any]:
        """Normalize the API response into platform/mode stat dicts."""
        stats = data.get("stats") or {}
        account = data.get("account") or {}
        battle_pass = data.get("battlePass") or {}

        result: dict[str, Any] = {
            "player_id": self.player_id,
            "account_name": account.get("name"),
            "battle_pass_level": battle_pass.get("level"),
        }

        for platform in API_PLATFORMS:
            platform_block = stats.get(platform) or {}
            result[platform] = {
                mode: self._transform_mode(platform_block.get(mode) or {})
                for mode in API_GAME_MODES
            }

        return result

    @staticmethod
    def _transform_mode(mode_stats: dict[str, Any]) -> dict[str, Any]:
        """Map one API game-mode block to the internal stat keys."""
        win_rate = mode_stats.get("winRate") or 0
        return {
            "kills": mode_stats.get("kills", 0),
            "deaths": mode_stats.get("deaths", 0),
            "matches": mode_stats.get("matches", 0),
            "win_ratio": win_rate / 100,
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
        }
