"""Integration tests for Fortnite API."""
from __future__ import annotations

import pytest
from unittest.mock import patch
from aioresponses import aioresponses

from custom_components.fortnite.coordinator import FortniteDataUpdateCoordinator
from custom_components.fortnite.sensor import FortniteSensor, FortniteAggregatedSensor


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for Fortnite API."""

    @pytest.mark.asyncio
    async def test_full_data_flow(self, coordinator, mock_api_response):
        """Test complete data flow from API to sensors."""
        with aioresponses() as m:
            # Mock API responses for both platforms
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload=mock_api_response,
                status=200
            )
            
            # Update coordinator data
            result = await coordinator._async_update_data()
            
            # Verify data structure
            assert result["using_real_api"] is True
            assert "gamepad" in result
            assert "keyboardMouse" in result
            
            # Verify gamepad data
            gamepad_data = result["gamepad"]
            assert "solo" in gamepad_data
            assert "duo" in gamepad_data
            assert "squad" in gamepad_data
            
            # Verify solo data
            solo_data = gamepad_data["solo"]
            assert solo_data["kills"] == 100
            assert solo_data["matches"] == 50
            assert solo_data["win_ratio"] == 0.2
            assert solo_data["kd"] == 2.0

    @pytest.mark.asyncio
    async def test_sensor_data_flow(self, coordinator, mock_config_entry, mock_api_response):
        """Test data flow from coordinator to sensors."""
        with aioresponses() as m:
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload=mock_api_response,
                status=200
            )
            
            # Update coordinator data
            await coordinator._async_update_data()
            
            # Create sensor
            sensor = FortniteSensor(
                coordinator,
                mock_config_entry,
                "eliminations",
                {"name": "Eliminations", "unit": "eliminations", "icon": "mdi:target"},
                "gamepad",
                "solo"
            )
            
            # Verify sensor data
            assert sensor.native_value == 100
            assert sensor.extra_state_attributes["using_real_api"] is True
            assert sensor.extra_state_attributes["platform"] == "gamepad"
            assert sensor.extra_state_attributes["game_mode"] == "solo"

    @pytest.mark.asyncio
    async def test_aggregated_sensor_data_flow(self, coordinator, mock_config_entry, mock_api_response):
        """Test data flow from coordinator to aggregated sensors."""
        with aioresponses() as m:
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload=mock_api_response,
                status=200
            )
            
            # Update coordinator data
            await coordinator._async_update_data()
            
            # Create aggregated sensor
            sensor = FortniteAggregatedSensor(
                coordinator,
                mock_config_entry,
                "eliminations",
                {"name": "Eliminations", "unit": "eliminations", "icon": "mdi:target"},
                "all_platforms_all_modes"
            )
            
            # Verify aggregated sensor data
            assert sensor.native_value == 350  # 100 + 50 + 200 + 0 + 0 + 0
            assert sensor.extra_state_attributes["using_real_api"] is True
            assert sensor.extra_state_attributes["aggregated_type"] == "all_platforms_all_modes"

    @pytest.mark.asyncio
    async def test_rate_limiting_integration(self, coordinator, mock_api_response):
        """Test rate limiting in real API calls."""
        with aioresponses() as m:
            # Mock multiple API calls
            for _ in range(4):  # 2 platforms * 2 calls
                m.get(
                    "https://fortnite-api.com/v2/stats/br/v2",
                    payload=mock_api_response,
                    status=200
                )
            
            # Make multiple requests to test rate limiting
            start_time = time.time()
            await coordinator._get_platform_data("gamepad")
            await coordinator._get_platform_data("keyboardMouse")
            elapsed = time.time() - start_time
            
            # Should have waited at least REQUEST_DELAY between calls
            assert elapsed >= REQUEST_DELAY

    @pytest.mark.asyncio
    async def test_error_recovery_integration(self, coordinator, mock_api_response):
        """Test error recovery in real API calls."""
        with aioresponses() as m:
            # First call fails with 429
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload={"status": 429, "error": "Rate limit exceeded"},
                status=429,
                headers={"Retry-After": "1"}
            )
            # Second call succeeds
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload=mock_api_response,
                status=200
            )
            
            # Should recover from rate limit error
            result = await coordinator._get_platform_data("gamepad")
            assert "solo" in result
            assert result["solo"]["kills"] == 100

    @pytest.mark.asyncio
    async def test_partial_failure_recovery(self, coordinator, mock_api_response):
        """Test recovery from partial API failures."""
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
                payload={"status": 500, "error": "Internal server error"},
                status=500
            )
            
            # Should handle partial failure gracefully
            with pytest.raises(Exception):
                await coordinator._try_fortnite_api()

    @pytest.mark.asyncio
    async def test_data_validation_integration(self, coordinator, mock_api_response):
        """Test data validation in real API responses."""
        # Modify mock response to include invalid data
        mock_api_response["data"]["stats"]["gamepad"]["solo"]["kills"] = -5
        mock_api_response["data"]["stats"]["gamepad"]["solo"]["matches"] = None
        
        with aioresponses() as m:
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                payload=mock_api_response,
                status=200
            )
            
            # Should sanitize invalid data
            result = await coordinator._get_platform_data("gamepad")
            assert result["solo"]["kills"] == 0  # Negative value corrected
            assert result["solo"]["matches"] == 0  # None value corrected

    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self, coordinator):
        """Test circuit breaker in real API calls."""
        with aioresponses() as m:
            # Mock multiple failures
            for _ in range(6):  # More than failure threshold
                m.get(
                    "https://fortnite-api.com/v2/stats/br/v2",
                    payload={"status": 500, "error": "Internal server error"},
                    status=500
                )
            
            # Record multiple failures
            for _ in range(5):
                coordinator._record_failure()
            
            # Circuit should be open
            assert coordinator._circuit_state.value == "open"
            assert coordinator._should_attempt_request() is False
            
            # Record success
            coordinator._record_success()
            
            # Circuit should be closed
            assert coordinator._circuit_state.value == "closed"
            assert coordinator._should_attempt_request() is True

    @pytest.mark.asyncio
    async def test_exponential_backoff_integration(self, coordinator):
        """Test exponential backoff in real API calls."""
        call_count = 0
        
        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("API Error")
            return "success"
        
        # Should retry with exponential backoff
        result = await coordinator._exponential_backoff_retry(failing_func)
        
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_connection_pooling_integration(self, coordinator, mock_api_response):
        """Test connection pooling in real API calls."""
        with aioresponses() as m:
            # Mock multiple API calls
            for _ in range(4):
                m.get(
                    "https://fortnite-api.com/v2/stats/br/v2",
                    payload=mock_api_response,
                    status=200
                )
            
            # Make multiple requests to test connection reuse
            results = []
            for platform in ["gamepad", "keyboardMouse"]:
                result = await coordinator._get_platform_data(platform)
                results.append(result)
            
            # Both requests should succeed
            assert len(results) == 2
            assert "solo" in results[0]
            assert "solo" in results[1]

    @pytest.mark.asyncio
    async def test_timeout_handling_integration(self, coordinator):
        """Test timeout handling in real API calls."""
        with aioresponses() as m:
            m.get(
                "https://fortnite-api.com/v2/stats/br/v2",
                exception=asyncio.TimeoutError()
            )
            
            # Should handle timeout gracefully
            with pytest.raises(asyncio.TimeoutError):
                await coordinator._get_platform_data("gamepad")

    @pytest.mark.asyncio
    async def test_concurrent_requests_integration(self, coordinator, mock_api_response):
        """Test concurrent API requests."""
        with aioresponses() as m:
            # Mock multiple API calls
            for _ in range(4):
                m.get(
                    "https://fortnite-api.com/v2/stats/br/v2",
                    payload=mock_api_response,
                    status=200
                )
            
            # Make concurrent requests
            tasks = []
            for platform in ["gamepad", "keyboardMouse"]:
                task = coordinator._get_platform_data(platform)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            # Both requests should succeed
            assert len(results) == 2
            assert "solo" in results[0]
            assert "solo" in results[1]
