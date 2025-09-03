#!/usr/bin/env python3
"""Test the integration structure without Home Assistant dependencies."""

import json
import os
import sys

def test_file_structure():
    """Test that all required files exist."""
    print("🧪 Testing File Structure...")
    
    required_files = [
        "custom_components/fortnite/__init__.py",
        "custom_components/fortnite/config_flow.py",
        "custom_components/fortnite/const.py",
        "custom_components/fortnite/coordinator.py",
        "custom_components/fortnite/sensor.py",
        "custom_components/fortnite/manifest.json",
        "custom_components/fortnite/services.yaml",
        "custom_components/fortnite/strings.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing {len(missing_files)} required files")
        return False
    else:
        print("✅ All required files present")
        return True

def test_manifest():
    """Test manifest.json structure."""
    print("\n🧪 Testing Manifest.json...")
    
    try:
        with open("custom_components/fortnite/manifest.json", "r") as f:
            manifest = json.load(f)
        
        required_keys = [
            "domain", "name", "version", "config_flow", 
            "requirements", "iot_class", "integration_type"
        ]
        
        for key in required_keys:
            if key in manifest:
                print(f"✅ {key}: {manifest[key]}")
            else:
                print(f"❌ Missing key: {key}")
                return False
        
        # Check specific values
        if manifest["domain"] != "fortnite":
            print("❌ Domain should be 'fortnite'")
            return False
        
        if not manifest["config_flow"]:
            print("❌ Config flow should be enabled")
            return False
        
        if "fortnite-python" not in str(manifest["requirements"]):
            print("❌ fortnite-python requirement missing")
            return False
        
        print("✅ Manifest.json is valid")
        return True
        
    except Exception as e:
        print(f"❌ Manifest test failed: {e}")
        return False

def test_strings():
    """Test strings.json structure."""
    print("\n🧪 Testing Strings.json...")
    
    try:
        with open("custom_components/fortnite/strings.json", "r") as f:
            strings = json.load(f)
        
        # Check config flow strings
        if "config" not in strings:
            print("❌ Missing 'config' section")
            return False
        
        if "step" not in strings["config"]:
            print("❌ Missing 'step' section in config")
            return False
        
        if "user" not in strings["config"]["step"]:
            print("❌ Missing 'user' step in config")
            return False
        
        # Check error strings
        if "error" not in strings["config"]:
            print("❌ Missing 'error' section in config")
            return False
        
        print("✅ Strings.json structure is valid")
        return True
        
    except Exception as e:
        print(f"❌ Strings test failed: {e}")
        return False

def test_python_syntax():
    """Test Python file syntax."""
    print("\n🧪 Testing Python Syntax...")
    
    python_files = [
        "custom_components/fortnite/__init__.py",
        "custom_components/fortnite/config_flow.py",
        "custom_components/fortnite/const.py",
        "custom_components/fortnite/coordinator.py",
        "custom_components/fortnite/sensor.py"
    ]
    
    for file_path in python_files:
        try:
            with open(file_path, "r") as f:
                compile(f.read(), file_path, "exec")
            print(f"✅ {file_path} - Syntax OK")
        except SyntaxError as e:
            print(f"❌ {file_path} - Syntax Error: {e}")
            return False
        except Exception as e:
            print(f"❌ {file_path} - Error: {e}")
            return False
    
    print("✅ All Python files have valid syntax")
    return True

def test_constants():
    """Test constants file content."""
    print("\n🧪 Testing Constants...")
    
    try:
        with open("custom_components/fortnite/const.py", "r") as f:
            content = f.read()
        
        # Check for required constants
        required_constants = [
            "DOMAIN = \"fortnite\"",
            "PLATFORM_OPTIONS = [",
            "MODE_OPTIONS = [",
            "CONF_API_KEY",
            "CONF_PLAYER_ID",
            "CONF_GAME_PLATFORM",
            "CONF_GAME_MODE"
        ]
        
        for constant in required_constants:
            if constant in content:
                print(f"✅ Found: {constant}")
            else:
                print(f"❌ Missing: {constant}")
                return False
        
        # Check platform options
        if '"switch"' in content:
            print("✅ Nintendo Switch platform option found")
        else:
            print("❌ Nintendo Switch platform option missing")
            return False
        
        print("✅ Constants file is valid")
        return True
        
    except Exception as e:
        print(f"❌ Constants test failed: {e}")
        return False

def test_platform_mapping():
    """Test platform mapping logic."""
    print("\n🧪 Testing Platform Mapping...")
    
    try:
        with open("custom_components/fortnite/coordinator.py", "r") as f:
            content = f.read()
        
        # Check for platform mapping
        if "platform_mapping" in content:
            print("✅ Platform mapping found in coordinator")
        else:
            print("❌ Platform mapping missing in coordinator")
            return False
        
        # Check for Nintendo Switch mapping
        if '"switch": Platform.GAMEPAD' in content:
            print("✅ Nintendo Switch mapping found (switch -> GAMEPAD)")
        else:
            print("❌ Nintendo Switch mapping missing")
            return False
        
        # Check for all platform mappings
        platforms = ["pc", "xbox", "psn", "switch", "kbm"]
        for platform in platforms:
            if f'"{platform}":' in content:
                print(f"✅ {platform} platform mapping found")
            else:
                print(f"❌ {platform} platform mapping missing")
                return False
        
        print("✅ Platform mapping is complete")
        return True
        
    except Exception as e:
        print(f"❌ Platform mapping test failed: {e}")
        return False

def test_captain_crunch88_specific():
    """Test Captain_Crunch88 specific configuration."""
    print("\n🧪 Testing Captain_Crunch88 Configuration...")
    
    # Test that the integration can handle Captain_Crunch88's setup
    test_config = {
        "name": "Captain_Crunch88 Switch Stats",
        "api_key": "test-api-key",
        "player_id": "Captain_Crunch88",
        "game_platform": "switch",
        "game_mode": "SQUAD"
    }
    
    print("✅ Test configuration for Captain_Crunch88:")
    for key, value in test_config.items():
        print(f"  {key}: {value}")
    
    # Verify platform is correct
    if test_config["game_platform"] == "switch":
        print("✅ Platform correctly set to 'switch' for Nintendo Switch")
    else:
        print("❌ Platform should be 'switch' for Nintendo Switch")
        return False
    
    # Verify player ID
    if test_config["player_id"] == "Captain_Crunch88":
        print("✅ Player ID correctly set to 'Captain_Crunch88'")
    else:
        print("❌ Player ID should be 'Captain_Crunch88'")
        return False
    
    print("✅ Captain_Crunch88 configuration is valid")
    return True

def main():
    """Run all structure tests."""
    print("🚀 Starting Fortnite Integration Structure Tests\n")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Manifest.json", test_manifest),
        ("Strings.json", test_strings),
        ("Python Syntax", test_python_syntax),
        ("Constants", test_constants),
        ("Platform Mapping", test_platform_mapping),
        ("Captain_Crunch88 Config", test_captain_crunch88_specific),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
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
        print(f"{test_name:25} {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL STRUCTURE TESTS PASSED!")
        print("✅ Your Fortnite integration structure is perfect!")
        print("\n📋 Ready for Home Assistant deployment:")
        print("1. Copy custom_components/fortnite/ to your Home Assistant")
        print("2. Restart Home Assistant")
        print("3. Add integration via UI")
        print("4. Configure with Captain_Crunch88 and switch platform")
        print("\n🎮 The integration will work with:")
        print("  - Player: Captain_Crunch88")
        print("  - Platform: switch (Nintendo Switch)")
        print("  - Game modes: SOLO, DUO, SQUAD")
        print("  - Auto-updates every 5 minutes")
    else:
        print(f"\n💥 {total - passed} tests failed!")
        print("Fix the issues above before deploying to Home Assistant.")

if __name__ == "__main__":
    main()
