"""Sensor platform for Fortnite Stats."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import FortniteConfigEntry
from .const import (
    AGGREGATED_SENSOR_TYPES,
    API_GAME_MODES,
    API_PLATFORMS,
    CONF_AGGREGATED_SENSORS,
    DOMAIN,
    PLATFORM_DISPLAY_NAMES,
)
from .coordinator import FortniteDataUpdateCoordinator

# Input types that show as enabled entities by default. The combined "all"
# block is what users compare against fortnitetracker.com, so only it is
# enabled out of the box; per-input breakdowns can be enabled when wanted.
DEFAULT_ENABLED_PLATFORMS = {"all"}


@dataclass(frozen=True, kw_only=True)
class FortniteSensorEntityDescription(SensorEntityDescription):
    """Describes a Fortnite stat and how to read it from coordinator data."""

    data_key: str


SENSOR_DESCRIPTIONS: tuple[FortniteSensorEntityDescription, ...] = (
    FortniteSensorEntityDescription(
        key="eliminations",
        translation_key="eliminations",
        data_key="kills",
        icon="mdi:target",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    FortniteSensorEntityDescription(
        key="deaths",
        translation_key="deaths",
        data_key="deaths",
        icon="mdi:skull",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    FortniteSensorEntityDescription(
        key="wins",
        translation_key="wins",
        data_key="top1",
        icon="mdi:trophy",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    FortniteSensorEntityDescription(
        key="matches",
        translation_key="matches",
        data_key="matches",
        icon="mdi:gamepad-variant",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    FortniteSensorEntityDescription(
        key="win_rate",
        translation_key="win_rate",
        data_key="win_ratio",
        icon="mdi:percent",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    FortniteSensorEntityDescription(
        key="kd",
        translation_key="kd",
        data_key="kd",
        icon="mdi:sword-cross",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    FortniteSensorEntityDescription(
        key="kills_per_match",
        translation_key="kills_per_match",
        data_key="kpg",
        icon="mdi:target-account",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    FortniteSensorEntityDescription(
        key="top10",
        translation_key="top10",
        data_key="top10",
        icon="mdi:medal",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    FortniteSensorEntityDescription(
        key="top25",
        translation_key="top25",
        data_key="top25",
        icon="mdi:medal-outline",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    FortniteSensorEntityDescription(
        key="score",
        translation_key="score",
        data_key="score",
        icon="mdi:scoreboard",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    FortniteSensorEntityDescription(
        key="minutes_played",
        translation_key="minutes_played",
        data_key="minutes_played",
        icon="mdi:clock-outline",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FortniteConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Fortnite Stats sensors from a config entry."""
    coordinator = entry.runtime_data

    entities: list[SensorEntity] = []

    for platform in API_PLATFORMS:
        for game_mode in API_GAME_MODES:
            for description in SENSOR_DESCRIPTIONS:
                entities.append(
                    FortniteSensor(coordinator, description, platform, game_mode)
                )

    if entry.data.get(CONF_AGGREGATED_SENSORS, True):
        for aggregated_type in AGGREGATED_SENSOR_TYPES:
            for description in SENSOR_DESCRIPTIONS:
                entities.append(
                    FortniteAggregatedSensor(coordinator, description, aggregated_type)
                )

    async_add_entities(entities)


class FortniteBaseSensor(CoordinatorEntity[FortniteDataUpdateCoordinator], SensorEntity):
    """Common device wiring for Fortnite sensors."""

    _attr_has_entity_name = True
    entity_description: FortniteSensorEntityDescription

    def __init__(
        self,
        coordinator: FortniteDataUpdateCoordinator,
        description: FortniteSensorEntityDescription,
    ) -> None:
        """Initialize the base sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.player_id)},
            name=f"Fortnite {coordinator.player_id}",
            manufacturer="Epic Games",
            model="Battle Royale Stats",
            configuration_url="https://fortnite-api.com/",
        )


class FortniteSensor(FortniteBaseSensor):
    """A single stat for one input type and game mode."""

    def __init__(
        self,
        coordinator: FortniteDataUpdateCoordinator,
        description: FortniteSensorEntityDescription,
        platform: str,
        game_mode: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description)
        self._platform = platform
        self._game_mode = game_mode
        self._attr_unique_id = (
            f"{coordinator.player_id}_{platform}_{game_mode}_{description.key}"
        )
        self._attr_translation_placeholders = {
            "platform": PLATFORM_DISPLAY_NAMES.get(platform, platform),
            "mode": game_mode.title(),
        }
        self._attr_entity_registry_enabled_default = platform in DEFAULT_ENABLED_PLATFORMS

    @property
    def native_value(self) -> float | int | None:
        """Return the value for this stat."""
        mode_data = self._mode_data()
        if mode_data is None:
            return None
        value = mode_data.get(self.entity_description.data_key)
        if value is None:
            return None
        if self.entity_description.key == "win_rate":
            return round(value * 100, 1)
        return value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return supporting attributes."""
        mode_data = self._mode_data()
        if mode_data is None:
            return {}
        return {
            "player_id": self.coordinator.player_id,
            "input_type": self._platform,
            "game_mode": self._game_mode,
            "last_modified": mode_data.get("last_modified", ""),
        }

    def _mode_data(self) -> dict[str, Any] | None:
        """Return the coordinator stat block for this platform/mode."""
        if not self.coordinator.data:
            return None
        platform_data = self.coordinator.data.get(self._platform)
        if not platform_data:
            return None
        return platform_data.get(self._game_mode)


class FortniteAggregatedSensor(FortniteBaseSensor):
    """A stat summed across input types and/or game modes (locally computed)."""

    # Aggregated sums duplicate registry noise; off unless a user wants them.
    _attr_entity_registry_enabled_default = False
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    _AGGREGATIONS: dict[str, tuple[list[str], list[str]]] = {
        "all_platforms_all_modes": (["gamepad", "keyboardMouse"], ["solo", "duo", "squad"]),
        "console_all_modes": (["gamepad"], ["solo", "duo", "squad"]),
        "pc_all_modes": (["keyboardMouse"], ["solo", "duo", "squad"]),
        "all_platforms_solo": (["gamepad", "keyboardMouse"], ["solo"]),
        "all_platforms_duo": (["gamepad", "keyboardMouse"], ["duo"]),
        "all_platforms_squad": (["gamepad", "keyboardMouse"], ["squad"]),
    }

    def __init__(
        self,
        coordinator: FortniteDataUpdateCoordinator,
        description: FortniteSensorEntityDescription,
        aggregated_type: str,
    ) -> None:
        """Initialize the aggregated sensor."""
        super().__init__(coordinator, description)
        self._aggregated_type = aggregated_type
        self._attr_unique_id = (
            f"{coordinator.player_id}_agg_{aggregated_type}_{description.key}"
        )
        self._attr_translation_key = f"agg_{description.translation_key}"
        self._attr_translation_placeholders = {
            "aggregation": AGGREGATED_SENSOR_TYPES[aggregated_type],
        }

    def _blocks(self) -> list[dict[str, Any]]:
        """Return the stat blocks that make up this aggregation."""
        if not self.coordinator.data:
            return []
        platforms, modes = self._AGGREGATIONS[self._aggregated_type]
        blocks = []
        for platform in platforms:
            platform_data = self.coordinator.data.get(platform) or {}
            for mode in modes:
                mode_data = platform_data.get(mode)
                if mode_data:
                    blocks.append(mode_data)
        return blocks

    @property
    def native_value(self) -> float | int | None:
        """Return the aggregated value."""
        blocks = self._blocks()
        if not blocks:
            return None

        key = self.entity_description.key

        if key == "win_rate":
            total_wins = sum(b.get("top1", 0) for b in blocks)
            total_matches = sum(b.get("matches", 0) for b in blocks)
            if total_matches == 0:
                return 0.0
            return round(total_wins / total_matches * 100, 1)

        if key == "kd":
            total_kills = sum(b.get("kills", 0) for b in blocks)
            total_deaths = sum(b.get("deaths", 0) for b in blocks)
            if total_deaths == 0:
                return 0.0
            return round(total_kills / total_deaths, 2)

        if key == "kills_per_match":
            total_kills = sum(b.get("kills", 0) for b in blocks)
            total_matches = sum(b.get("matches", 0) for b in blocks)
            if total_matches == 0:
                return 0.0
            return round(total_kills / total_matches, 2)

        return sum(b.get(self.entity_description.data_key, 0) for b in blocks)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return supporting attributes."""
        platforms, modes = self._AGGREGATIONS[self._aggregated_type]
        return {
            "player_id": self.coordinator.player_id,
            "aggregation": AGGREGATED_SENSOR_TYPES[self._aggregated_type],
            "input_types_included": platforms,
            "game_modes_included": modes,
        }
