"""Consolidated sensor platform for Fortnite Stats - groups platforms by API endpoint."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_AGGREGATED_SENSORS, AGGREGATED_SENSOR_TYPES
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

    # Create sensors for consolidated platforms and game modes
    entities = []
    
    # Get configured platforms and game modes
    platforms = config_entry.data.get("platforms", ["gamepad", "keyboardMouse"])
    game_modes = config_entry.data.get("game_modes", ["solo", "duo", "squad"])
    
    # Create individual platform/mode sensors
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
    
    # Create aggregated sensors if enabled
    if config_entry.data.get(CONF_AGGREGATED_SENSORS, True):
        for aggregated_type in AGGREGATED_SENSOR_TYPES.keys():
            for sensor_key, sensor_info in SENSOR_TYPES.items():
                entities.append(
                    FortniteAggregatedSensor(
                        coordinator,
                        config_entry,
                        sensor_key,
                        sensor_info,
                        aggregated_type
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
        self._attr_name = f"Fortnite {config_entry.data['player_id']} {platform_display} {game_mode.title()} {sensor_info['name']}"
        self._attr_unique_id = f"{config_entry.entry_id}_{config_entry.data['player_id']}_{platform}_{game_mode}_{sensor_key}"
        self._attr_icon = sensor_info["icon"]
        self._attr_native_unit_of_measurement = sensor_info["unit"]

    def _get_platform_display_name(self, platform: str) -> str:
        """Get a user-friendly display name for the platform."""
        platform_names = {
            "gamepad": "Console",
            "keyboardMouse": "PC"
        }
        return platform_names.get(platform, platform.title())


class FortniteAggregatedSensor(CoordinatorEntity, SensorEntity):
    """Representation of an aggregated Fortnite Stats sensor."""

    def __init__(
        self, 
        coordinator: FortniteDataUpdateCoordinator, 
        config_entry: ConfigEntry,
        sensor_key: str,
        sensor_info: dict,
        aggregated_type: str
    ) -> None:
        """Initialize the aggregated sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._sensor_key = sensor_key
        self._sensor_info = sensor_info
        self._aggregated_type = aggregated_type
        
        # Set up the sensor properties
        aggregated_display = AGGREGATED_SENSOR_TYPES[aggregated_type]
        self._attr_name = f"Fortnite {config_entry.data['player_id']} {aggregated_display} {sensor_info['name']}"
        self._attr_unique_id = f"{config_entry.entry_id}_{config_entry.data['player_id']}_{aggregated_type}_{sensor_key}"
        self._attr_icon = sensor_info["icon"]
        self._attr_native_unit_of_measurement = sensor_info["unit"]

    @property
    def native_value(self) -> float | int | None:
        """Return the aggregated state of the sensor."""
        if not self.coordinator.data:
            return None
            
        # Calculate aggregated value based on type
        total_value = 0
        platforms = self.coordinator.data.get("platforms", ["gamepad", "keyboardMouse"])
        game_modes = self.coordinator.data.get("game_modes", ["solo", "duo", "squad"])
        
        # Map sensor keys to data keys
        data_mapping = {
            "eliminations": "kills",
            "wins": "top1",
            "matches": "matches",
            "win_rate": "win_ratio",
            "kd": "kd",
            "top10": "top10",
            "top25": "top25",
            "score": "score",
            "minutes_played": "minutes_played"
        }
        
        data_key = data_mapping.get(self._sensor_key)
        if not data_key:
            return None
            
        # Determine which platforms and modes to aggregate
        platforms_to_aggregate = []
        modes_to_aggregate = []
        
        if self._aggregated_type == "all_platforms_all_modes":
            platforms_to_aggregate = platforms
            modes_to_aggregate = game_modes
        elif self._aggregated_type == "console_all_modes":
            platforms_to_aggregate = ["gamepad"]
            modes_to_aggregate = game_modes
        elif self._aggregated_type == "pc_all_modes":
            platforms_to_aggregate = ["keyboardMouse"]
            modes_to_aggregate = game_modes
        elif self._aggregated_type == "all_platforms_solo":
            platforms_to_aggregate = platforms
            modes_to_aggregate = ["solo"]
        elif self._aggregated_type == "all_platforms_duo":
            platforms_to_aggregate = platforms
            modes_to_aggregate = ["duo"]
        elif self._aggregated_type == "all_platforms_squad":
            platforms_to_aggregate = platforms
            modes_to_aggregate = ["squad"]
        
        # Sum up values from selected platforms and modes
        for platform in platforms_to_aggregate:
            platform_data = self.coordinator.data.get(platform, {})
            for mode in modes_to_aggregate:
                mode_data = platform_data.get(mode, {})
                value = mode_data.get(data_key, 0)
                if value is not None:
                    total_value += value
        
        # Handle special cases
        if self._sensor_key == "win_rate" and total_value > 0:
            # For win rate, we need to calculate the weighted average
            total_matches = 0
            weighted_wins = 0
            for platform in platforms_to_aggregate:
                platform_data = self.coordinator.data.get(platform, {})
                for mode in modes_to_aggregate:
                    mode_data = platform_data.get(mode, {})
                    matches = mode_data.get("matches", 0)
                    wins = mode_data.get("top1", 0)
                    if matches > 0:
                        total_matches += matches
                        weighted_wins += wins
            
            if total_matches > 0:
                return round((weighted_wins / total_matches) * 100, 1)
            return 0.0
        elif self._sensor_key == "kd" and total_value > 0:
            # For K/D ratio, calculate weighted average
            total_eliminations = 0
            total_deaths = 0
            for platform in platforms_to_aggregate:
                platform_data = self.coordinator.data.get(platform, {})
                for mode in modes_to_aggregate:
                    mode_data = platform_data.get(mode, {})
                    eliminations = mode_data.get("kills", 0)
                    matches = mode_data.get("matches", 0)
                    if matches > 0:
                        # Estimate deaths: matches - wins
                        wins = mode_data.get("top1", 0)
                        deaths = matches - wins
                        total_eliminations += eliminations
                        total_deaths += deaths
            
            if total_deaths > 0:
                return round(total_eliminations / total_deaths, 3)
            return 0.0
        
        return total_value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}
        
        return {
            "player_id": self._config_entry.data["player_id"],
            "aggregated_type": self._aggregated_type,
            "aggregated_display": AGGREGATED_SENSOR_TYPES[self._aggregated_type],
            "platforms_included": self._get_platforms_included(),
            "modes_included": self._get_modes_included(),
        }
    
    def _get_platforms_included(self) -> list[str]:
        """Get list of platforms included in this aggregation."""
        platforms = self.coordinator.data.get("platforms", ["gamepad", "keyboardMouse"])
        
        if self._aggregated_type in ["all_platforms_all_modes", "all_platforms_solo", "all_platforms_duo", "all_platforms_squad"]:
            return platforms
        elif self._aggregated_type == "console_all_modes":
            return ["gamepad"]
        elif self._aggregated_type == "pc_all_modes":
            return ["keyboardMouse"]
        return []
    
    def _get_modes_included(self) -> list[str]:
        """Get list of game modes included in this aggregation."""
        game_modes = self.coordinator.data.get("game_modes", ["solo", "duo", "squad"])
        
        if self._aggregated_type in ["all_platforms_all_modes", "console_all_modes", "pc_all_modes"]:
            return game_modes
        elif self._aggregated_type == "all_platforms_solo":
            return ["solo"]
        elif self._aggregated_type == "all_platforms_duo":
            return ["duo"]
        elif self._aggregated_type == "all_platforms_squad":
            return ["squad"]
        return []
