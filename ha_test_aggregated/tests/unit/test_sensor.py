"""Unit tests for Fortnite sensors."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from custom_components.fortnite.sensor import (
    FortniteSensor,
    FortniteAggregatedSensor,
    SENSOR_TYPES
)


@pytest.mark.unit
class TestFortniteSensor:
    """Test cases for FortniteSensor."""

    def test_sensor_initialization(self, coordinator, mock_config_entry):
        """Test sensor initialization."""
        sensor = FortniteSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "gamepad",
            "solo"
        )
        
        assert sensor._sensor_key == "eliminations"
        assert sensor._platform == "gamepad"
        assert sensor._game_mode == "solo"
        assert sensor._attr_icon == "mdi:target"
        assert sensor._attr_native_unit_of_measurement == "eliminations"

    def test_sensor_name_generation(self, coordinator, mock_config_entry):
        """Test sensor name generation."""
        sensor = FortniteSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "gamepad",
            "solo"
        )
        
        expected_name = "Fortnite test_player Console Solo Eliminations"
        assert sensor._attr_name == expected_name

    def test_sensor_unique_id(self, coordinator, mock_config_entry):
        """Test sensor unique ID generation."""
        sensor = FortniteSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "gamepad",
            "solo"
        )
        
        expected_id = "test_entry_id_test_player_gamepad_solo_eliminations"
        assert sensor._attr_unique_id == expected_id

    def test_platform_display_name(self, coordinator, mock_config_entry):
        """Test platform display name mapping."""
        sensor = FortniteSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "gamepad",
            "solo"
        )
        
        assert sensor._get_platform_display_name("gamepad") == "Console"
        assert sensor._get_platform_display_name("keyboardMouse") == "PC"
        assert sensor._get_platform_display_name("unknown") == "Unknown"

    def test_native_value_with_data(self, coordinator, mock_config_entry, mock_api_response):
        """Test native value calculation with valid data."""
        # Set up coordinator data
        coordinator.data = {
            "using_real_api": True,
            "gamepad": {
                "solo": {
                    "kills": 100,
                    "matches": 50,
                    "win_ratio": 0.2,
                    "kd": 2.0,
                    "top1": 10,
                    "top10": 25,
                    "top25": 30,
                    "score": 15000,
                    "minutes_played": 500
                }
            }
        }
        
        sensor = FortniteSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "gamepad",
            "solo"
        )
        
        assert sensor.native_value == 100

    def test_native_value_win_rate_conversion(self, coordinator, mock_config_entry):
        """Test win rate conversion from decimal to percentage."""
        coordinator.data = {
            "gamepad": {
                "solo": {
                    "win_ratio": 0.2,
                    "kd": 2.0
                }
            }
        }
        
        win_rate_sensor = FortniteSensor(
            coordinator,
            mock_config_entry,
            "win_rate",
            SENSOR_TYPES["win_rate"],
            "gamepad",
            "solo"
        )
        
        assert win_rate_sensor.native_value == 20.0

    def test_native_value_kd_rounding(self, coordinator, mock_config_entry):
        """Test K/D ratio rounding."""
        coordinator.data = {
            "gamepad": {
                "solo": {
                    "kd": 2.123456789
                }
            }
        }
        
        kd_sensor = FortniteSensor(
            coordinator,
            mock_config_entry,
            "kd",
            SENSOR_TYPES["kd"],
            "gamepad",
            "solo"
        )
        
        assert kd_sensor.native_value == 2.123

    def test_native_value_no_data(self, coordinator, mock_config_entry):
        """Test native value when no data is available."""
        coordinator.data = None
        
        sensor = FortniteSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "gamepad",
            "solo"
        )
        
        assert sensor.native_value is None

    def test_extra_state_attributes(self, coordinator, mock_config_entry):
        """Test extra state attributes."""
        coordinator.data = {
            "using_real_api": True,
            "gamepad": {
                "solo": {
                    "last_modified": "2023-01-01T00:00:00Z",
                    "kpg": 2.0,
                    "score_per_match": 300.0
                }
            }
        }
        
        sensor = FortniteSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "gamepad",
            "solo"
        )
        
        attrs = sensor.extra_state_attributes
        
        assert attrs["player_id"] == "test_player"
        assert attrs["platform"] == "gamepad"
        assert attrs["platform_display"] == "Console"
        assert attrs["game_mode"] == "solo"
        assert attrs["using_real_api"] is True
        assert attrs["last_modified"] == "2023-01-01T00:00:00Z"
        assert attrs["kills_per_match"] == 2.0
        assert attrs["score_per_match"] == 300.0


@pytest.mark.unit
class TestFortniteAggregatedSensor:
    """Test cases for FortniteAggregatedSensor."""

    def test_aggregated_sensor_initialization(self, coordinator, mock_config_entry):
        """Test aggregated sensor initialization."""
        sensor = FortniteAggregatedSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "all_platforms_all_modes"
        )
        
        assert sensor._sensor_key == "eliminations"
        assert sensor._aggregated_type == "all_platforms_all_modes"
        assert sensor._attr_icon == "mdi:target"
        assert sensor._attr_native_unit_of_measurement == "eliminations"

    def test_aggregated_sensor_name_generation(self, coordinator, mock_config_entry):
        """Test aggregated sensor name generation."""
        sensor = FortniteAggregatedSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "all_platforms_all_modes"
        )
        
        expected_name = "Fortnite test_player All Platforms All Modes Eliminations"
        assert sensor._attr_name == expected_name

    def test_aggregated_sensor_unique_id(self, coordinator, mock_config_entry):
        """Test aggregated sensor unique ID generation."""
        sensor = FortniteAggregatedSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "all_platforms_all_modes"
        )
        
        expected_id = "test_entry_id_test_player_all_platforms_all_modes_eliminations"
        assert sensor._attr_unique_id == expected_id

    def test_aggregated_native_value_all_platforms(self, coordinator, mock_config_entry):
        """Test aggregated native value calculation for all platforms."""
        coordinator.data = {
            "using_real_api": True,
            "platforms": ["gamepad", "keyboardMouse"],
            "game_modes": ["solo", "duo", "squad"],
            "gamepad": {
                "solo": {"kills": 100},
                "duo": {"kills": 50},
                "squad": {"kills": 200}
            },
            "keyboardMouse": {
                "solo": {"kills": 0},
                "duo": {"kills": 0},
                "squad": {"kills": 0}
            }
        }
        
        sensor = FortniteAggregatedSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "all_platforms_all_modes"
        )
        
        # Should sum all kills from all platforms and modes
        assert sensor.native_value == 350

    def test_aggregated_native_value_console_only(self, coordinator, mock_config_entry):
        """Test aggregated native value calculation for console only."""
        coordinator.data = {
            "gamepad": {
                "solo": {"kills": 100},
                "duo": {"kills": 50},
                "squad": {"kills": 200}
            },
            "keyboardMouse": {
                "solo": {"kills": 0},
                "duo": {"kills": 0},
                "squad": {"kills": 0}
            }
        }
        
        sensor = FortniteAggregatedSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "console_all_modes"
        )
        
        # Should only sum kills from gamepad platform
        assert sensor.native_value == 350

    def test_aggregated_native_value_solo_only(self, coordinator, mock_config_entry):
        """Test aggregated native value calculation for solo only."""
        coordinator.data = {
            "gamepad": {
                "solo": {"kills": 100},
                "duo": {"kills": 50},
                "squad": {"kills": 200}
            },
            "keyboardMouse": {
                "solo": {"kills": 0},
                "duo": {"kills": 0},
                "squad": {"kills": 0}
            }
        }
        
        sensor = FortniteAggregatedSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "all_platforms_solo"
        )
        
        # Should only sum kills from solo mode across all platforms
        assert sensor.native_value == 100

    def test_aggregated_win_rate_calculation(self, coordinator, mock_config_entry):
        """Test aggregated win rate calculation."""
        coordinator.data = {
            "gamepad": {
                "solo": {"matches": 100, "top1": 20},
                "duo": {"matches": 50, "top1": 10},
                "squad": {"matches": 200, "top1": 50}
            },
            "keyboardMouse": {
                "solo": {"matches": 10, "top1": 2},
                "duo": {"matches": 5, "top1": 1},
                "squad": {"matches": 20, "top1": 5}
            }
        }
        
        sensor = FortniteAggregatedSensor(
            coordinator,
            mock_config_entry,
            "win_rate",
            SENSOR_TYPES["win_rate"],
            "all_platforms_all_modes"
        )
        
        # Total matches: 385, Total wins: 88
        # Win rate: (88/385) * 100 = 22.86%
        expected_rate = round((88 / 385) * 100, 1)
        assert sensor.native_value == expected_rate

    def test_aggregated_kd_calculation(self, coordinator, mock_config_entry):
        """Test aggregated K/D ratio calculation."""
        coordinator.data = {
            "gamepad": {
                "solo": {"kills": 100, "matches": 50, "top1": 10},
                "duo": {"kills": 50, "matches": 25, "top1": 5},
                "squad": {"kills": 200, "matches": 100, "top1": 25}
            }
        }
        
        sensor = FortniteAggregatedSensor(
            coordinator,
            mock_config_entry,
            "kd",
            SENSOR_TYPES["kd"],
            "console_all_modes"
        )
        
        # Total kills: 350, Total deaths: 175 - 40 = 135
        # K/D: 350/135 = 2.593
        expected_kd = round(350 / 135, 3)
        assert sensor.native_value == expected_kd

    def test_get_platforms_included(self, coordinator, mock_config_entry):
        """Test platforms included in aggregation."""
        coordinator.data = {
            "platforms": ["gamepad", "keyboardMouse"]
        }
        
        # Test all platforms
        sensor = FortniteAggregatedSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "all_platforms_all_modes"
        )
        assert sensor._get_platforms_included() == ["gamepad", "keyboardMouse"]
        
        # Test console only
        sensor = FortniteAggregatedSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "console_all_modes"
        )
        assert sensor._get_platforms_included() == ["gamepad"]
        
        # Test PC only
        sensor = FortniteAggregatedSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "pc_all_modes"
        )
        assert sensor._get_platforms_included() == ["keyboardMouse"]

    def test_get_modes_included(self, coordinator, mock_config_entry):
        """Test game modes included in aggregation."""
        coordinator.data = {
            "game_modes": ["solo", "duo", "squad"]
        }
        
        # Test all modes
        sensor = FortniteAggregatedSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "all_platforms_all_modes"
        )
        assert sensor._get_modes_included() == ["solo", "duo", "squad"]
        
        # Test solo only
        sensor = FortniteAggregatedSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "all_platforms_solo"
        )
        assert sensor._get_modes_included() == ["solo"]
        
        # Test duo only
        sensor = FortniteAggregatedSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "all_platforms_duo"
        )
        assert sensor._get_modes_included() == ["duo"]
        
        # Test squad only
        sensor = FortniteAggregatedSensor(
            coordinator,
            mock_config_entry,
            "eliminations",
            SENSOR_TYPES["eliminations"],
            "all_platforms_squad"
        )
        assert sensor._get_modes_included() == ["squad"]
