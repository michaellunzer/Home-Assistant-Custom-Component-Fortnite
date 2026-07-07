"""Constants for the Fortnite Stats integration."""

DOMAIN = "fortnite"

# Configuration keys
CONF_API_KEY = "api_key"
CONF_PLAYER_ID = "player_id"
CONF_AGGREGATED_SENSORS = "aggregated_sensors"

# fortnite-api.com endpoint
API_STATS_URL = "https://fortnite-api.com/v2/stats/br/v2"

# Update every 5 minutes
DEFAULT_SCAN_INTERVAL = 300

# Input-type blocks returned by fortnite-api.com.
# "all" is the combined lifetime block (matches fortnitetracker.com and the
# raw API "overall" numbers users compare against).
API_PLATFORMS = ["all", "gamepad", "keyboardMouse"]
PLATFORM_DISPLAY_NAMES = {
    "all": "All Inputs",
    "gamepad": "Console",
    "keyboardMouse": "PC",
}

# Game-mode blocks returned by the API. "overall" includes LTM and other
# modes that solo/duo/squad alone do not cover.
API_GAME_MODES = ["overall", "solo", "duo", "squad"]

# Aggregated sensor types (locally computed sums over solo+duo+squad on
# gamepad+keyboardMouse, kept for backward compatibility with v2.0.x)
AGGREGATED_SENSOR_TYPES = {
    "all_platforms_all_modes": "All Platforms All Modes",
    "console_all_modes": "Console All Modes",
    "pc_all_modes": "PC All Modes",
    "all_platforms_solo": "All Platforms Solo",
    "all_platforms_duo": "All Platforms Duo",
    "all_platforms_squad": "All Platforms Squad",
}
