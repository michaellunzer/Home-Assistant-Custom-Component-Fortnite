"""The Fortnite Stats integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import FortniteDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]

FortniteConfigEntry = ConfigEntry[FortniteDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: FortniteConfigEntry) -> bool:
    """Set up Fortnite Stats from a config entry."""
    coordinator = FortniteDataUpdateCoordinator(hass, entry)

    # Fetch initial data so we have data when entities are added
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: FortniteConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
