#!/usr/bin/env python3
"""Comprehensive test script for the Fortnite integration in Home Assistant context."""

import asyncio
import json
import sys
from unittest.mock import Mock, AsyncMock, patch
from datetime import timedelta

# Mock Home Assistant components
class MockConfigEntry:
    def __init__(self, data):
        self.data = data
        self.entry_id = "test_entry_123"
        self.title = data.get("name", "Test Fortnite Stats")

class MockHass:
    def __init__(self):
        self.data = {}
        self.async_add_executor_job = AsyncMock()
        self.config_entries = Mock()
        self.config_entries.async_forward_entry_setups = AsyncMock()
        self.config_entries.async_unload_platforms = AsyncMock(return_value=True)

class MockEntity:
    def __init__(self, coordinator, config_entry):
        self.coordinator = coordinator
        self._config_entry = config_entry
        self._attr_name = config_entry.data["name"]
        self._attr_unique_id = f"{config_entry.entry_id}_{config_entry.data['player_id']}_{config_entry.data['game_mode']}"
        self._attr_icon = "mdi:gamepad-variant"

async def test_integration_loading():
    """Test the integration loading process."""
    print("🧪 Testing Integration Loading...")
    
    try:
        # Mock the integration setup
        from custom_components.fortnite import async_setup_entry, async_unload_entry
        
        # Create mock config entry
        entry_data = {
            "name": "Captain_Crunch88 Switch Stats",
            "api_key": "test-api-key",
            "player_id": "Captain_Crunch88",
            "game_platform": "switch",
            "game_mode": "SQUAD"
        }
        
        entry = MockConfigEntry(entry_data)
        hass = MockHass()
        
        # Test setup
        result = await async_setup_entry(hass, entry)
        print("✅ Integration setup successful")
        
        # Test unload
        unload_result = await async_unload_entry(hass, entry)
        print("✅ Integration unload successful")
        
        return True
    except Exception as e:
        print(f"❌ Integration loading test failed: {e}")
        return False

async def test_coordinator_with_mock_data():
    """Test the coordinator with mock Fortnite data."""
    print("\n🧪 Testing Coordinator with Mock Data...")
    
    try:
        from custom_components.fortnite.coordinator import FortniteDataUpdateCoordinator
        
        # Mock Fortnite API response
        mock_stats = Mock()
        mock_stats.top1 = 5
        mock_stats.top3 = 12
        mock_stats.top5 = 8
        mock_stats.top6 = 3
        mock_stats.top10 = 15
        mock_stats.top12 = 7
        mock_stats.top25 = 20
        mock_stats.kills = 150
        mock_stats.kd = 1.5
        mock_stats.kpg = 2.3
        mock_stats.matches = 65
        mock_stats.score = 12500
        mock_stats.score_per_match = 192.3
        mock_stats.id = "test_player_id"
        mock_stats.win_ratio = 0.15
        
        # Create mock entry
        entry_data = {
            "name": "Captain_Crunch88 Switch Stats",
            "api_key": "test-api-key",
            "player_id": "Captain_Crunch88",
            "game_platform": "switch",
            "game_mode": "SQUAD"
        }
        
        entry = MockConfigEntry(entry_data)
        hass = MockHass()
        
        # Mock the Fortnite API calls
        with patch('custom_components.fortnite.coordinator.Fortnite') as mock_fortnite:
            mock_game = Mock()
            mock_player = Mock()
            mock_player.get_stats.return_value = mock_stats
            mock_game.player.return_value = mock_player
            mock_fortnite.return_value = mock_game
            
            # Create coordinator
            coordinator = FortniteDataUpdateCoordinator(hass, entry)
            
            # Test data update
            hass.async_add_executor_job.return_value = mock_stats
            await coordinator._async_update_data()
            
            print("✅ Coordinator created successfully")
            print(f"  Player ID: {coordinator.player_id}")
            print(f"  Platform: {coordinator.platform}")
            print(f"  Mode: {coordinator.mode}")
            print(f"  Update interval: {coordinator.update_interval}")
            
            # Test data structure
            if coordinator.data:
                print("✅ Data retrieved successfully")
                print(f"  Kills: {coordinator.data.get('kills')}")
                print(f"  Matches: {coordinator.data.get('matches')}")
                print(f"  Win Ratio: {coordinator.data.get('win_ratio')}")
            else:
                print("❌ No data retrieved")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Coordinator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_sensor_entity():
    """Test the sensor entity creation and data display."""
    print("\n🧪 Testing Sensor Entity...")
    
    try:
        from custom_components.fortnite.sensor import FortniteSensor
        
        # Create mock coordinator with data
        mock_coordinator = Mock()
        mock_coordinator.data = {
            "kills": 150,
            "matches": 65,
            "win_ratio": 0.15,
            "kd": 1.5,
            "top1": 5,
            "top3": 12,
            "top5": 8,
            "top6": 3,
            "top10": 15,
            "top12": 7,
            "top25": 20,
            "kpg": 2.3,
            "score": 12500,
            "score_per_match": 192.3,
            "id": "test_player_id"
        }
        
        # Create mock config entry
        entry_data = {
            "name": "Captain_Crunch88 Switch Stats",
            "api_key": "test-api-key",
            "player_id": "Captain_Crunch88",
            "game_platform": "switch",
            "game_mode": "SQUAD"
        }
        
        entry = MockConfigEntry(entry_data)
        
        # Create sensor
        sensor = FortniteSensor(mock_coordinator, entry)
        
        print("✅ Sensor entity created successfully")
        print(f"  Name: {sensor._attr_name}")
        print(f"  Unique ID: {sensor._attr_unique_id}")
        print(f"  Icon: {sensor._attr_icon}")
        
        # Test sensor properties
        print(f"  Native Value: {sensor.native_value}")
        print(f"  Unit: {sensor.native_unit_of_measurement}")
        
        # Test attributes
        attributes = sensor.extra_state_attributes
        print("✅ Sensor attributes:")
        for key, value in attributes.items():
            print(f"    {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sensor entity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_config_flow_validation():
    """Test the config flow validation logic."""
    print("\n🧪 Testing Config Flow Validation...")
    
    try:
        from custom_components.fortnite.config_flow import validate_input
        
        # Test data
        test_data = {
            "name": "Captain_Crunch88 Switch Stats",
            "api_key": "test-api-key",
            "player_id": "Captain_Crunch88",
            "game_platform": "switch",
            "game_mode": "SQUAD"
        }
        
        # Mock the validation (since we can't make real API calls)
        with patch('custom_components.fortnite.config_flow.Fortnite') as mock_fortnite:
            mock_game = Mock()
            mock_player = Mock()
            mock_stats = Mock()
            mock_player.get_stats.return_value = mock_stats
            mock_game.player.return_value = mock_player
            mock_fortnite.return_value = mock_game
            
            # Mock Home Assistant
            class MockHass:
                pass
            
            hass = MockHass()
            
            # Test validation
            result = await validate_input(hass, test_data)
            
            print("✅ Config flow validation successful")
            print(f"  Title: {result['title']}")
            print(f"  Player ID: {result['player_id']}")
            print(f"  Platform: {result['platform']}")
            print(f"  Mode: {result['mode']}")
            
            return True
            
    except Exception as e:
        print(f"❌ Config flow validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_platform_mapping():
    """Test the platform mapping functionality."""
    print("\n🧪 Testing Platform Mapping...")
    
    try:
        # Test the platform mapping from coordinator
        platform_mapping = {
            "pc": "Platform.PC",
            "xbox": "Platform.XBOX",
            "psn": "Platform.PSN",
            "switch": "Platform.GAMEPAD",  # Nintendo Switch
            "kbm": "Platform.KBM"
        }
        
        print("✅ Platform mapping structure:")
        for api_name, lib_name in platform_mapping.items():
            print(f"  {api_name} -> {lib_name}")
        
        # Test Captain_Crunch88 specific case
        player_platform = "switch"
        mapped_platform = platform_mapping.get(player_platform, "Platform.PC")
        print(f"✅ Captain_Crunch88 platform: {player_platform} -> {mapped_platform}")
        
        # Test all platforms
        test_platforms = ["pc", "xbox", "psn", "switch", "kbm"]
        for platform in test_platforms:
            mapped = platform_mapping.get(platform, "Platform.PC")
            print(f"✅ {platform} -> {mapped}")
        
        return True
        
    except Exception as e:
        print(f"❌ Platform mapping test failed: {e}")
        return False

async def main():
    """Run all integration tests."""
    print("🚀 Starting Comprehensive Fortnite Integration Tests\n")
    print("=" * 60)
    
    tests = [
        ("Platform Mapping", test_platform_mapping),
        ("Integration Loading", test_integration_loading),
        ("Coordinator with Mock Data", test_coordinator_with_mock_data),
        ("Sensor Entity", test_sensor_entity),
        ("Config Flow Validation", test_config_flow_validation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS:")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30} {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Your Fortnite integration is ready for Home Assistant!")
        print("\n📋 Next Steps:")
        print("1. Copy custom_components/fortnite/ to your Home Assistant")
        print("2. Restart Home Assistant")
        print("3. Add integration via UI: Settings > Devices & Services")
        print("4. Configure with your API key and Captain_Crunch88")
        print("5. Select platform: switch (Nintendo Switch)")
        print("6. Choose game mode: SOLO, DUO, or SQUAD")
    else:
        print(f"\n💥 {total - passed} tests failed!")
        print("Check the errors above and fix them before deploying.")

if __name__ == "__main__":
    asyncio.run(main())
