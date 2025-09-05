"""Mock config flow for testing without real API."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import PLATFORM_OPTIONS, MODE_OPTIONS

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("name"): str,
        vol.Required("api_key"): str,
        vol.Required("player_id"): str,
        vol.Required("game_platform"): vol.In(PLATFORM_OPTIONS),
        vol.Required("game_mode"): vol.In(MODE_OPTIONS),
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain="fortnite"):
    """Mock config flow that always succeeds for testing."""
    
    VERSION = 1
    
    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA
            )
        
        # Always succeed for mock testing
        return self.async_create_entry(
            title=user_input["name"],
            data=user_input
        )
