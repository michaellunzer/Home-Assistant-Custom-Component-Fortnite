"""Unit tests for Fortnite coordinator."""
from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
import aiohttp
from aioresponses import aioresponses

from custom_components.fortnite.coordinator import (
    FortniteDataUpdateCoordinator,
    MAX_REQUESTS_PER_SECOND,
    REQUEST_DELAY
)


@pytest.mark.unit
class TestFortniteDataUpdateCoordinator:
    """Test cases for FortniteDataUpdateCoordinator."""

    def test_init(self, coordinator):
        """Test coordinator initialization."""
        assert coordinator.api_key == "test_api_key_12345"
        assert coordinator.player_id == "test_player"
        assert coordinator.platforms == ["gamepad", "keyboardMouse"]
        assert coordinator.game_modes == ["solo", "duo", "squad"]

    @pytest.mark.asyncio
    async def test_enforce_rate_limit(self, coordinator):
        """Test that rate limiting works correctly."""
        start_time = time.time()
        await coordinator._enforce_rate_limit()
        await coordinator._enforce_rate_limit()
        elapsed = time.time() - start_time
        
        # Should have waited at least REQUEST_DELAY
        assert elapsed >= REQUEST_DELAY

    @pytest.mark.asyncio
    async def test_get_platform_data_success(self, coordinator, mock_api_response):
        """Test successful platform data retrieval."""
        with aioresponses() as m:
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload=mock_api_response,
                status=200
            )
            
            result = await coordinator._get_platform_data("gamepad")
            
            assert "solo" in result
            assert "duo" in result
            assert "squad" in result
            assert result["solo"]["kills"] == 100
            assert result["solo"]["matches"] == 50

    @pytest.mark.asyncio
    async def test_get_platform_data_api_error(self, coordinator, mock_error_response):
        """Test API error handling."""
        with aioresponses() as m:
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload=mock_error_response,
                status=400
            )
            
            with pytest.raises(Exception, match="API error: 400"):
                await coordinator._get_platform_data("gamepad")

    @pytest.mark.asyncio
    async def test_get_platform_data_rate_limit(self, coordinator, mock_api_response):
        """Test rate limit handling with retry."""
        with aioresponses() as m:
            # First request returns 429
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload={"status": 429, "error": "Rate limit exceeded"},
                status=429,
                headers={"Retry-After": "1"}
            )
            # Second request succeeds
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload=mock_api_response,
                status=200
            )
            
            result = await coordinator._get_platform_data("gamepad")
            
            assert "solo" in result
            assert result["solo"]["kills"] == 100

    @pytest.mark.asyncio
    async def test_transform_platform_data(self, coordinator, mock_api_response):
        """Test data transformation."""
        result = coordinator._transform_platform_data(mock_api_response, "gamepad")
        
        assert "solo" in result
        assert "duo" in result
        assert "squad" in result
        
        # Check that win_ratio is converted from percentage to decimal
        assert result["solo"]["win_ratio"] == 0.2  # 20% -> 0.2
        assert result["duo"]["win_ratio"] == 0.16  # 16% -> 0.16
        assert result["squad"]["win_ratio"] == 0.25  # 25% -> 0.25

    @pytest.mark.asyncio
    async def test_try_fortnite_api_success(self, coordinator, mock_api_response):
        """Test successful API data retrieval for all platforms."""
        with aioresponses() as m:
            # Mock responses for both platforms
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload=mock_api_response,
                status=200
            )
            
            result = await coordinator._try_fortnite_api()
            
            assert result["using_real_api"] is True
            assert "gamepad" in result
            assert "keyboardMouse" in result
            assert result["player_id"] == "test_player"

    @pytest.mark.asyncio
    async def test_try_fortnite_api_partial_failure(self, coordinator, mock_api_response):
        """Test partial API failure handling."""
        with aioresponses() as m:
            # First platform succeeds
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload=mock_api_response,
                status=200
            )
            # Second platform fails
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload={"status": 400, "error": "Invalid platform"},
                status=400
            )
            
            with pytest.raises(Exception):
                await coordinator._try_fortnite_api()

    @pytest.mark.asyncio
    async def test_async_update_data_success(self, coordinator, mock_api_response):
        """Test successful data update."""
        with aioresponses() as m:
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload=mock_api_response,
                status=200
            )
            
            result = await coordinator._async_update_data()
            
            assert result["using_real_api"] is True
            assert "gamepad" in result
            assert "keyboardMouse" in result

    @pytest.mark.asyncio
    async def test_async_update_data_failure(self, coordinator):
        """Test data update failure."""
        with aioresponses() as m:
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload={"status": 500, "error": "Internal server error"},
                status=500
            )
            
            with pytest.raises(Exception):
                await coordinator._async_update_data()

    def test_validate_player_id(self, coordinator):
        """Test player ID validation."""
        # Valid player IDs
        assert coordinator._validate_player_id("test_player") is True
        assert coordinator._validate_player_id("player123") is True
        assert coordinator._validate_player_id("test_player_123") is True
        
        # Invalid player IDs
        assert coordinator._validate_player_id("") is False
        assert coordinator._validate_player_id("ab") is False  # Too short
        assert coordinator._validate_player_id("a" * 17) is False  # Too long
        assert coordinator._validate_player_id("test-player") is False  # Invalid char
        assert coordinator._validate_player_id("test player") is False  # Space

    def test_sanitize_api_response(self, coordinator, mock_api_response):
        """Test API response sanitization."""
        # Add some invalid data
        mock_api_response["data"]["stats"]["gamepad"]["solo"]["kills"] = -5
        mock_api_response["data"]["stats"]["gamepad"]["solo"]["matches"] = None
        
        result = coordinator._sanitize_api_response(mock_api_response)
        
        # Check that negative values are corrected
        assert result["data"]["stats"]["gamepad"]["solo"]["kills"] == 0
        assert result["data"]["stats"]["gamepad"]["solo"]["matches"] == 0

    @pytest.mark.asyncio
    async def test_exponential_backoff_retry(self, coordinator):
        """Test exponential backoff retry logic."""
        call_count = 0
        
        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("API Error")
            return "success"
        
        result = await coordinator._exponential_backoff_retry(failing_func)
        
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_exponential_backoff_max_retries(self, coordinator):
        """Test exponential backoff with max retries exceeded."""
        async def always_failing_func():
            raise Exception("API Error")
        
        with pytest.raises(Exception, match="API Error"):
            await coordinator._exponential_backoff_retry(always_failing_func)

    def test_circuit_breaker_states(self, coordinator):
        """Test circuit breaker state management."""
        # Initially closed
        assert coordinator._circuit_state.value == "closed"
        assert coordinator._should_attempt_request() is True
        
        # Record failures to open circuit
        for _ in range(5):
            coordinator._record_failure()
        
        assert coordinator._circuit_state.value == "open"
        assert coordinator._should_attempt_request() is False
        
        # Record success to close circuit
        coordinator._record_success()
        assert coordinator._circuit_state.value == "closed"
        assert coordinator._should_attempt_request() is True
