"""Constants for the Fortnite Stats integration."""

DOMAIN = "fortnite"

# Configuration keys
CONF_API_KEY = "api_key"
CONF_PLAYER_ID = "player_id"
CONF_GAME_PLATFORM = "game_platform"
CONF_GAME_MODE = "game_mode"
CONF_AGGREGATED_SENSORS = "aggregated_sensors"

# Default values
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes
DEFAULT_PLATFORM = "pc"
DEFAULT_MODE = "SOLO"

# Platform options (FortniteAPI.io identifiers)
PLATFORM_OPTIONS = [
    "pc",
    "xbox", 
    "psn",
    "gamepad",  # Nintendo Switch uses "gamepad" in FortniteAPI.io
    "kbm"
]

# Game mode options
MODE_OPTIONS = [
    "SOLO",
    "DUO", 
    "SQUAD"
]

# Aggregated sensor types
AGGREGATED_SENSOR_TYPES = {
    "all_platforms_all_modes": "All Platforms All Modes",
    "console_all_modes": "Console All Modes", 
    "pc_all_modes": "PC All Modes",
    "all_platforms_solo": "All Platforms Solo",
    "all_platforms_duo": "All Platforms Duo",
    "all_platforms_squad": "All Platforms Squad"
}
