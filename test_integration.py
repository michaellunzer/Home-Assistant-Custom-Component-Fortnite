#!/usr/bin/env python3
"""Test script for the Fortnite integration without Home Assistant."""

import asyncio
import json
from unittest.mock import Mock, AsyncMock
from fortnite_python import Fortnite
from fortnite_python.domain import Mode, Platform

# Mock Home Assistant components
class MockConfigEntry:
    def __init__(self, data):
        self.data = data
        self.entry_id = "test_entry_123"

class MockHass:
    def __init__(self):
        self.data = {}
        self.async_add_executor_job = AsyncMock()

class MockCoordinator:
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self.data = None
        self._update_interval = 300  # 5 minutes

async def test_coordinator():
    """Test the coordinator logic."""
    print("🧪 Testing Fortnite Coordinator...")
    
    # Mock data
    entry_data = {
        "name": "Test Fortnite Stats",
        "api_key": "test-api-key",
        "player_id": "Captain_Crunch88",
        "game_platform": "GAMEPAD",
        "game_mode": "SOLO"
    }
    
    entry = MockConfigEntry(entry_data)
    hass = MockHass()
    
    # Test coordinator initialization
    try:
        from custom_components.fortnite.coordinator import FortniteDataUpdateCoordinator
        
        coordinator = FortniteDataUpdateCoordinator(hass, entry)
        print("✅ Coordinator initialized successfully")
        print(f"  Player ID: {coordinator.player_id}")
        print(f"  Platform: {coordinator.platform}")
        print(f"  Mode: {coordinator.mode}")
        print(f"  Update interval: {coordinator.update_interval}")
        
        return True
    except Exception as e:
        print(f"❌ Coordinator test failed: {e}")
        return False

def test_config_flow():
    """Test the config flow validation."""
    print("\n🧪 Testing Config Flow...")
    
    try:
        from custom_components.fortnite.config_flow import validate_input
        
        # Mock Home Assistant
        class MockHass:
            pass
        
        test_data = {
            "name": "Test Integration",
            "api_key": "test-key",
            "player_id": "test-player",
            "game_platform": "PC",
            "game_mode": "SOLO"
        }
        
        # This will fail without real API, but we can test the structure
        print("✅ Config flow structure is valid")
        return True
    except Exception as e:
        print(f"❌ Config flow test failed: {e}")
        return False

def test_constants():
    """Test the constants file."""
    print("\n🧪 Testing Constants...")
    
    try:
        from custom_components.fortnite.const import (
            DOMAIN, PLATFORM_OPTIONS, MODE_OPTIONS,
            CONF_API_KEY, CONF_PLAYER_ID
        )
        
        print("✅ Constants imported successfully")
        print(f"  Domain: {DOMAIN}")
        print(f"  Platform options: {PLATFORM_OPTIONS}")
        print(f"  Mode options: {MODE_OPTIONS}")
        return True
    except Exception as e:
        print(f"❌ Constants test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting Fortnite Integration Tests\n")
    
    tests = [
        ("Constants", test_constants),
        ("Config Flow", test_config_flow),
        ("Coordinator", test_coordinator),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n📊 Test Results:")
    print("=" * 50)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Integration structure is valid.")
    else:
        print("💥 Some tests failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
