"""Pytest configuration and fixtures for Fortnite integration tests."""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock
from typing import Any, Dict

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.fortnite.coordinator import FortniteDataUpdateCoordinator
from custom_components.fortnite.const import CONF_API_KEY, CONF_PLAYER_ID


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {}
    return hass


@pytest.fixture
def mock_config_entry():
    """Create a mock configuration entry."""
    entry = MagicMock(spec=ConfigEntry)
    entry.data = {
        CONF_API_KEY: "test_api_key_12345",
        CONF_PLAYER_ID: "test_player",
        "platforms": ["gamepad", "keyboardMouse"],
        "game_modes": ["solo", "duo", "squad"],
        "aggregated_sensors": True
    }
    entry.entry_id = "test_entry_id"
    return entry


@pytest.fixture
def coordinator(mock_hass, mock_config_entry):
    """Create a Fortnite coordinator instance for testing."""
    return FortniteDataUpdateCoordinator(mock_hass, mock_config_entry)


@pytest.fixture
def mock_api_response():
    """Mock API response data."""
    return {
        "status": 200,
        "data": {
            "stats": {
                "gamepad": {
                    "solo": {
                        "kills": 100,
                        "matches": 50,
                        "winRate": 20.0,
                        "kd": 2.0,
                        "killsPerMatch": 2.0,
                        "wins": 10,
                        "top10": 25,
                        "top25": 30,
                        "score": 15000,
                        "scorePerMatch": 300.0,
                        "minutesPlayed": 500,
                        "lastModified": "2023-01-01T00:00:00Z"
                    },
                    "duo": {
                        "kills": 50,
                        "matches": 25,
                        "winRate": 16.0,
                        "kd": 1.5,
                        "killsPerMatch": 2.0,
                        "wins": 4,
                        "top10": 10,
                        "top25": 15,
                        "score": 7500,
                        "scorePerMatch": 300.0,
                        "minutesPlayed": 250,
                        "lastModified": "2023-01-01T00:00:00Z"
                    },
                    "squad": {
                        "kills": 200,
                        "matches": 100,
                        "winRate": 25.0,
                        "kd": 2.5,
                        "killsPerMatch": 2.0,
                        "wins": 25,
                        "top10": 50,
                        "top25": 60,
                        "score": 30000,
                        "scorePerMatch": 300.0,
                        "minutesPlayed": 1000,
                        "lastModified": "2023-01-01T00:00:00Z"
                    }
                },
                "keyboardMouse": {
                    "solo": {
                        "kills": 0,
                        "matches": 1,
                        "winRate": 0.0,
                        "kd": 0.0,
                        "killsPerMatch": 0.0,
                        "wins": 0,
                        "top10": 0,
                        "top25": 0,
                        "score": 77,
                        "scorePerMatch": 77.0,
                        "minutesPlayed": 5,
                        "lastModified": "2023-01-01T00:00:00Z"
                    },
                    "duo": {
                        "kills": 0,
                        "matches": 0,
                        "winRate": 0.0,
                        "kd": 0.0,
                        "killsPerMatch": 0.0,
                        "wins": 0,
                        "top10": 0,
                        "top25": 0,
                        "score": 0,
                        "scorePerMatch": 0.0,
                        "minutesPlayed": 0,
                        "lastModified": "2023-01-01T00:00:00Z"
                    },
                    "squad": {
                        "kills": 0,
                        "matches": 1,
                        "winRate": 0.0,
                        "kd": 0.0,
                        "killsPerMatch": 0.0,
                        "wins": 0,
                        "top10": 0,
                        "top25": 0,
                        "score": 77,
                        "scorePerMatch": 77.0,
                        "minutesPlayed": 5,
                        "lastModified": "2023-01-01T00:00:00Z"
                    }
                }
            }
        }
    }


@pytest.fixture
def mock_error_response():
    """Mock API error response."""
    return {
        "status": 400,
        "error": "Invalid player ID"
    }


@pytest.fixture
def mock_rate_limit_response():
    """Mock rate limit response."""
    return {
        "status": 429,
        "error": "Rate limit exceeded"
    }


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
