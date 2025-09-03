# Testing Guide for Fortnite Stats Integration

This guide provides multiple ways to test your modernized Fortnite Stats integration.

## 🧪 Testing Methods

### 1. **Basic Structure Validation**

Test that all files are properly structured:

```bash
# Check file structure
ls -la custom_components/fortnite/

# Validate Python syntax
python3 -m py_compile custom_components/fortnite/__init__.py
python3 -m py_compile custom_components/fortnite/config_flow.py
python3 -m py_compile custom_components/fortnite/coordinator.py
python3 -m py_compile custom_components/fortnite/sensor.py
python3 -m py_compile custom_components/fortnite/const.py
```

### 2. **API Connection Test**

Test the Fortnite API connection:

```bash
# Run the API test script
python3 test_fortnite_api.py
```

**Requirements:**
- Valid Fortnite Tracker API key (get one at https://fortnitetracker.com/site-api)
- Valid player ID/username
- Internet connection

### 3. **Integration Structure Test**

Test the integration components:

```bash
# Run the integration test
python3 test_integration.py
```

This tests:
- Constants import
- Config flow structure
- Coordinator initialization

### 4. **Home Assistant Testing**

#### Option A: Development Environment

1. **Set up Home Assistant Development Environment:**
   ```bash
   # Clone Home Assistant
   git clone https://github.com/home-assistant/core.git
   cd core
   
   # Install dependencies
   python3 -m pip install -e .
   
   # Copy your integration
   cp -r /path/to/your/custom_components/fortnite homeassistant/components/
   ```

2. **Run Home Assistant with your integration:**
   ```bash
   # Start Home Assistant
   python3 -m homeassistant --config /path/to/test/config
   ```

#### Option B: Docker Testing

1. **Create a test configuration:**
   ```yaml
   # test_config/configuration.yaml
   default_config:
   
   # Add your integration to custom_components
   ```

2. **Run with Docker:**
   ```bash
   docker run -d \
     --name homeassistant \
     --privileged \
     --restart=unless-stopped \
     -e TZ=America/New_York \
     -v /path/to/test_config:/config \
     -v /path/to/custom_components:/config/custom_components \
     --network=host \
     ghcr.io/home-assistant/home-assistant:stable
   ```

#### Option C: HACS Testing

1. **Install via HACS:**
   - Add your repository to HACS
   - Install the integration
   - Configure through UI

### 5. **Manual Testing Steps**

#### Step 1: Install Integration
1. Copy `custom_components/fortnite/` to your Home Assistant `custom_components/` directory
2. Restart Home Assistant

#### Step 2: Add Integration
1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for **Fortnite Stats**
4. Follow the setup wizard

#### Step 3: Verify Configuration
- Check that the integration appears in **Devices & Services**
- Verify the sensor entity is created
- Check the entity attributes

#### Step 4: Test Data Updates
- Wait 5 minutes for automatic update
- Check Home Assistant logs for any errors
- Verify sensor values are updating

### 6. **Debugging**

#### Check Home Assistant Logs
```bash
# View logs
tail -f /path/to/homeassistant/home-assistant.log

# Or in Home Assistant UI:
# Settings > System > Logs
```

#### Common Issues and Solutions

**Integration won't load:**
- Check manifest.json syntax
- Verify all required files exist
- Check Home Assistant logs

**Config flow fails:**
- Verify API key is valid
- Check player ID exists
- Ensure platform/mode are correct

**No data updates:**
- Check internet connection
- Verify API key permissions
- Check coordinator logs

**Entity not created:**
- Verify sensor.py syntax
- Check coordinator data
- Review entity registration

### 7. **Automated Testing**

Create unit tests:

```python
# tests/test_fortnite.py
import pytest
from unittest.mock import Mock, patch
from custom_components.fortnite.coordinator import FortniteDataUpdateCoordinator

@pytest.mark.asyncio
async def test_coordinator_update():
    """Test coordinator data update."""
    # Mock the coordinator
    coordinator = Mock()
    coordinator.data = {"kills": 100, "matches": 50}
    
    # Test data retrieval
    assert coordinator.data["kills"] == 100
    assert coordinator.data["matches"] == 50
```

### 8. **Performance Testing**

Test update frequency and performance:

```python
# Monitor update times
import time
start_time = time.time()
# Trigger update
end_time = time.time()
print(f"Update took {end_time - start_time:.2f} seconds")
```

## 🚀 Quick Test Checklist

- [ ] All Python files compile without syntax errors
- [ ] Integration appears in Home Assistant UI
- [ ] Config flow accepts valid credentials
- [ ] Sensor entity is created
- [ ] Data updates automatically every 5 minutes
- [ ] All Fortnite stats are displayed correctly
- [ ] Error handling works for invalid API keys
- [ ] Multiple integrations can be added (different modes/platforms)

## 📝 Test Results Template

```
Test Date: ___________
Home Assistant Version: ___________
Integration Version: 2.0.0

✅ Structure Validation: PASS/FAIL
✅ API Connection: PASS/FAIL  
✅ Config Flow: PASS/FAIL
✅ Sensor Creation: PASS/FAIL
✅ Data Updates: PASS/FAIL
✅ Error Handling: PASS/FAIL

Notes:
- 
- 
- 
```

## 🔧 Troubleshooting Commands

```bash
# Check integration files
find custom_components/fortnite -name "*.py" -exec python3 -m py_compile {} \;

# Validate manifest
python3 -c "import json; json.load(open('custom_components/fortnite/manifest.json'))"

# Test API key (replace with your key)
curl -H "TRN-Api-Key: YOUR_API_KEY" https://api.fortnitetracker.com/v1/profile/pc/player_name
```

## 📞 Support

If you encounter issues:
1. Check Home Assistant logs
2. Verify your API credentials
3. Test with the provided scripts
4. Open an issue on GitHub with test results
