"""Unit tests for Fortnite config flow."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch
from aioresponses import aioresponses

from custom_components.fortnite.config_flow import ConfigFlow
from custom_components.fortnite.const import CONF_AGGREGATED_SENSORS


@pytest.mark.unit
class TestConfigFlow:
    """Test cases for ConfigFlow."""

    def test_init(self):
        """Test config flow initialization."""
        flow = ConfigFlow()
        assert flow.VERSION == 1

    @pytest.mark.asyncio
    async def test_async_step_user_initial_form(self):
        """Test initial form display."""
        flow = ConfigFlow()
        result = await flow.async_step_user()
        
        assert result["type"] == "form"
        assert result["step_id"] == "user"
        assert "data_schema" in result

    @pytest.mark.asyncio
    async def test_async_step_user_success(self, mock_api_response):
        """Test successful user input."""
        flow = ConfigFlow()
        user_input = {
            "api_key": "test_api_key_12345",
            "player_id": "test_player",
            CONF_AGGREGATED_SENSORS: True
        }
        
        with aioresponses() as m:
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload=mock_api_response,
                status=200
            )
            
            result = await flow.asyncio_step_user(user_input)
            
            assert result["type"] == "create_entry"
            assert result["data"]["api_key"] == "test_api_key_12345"
            assert result["data"]["player_id"] == "test_player"
            assert result["data"]["platforms"] == ["gamepad", "keyboardMouse"]
            assert result["data"]["game_modes"] == ["solo", "duo", "squad"]

    @pytest.mark.asyncio
    async def test_async_step_user_invalid_api_key(self):
        """Test invalid API key handling."""
        flow = ConfigFlow()
        user_input = {
            "api_key": "invalid_key",
            "player_id": "test_player",
            CONF_AGGREGATED_SENSORS: True
        }
        
        with aioresponses() as m:
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload={"status": 401, "error": "Invalid API key"},
                status=401
            )
            
            result = await flow.asyncio_step_user(user_input)
            
            # Should still create entry but log warning
            assert result["type"] == "create_entry"

    @pytest.mark.asyncio
    async def test_async_step_user_player_not_found(self):
        """Test player not found handling."""
        flow = ConfigFlow()
        user_input = {
            "api_key": "test_api_key_12345",
            "player_id": "nonexistent_player",
            CONF_AGGREGATED_SENSORS: True
        }
        
        with aioresponses() as m:
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload={"status": 404, "error": "Player not found"},
                status=404
            )
            
            result = await flow.asyncio_step_user(user_input)
            
            # Should still create entry but log warning
            assert result["type"] == "create_entry"

    @pytest.mark.asyncio
    async def test_async_step_user_api_error(self):
        """Test API error handling."""
        flow = ConfigFlow()
        user_input = {
            "api_key": "test_api_key_12345",
            "player_id": "test_player",
            CONF_AGGREGATED_SENSORS: True
        }
        
        with aioresponses() as m:
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload={"status": 500, "error": "Internal server error"},
                status=500
            )
            
            result = await flow.asyncio_step_user(user_input)
            
            # Should still create entry but log warning
            assert result["type"] == "create_entry"

    @pytest.mark.asyncio
    async def test_test_connection_success(self, mock_api_response):
        """Test successful connection test."""
        flow = ConfigFlow()
        user_input = {
            "api_key": "test_api_key_12345",
            "player_id": "test_player"
        }
        
        with aioresponses() as m:
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload=mock_api_response,
                status=200
            )
            
            # Should not raise exception
            await flow._test_connection(user_input)

    @pytest.mark.asyncio
    async def test_test_connection_invalid_api_key(self):
        """Test connection test with invalid API key."""
        flow = ConfigFlow()
        user_input = {
            "api_key": "invalid_key",
            "player_id": "test_player"
        }
        
        with aioresponses() as m:
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload={"status": 401, "error": "Invalid API key"},
                status=401
            )
            
            with pytest.raises(Exception, match="Invalid API key"):
                await flow._test_connection(user_input)

    @pytest.mark.asyncio
    async def test_test_connection_player_not_found(self):
        """Test connection test with player not found."""
        flow = ConfigFlow()
        user_input = {
            "api_key": "test_api_key_12345",
            "player_id": "nonexistent_player"
        }
        
        with aioresponses() as m:
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload={"status": 404, "error": "Player not found"},
                status=404
            )
            
            with pytest.raises(Exception, match="Player not found"):
                await flow._test_connection(user_input)

    @pytest.mark.asyncio
    async def test_test_connection_api_error(self):
        """Test connection test with API error."""
        flow = ConfigFlow()
        user_input = {
            "api_key": "test_api_key_12345",
            "player_id": "test_player"
        }
        
        with aioresponses() as m:
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload={"status": 500, "error": "Internal server error"},
                status=500
            )
            
            with pytest.raises(Exception, match="API error: 500"):
                await flow._test_connection(user_input)

    @pytest.mark.asyncio
    async def test_test_connection_timeout(self):
        """Test connection test with timeout."""
        flow = ConfigFlow()
        user_input = {
            "api_key": "test_api_key_12345",
            "player_id": "test_player"
        }
        
        with aioresponses() as m:
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                exception=asyncio.TimeoutError()
            )
            
            with pytest.raises(asyncio.TimeoutError):
                await flow._test_connection(user_input)

    def test_validate_player_id(self):
        """Test player ID validation."""
        flow = ConfigFlow()
        
        # Valid player IDs
        assert flow._validate_player_id("test_player") is True
        assert flow._validate_player_id("player123") is True
        assert flow._validate_player_id("test_player_123") is True
        
        # Invalid player IDs
        assert flow._validate_player_id("") is False
        assert flow._validate_player_id("ab") is False  # Too short
        assert flow._validate_player_id("a" * 17) is False  # Too long
        assert flow._validate_player_id("test-player") is False  # Invalid char
        assert flow._validate_player_id("test player") is False  # Space

    def test_validate_api_key(self):
        """Test API key validation."""
        flow = ConfigFlow()
        
        # Valid API keys
        assert flow._validate_api_key("test_api_key_12345") is True
        assert flow._validate_api_key("a" * 20) is True
        
        # Invalid API keys
        assert flow._validate_api_key("") is False
        assert flow._validate_api_key("short") is False  # Too short
        assert flow._validate_api_key("a" * 5) is False  # Too short
