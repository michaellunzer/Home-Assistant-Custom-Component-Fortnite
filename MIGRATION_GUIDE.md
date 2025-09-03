# Migration Guide: Fortnite Stats v1.x to v2.0

This guide will help you migrate from the old YAML-based configuration to the new modern Home Assistant integration.

## What's New in v2.0

- **Modern Integration Architecture**: Now uses the standard Home Assistant integration structure
- **Config Flow**: Set up through the UI instead of YAML configuration
- **Asynchronous**: Fully async implementation for better performance
- **Real-time Updates**: Automatic updates every 5 minutes (configurable)
- **Better Error Handling**: Improved error handling and logging
- **Unique Entity IDs**: Proper unique IDs for all entities

## Migration Steps

### 1. Remove Old Configuration

Remove the old YAML configuration from your `configuration.yaml`:

```yaml
# REMOVE THIS OLD CONFIGURATION
sensor:
  - platform: fortnite
    name: Fortnite Solo Stats
    api_key: 12345678-90ab-cdef-ghij-lmnopqrstuvw
    player_id: Captain_Crunch88
    game_platform: "GAMEPAD"
    game_mode: "SOLO"
```

### 2. Update the Integration

1. Update the integration through HACS or manually replace the files
2. Restart Home Assistant

### 3. Add New Integration

1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for **Fortnite Stats**
4. Follow the setup wizard:
   - Enter a name for your integration
   - Enter your Fortnite Tracker API key
   - Enter your player ID/username
   - Select your game platform
   - Select your game mode

### 4. Repeat for Multiple Configurations

If you had multiple sensors (different platforms/modes), you'll need to add separate integrations for each:

- One integration for Solo mode
- One integration for Duo mode  
- One integration for Squad mode
- Separate integrations for different platforms (PC, Xbox, etc.)

## Breaking Changes

- **YAML Configuration**: No longer supported - must use UI configuration
- **Entity Names**: May change due to new unique ID system
- **Update Frequency**: Now updates every 5 minutes instead of manual updates
- **Entity Structure**: Uses modern Home Assistant entity structure

## Troubleshooting

### Integration Won't Load
- Ensure you have a valid Fortnite Tracker API key
- Verify your player ID is correct
- Check the logs for specific error messages

### No Data Showing
- Wait a few minutes for the first update
- Check that your player has played the selected game mode recently
- Verify your platform selection matches where you play

### Multiple Platforms
- Create separate integrations for each platform you play on
- Each integration will create its own sensor entity

## Support

If you encounter issues during migration:
1. Check the Home Assistant logs
2. Verify your API key and player ID
3. Open an issue on the GitHub repository

## Rollback

If you need to rollback to the old version:
1. Restore the old files from backup
2. Add the YAML configuration back
3. Restart Home Assistant

**Note**: The old version is not compatible with newer Home Assistant versions and may not work properly.
