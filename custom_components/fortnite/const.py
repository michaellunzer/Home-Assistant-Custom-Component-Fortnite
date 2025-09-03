"""Constants for the Fortnite Stats integration."""

DOMAIN = "fortnite"

# Configuration keys
CONF_API_KEY = "api_key"
CONF_PLAYER_ID = "player_id"
CONF_GAME_PLATFORM = "game_platform"
CONF_GAME_MODE = "game_mode"

# Default values
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes
DEFAULT_PLATFORM = "pc"
DEFAULT_MODE = "SOLO"

# Platform options (Fortnite Tracker API identifiers)
PLATFORM_OPTIONS = [
    "pc",
    "xbox", 
    "psn",
    "switch",
    "kbm"
]

# Game mode options
MODE_OPTIONS = [
    "SOLO",
    "DUO", 
    "SQUAD"
]
