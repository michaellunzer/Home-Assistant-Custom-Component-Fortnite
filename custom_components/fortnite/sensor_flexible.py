"""Flexible sensor platform for Fortnite Stats - handles multiple platforms and game modes."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FortniteDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Define all the sensors we want to create
SENSOR_TYPES = {
    "eliminations": {"name": "Eliminations", "unit": "eliminations", "icon": "mdi:target"},
    "wins": {"name": "Wins", "unit": "wins", "icon": "mdi:trophy"},
    "matches": {"name": "Matches", "unit": "matches", "icon": "mdi:gamepad-variant"},
    "win_rate": {"name": "Win Rate", "unit": "%", "icon": "mdi:percent"},
    "kd": {"name": "K/D Ratio", "unit": "ratio", "icon": "mdi:sword-cross"},
    "top10": {"name": "Top 10 Finishes", "unit": "finishes", "icon": "mdi:medal"},
    "top25": {"name": "Top 25 Finishes", "unit": "finishes", "icon": "mdi:medal"},
    "score": {"name": "Score", "unit": "points", "icon": "mdi:scoreboard"},
    "minutes_played": {"name": "Minutes Played", "unit": "min", "icon": "mdi:clock"},
}

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Fortnite Stats sensors based on a config entry."""
    coordinator: FortniteDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create sensors for all configured platforms and game modes
    entities = []
    
    # Get configured platforms and game modes
    platforms = config_entry.data.get("platforms", ["pc", "xbox", "psn", "gamepad", "kbm"])
    game_modes = config_entry.data.get("game_modes", ["solo", "duo", "squad"])
    
    for platform in platforms:
        for game_mode in game_modes:
            for sensor_key, sensor_info in SENSOR_TYPES.items():
                entities.append(
                    FortniteSensor(
                        coordinator, 
                        config_entry, 
                        sensor_key, 
                        sensor_info, 
                        platform,
                        game_mode
                    )
                )
    
    async_add_entities(entities)


class FortniteSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Fortnite Stats sensor."""

    def __init__(
        self, 
        coordinator: FortniteDataUpdateCoordinator, 
        config_entry: ConfigEntry,
        sensor_key: str,
        sensor_info: dict,
        platform: str,
        game_mode: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._sensor_key = sensor_key
        self._sensor_info = sensor_info
        self._platform = platform
        self._game_mode = game_mode
        
        # Set up the sensor properties
        platform_display = self._get_platform_display_name(platform)
        self._attr_name = f"{config_entry.data['player_id']} {platform_display} {game_mode.title()} {sensor_info['name']}"
        self._attr_unique_id = f"{config_entry.entry_id}_{config_entry.data['player_id']}_{platform}_{game_mode}_{sensor_key}"
        self._attr_icon = sensor_info["icon"]
        self._attr_native_unit_of_measurement = sensor_info["unit"]

    def _get_platform_display_name(self, platform: str) -> str:
        """Get a user-friendly display name for the platform."""
        platform_names = {
            "pc": "PC",
            "xbox": "Xbox",
            "psn": "PlayStation",
            "gamepad": "Switch",
            "kbm": "Keyboard & Mouse"
        }
        return platform_names.get(platform, platform.title())

    @property
    def native_value(self) -> float | int | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
            
        # Get the data for the specific platform and game mode
        platform_data = self.coordinator.data.get(self._platform, {})
        game_mode_data = platform_data.get(self._game_mode, {})
        
        # Map sensor keys to data keys
        data_mapping = {
            "eliminations": "kills",
            "wins": "top1",  # Wins are top1 finishes
            "matches": "matches",
            "win_rate": "win_ratio",
            "kd": "kd",
            "top10": "top10",
            "top25": "top25",
            "score": "score",
            "minutes_played": "minutes_played"
        }
        
        data_key = data_mapping.get(self._sensor_key)
        if data_key:
            value = game_mode_data.get(data_key)
            if value is not None:
                # Convert win_ratio to percentage
                if self._sensor_key == "win_rate":
                    return round(value * 100, 1)
                return value
        
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}
        
        platform_data = self.coordinator.data.get(self._platform, {})
        game_mode_data = platform_data.get(self._game_mode, {})
        
        return {
            "player_id": self._config_entry.data["player_id"],
            "platform": self._platform,
            "platform_display": self._get_platform_display_name(self._platform),
            "game_mode": self._game_mode,
            "using_real_api": self.coordinator.data.get("using_real_api", False),
            "last_modified": game_mode_data.get("last_modified", ""),
            "eliminations_per_match": game_mode_data.get("kpg", 0),
            "score_per_match": game_mode_data.get("score_per_match", 0),
            "top3": game_mode_data.get("top3", 0),
            "top5": game_mode_data.get("top5", 0),
            "top6": game_mode_data.get("top6", 0),
            "top12": game_mode_data.get("top12", 0),
        }
