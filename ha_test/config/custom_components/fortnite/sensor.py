"""Sensor platform for Fortnite Stats integration."""
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


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Fortnite Stats sensor based on a config entry."""
    coordinator: FortniteDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([FortniteSensor(coordinator, config_entry)])


class FortniteSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Fortnite Stats sensor."""

    def __init__(
        self, coordinator: FortniteDataUpdateCoordinator, config_entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = config_entry.data["name"]
        self._attr_unique_id = f"{config_entry.entry_id}_{config_entry.data['player_id']}_{config_entry.data['game_mode']}"
        self._attr_icon = "mdi:gamepad-variant"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("kills")
        return None

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "eliminations"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}
        
        return {
            "top1": self.coordinator.data.get("top1"),
            "top3": self.coordinator.data.get("top3"),
            "top5": self.coordinator.data.get("top5"),
            "top6": self.coordinator.data.get("top6"),
            "top10": self.coordinator.data.get("top10"),
            "top12": self.coordinator.data.get("top12"),
            "top25": self.coordinator.data.get("top25"),
            "kills": self.coordinator.data.get("kills"),
            "kd": self.coordinator.data.get("kd"),
            "kpg": self.coordinator.data.get("kpg"),
            "matches": self.coordinator.data.get("matches"),
            "score": self.coordinator.data.get("score"),
            "score_per_match": self.coordinator.data.get("score_per_match"),
            "id": self.coordinator.data.get("id"),
            "win_ratio": self.coordinator.data.get("win_ratio"),
            "player_id": self._config_entry.data["player_id"],
            "platform": self._config_entry.data["game_platform"],
            "game_mode": self._config_entry.data["game_mode"],
        }
