# Manual Home Assistant Integration Testing Guide

## 🚀 Quick Setup

1. **Start Docker Desktop** (if not already running)
2. **Run the setup script:**
   ```bash
   ./setup_ha_test.sh
   ```
3. **Start Home Assistant:**
   ```bash
   cd ha_test
   docker-compose up -d
   ```
4. **Open Home Assistant:**
   - Go to http://localhost:8123
   - Complete the initial setup (create admin account)

## 🧪 Testing the Fortnite Integration

### Step 1: Add the Integration
1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **"Fortnite Stats"**
4. Click on it to start the setup

### Step 2: Configure the Integration
Fill in the configuration form:

- **Integration Name**: `Captain_Crunch88 Switch Stats`
- **API Key**: `ea1b5a95-662b-4fce-be79-eb7f46344e55`
- **Player ID**: `Captain_Crunch88`
- **Platform**: `switch` (Nintendo Switch)
- **Game Mode**: `SQUAD` (or SOLO/DUO)

### Step 3: Verify the Integration
1. Check that the integration appears in **Devices & Services**
2. Look for the sensor entity in **Settings** → **Entities**
3. Search for `sensor.captain_crunch88_switch_stats`

### Step 4: Check the Sensor Data
1. Go to **Overview** (main dashboard)
2. Add the sensor to a card
3. Verify the following data is displayed:
   - **State**: Number of kills
   - **Unit**: eliminations
   - **Attributes**: All Fortnite stats (top1, top3, kills, kd, etc.)

### Step 5: Test Data Updates
1. Wait 5 minutes for automatic update
2. Check Home Assistant logs: `docker-compose logs -f homeassistant`
3. Look for Fortnite API calls and data updates

## 🔍 Expected Results

### ✅ Success Indicators:
- Integration loads without errors
- Sensor entity is created with correct name
- Data is displayed (kills, matches, win ratio, etc.)
- Automatic updates work every 5 minutes
- No error messages in logs

### ❌ Troubleshooting:
- **Integration won't load**: Check manifest.json and file structure
- **Config flow fails**: Verify API key and player ID
- **No data**: Check internet connection and API key permissions
- **Entity not created**: Check sensor.py and coordinator

## 📊 Test Multiple Configurations

Create additional integrations for different game modes:

1. **Solo Mode**: `Captain_Crunch88 Solo Stats`
2. **Duo Mode**: `Captain_Crunch88 Duo Stats`
3. **Squad Mode**: `Captain_Crunch88 Squad Stats`

Each should create a separate sensor entity.

## 🐛 Debugging Commands

```bash
# View Home Assistant logs
docker-compose logs -f homeassistant

# Check integration files
ls -la config/custom_components/fortnite/

# Restart Home Assistant
docker-compose restart

# Stop and clean up
docker-compose down
```

## 📝 Test Checklist

- [ ] Integration appears in Devices & Services
- [ ] Config flow accepts credentials
- [ ] Sensor entity is created
- [ ] Data is displayed correctly
- [ ] Automatic updates work
- [ ] Multiple integrations can be added
- [ ] No errors in logs
- [ ] Platform mapping works (switch → GAMEPAD)

## 🎯 Success Criteria

The integration is working correctly if:
1. ✅ All checklist items are checked
2. ✅ Captain_Crunch88's Nintendo Switch stats are displayed
3. ✅ Data updates automatically every 5 minutes
4. ✅ No error messages in Home Assistant logs
5. ✅ Multiple game modes can be configured separately

## 🚀 Next Steps

Once testing is complete:
1. Commit the changes to your repository
2. Create a pull request
3. Update HACS repository
4. Publish the new version

The integration is ready for production use!
