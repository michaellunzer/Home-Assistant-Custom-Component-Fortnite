"""Mock coordinator for testing without real API."""
import asyncio
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

# Mock data based on Captain_Crunch88's typical stats
MOCK_DATA = {
    "solo": {
        "kills": 150, "matches": 65, "win_ratio": 0.15, "kd": 1.5, "kpg": 2.3,
        "top1": 5, "top3": 12, "top5": 8, "top6": 3, "top10": 15,
        "top12": 7, "top25": 20, "score": 12500, "score_per_match": 192.3,
        "id": "captain_crunch88_solo"
    },
    "duo": {
        "kills": 200, "matches": 80, "win_ratio": 0.20, "kd": 1.8, "kpg": 2.5,
        "top1": 8, "top3": 15, "top5": 12, "top6": 5, "top10": 20,
        "top12": 10, "top25": 25, "score": 18000, "score_per_match": 225.0,
        "id": "captain_crunch88_duo"
    },
    "squad": {
        "kills": 300, "matches": 100, "win_ratio": 0.25, "kd": 2.0, "kpg": 3.0,
        "top1": 12, "top3": 20, "top5": 15, "top6": 8, "top10": 30,
        "top12": 15, "top25": 35, "score": 25000, "score_per_match": 250.0,
        "id": "captain_crunch88_squad"
    }
}

class FortniteDataUpdateCoordinator(DataUpdateCoordinator):
    """Mock coordinator that returns fake data for testing."""
    
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            None,  # logger
            name="fortnite_mock",
            update_interval=timedelta(seconds=300),  # 5 minutes
        )
        self.entry = entry
        self._update_count = 0
    
    async def _async_update_data(self):
        """Return mock data with some variation to simulate real updates."""
        mode = self.entry.data.get("game_mode", "SQUAD").lower()
        base_data = MOCK_DATA.get(mode, MOCK_DATA["squad"]).copy()
        
        # Add some variation to make it feel more realistic
        import random
        variation = random.uniform(0.95, 1.05)
        
        # Update some stats with variation
        base_data["kills"] = int(base_data["kills"] * variation)
        base_data["matches"] = int(base_data["matches"] * variation)
        base_data["score"] = int(base_data["score"] * variation)
        
        # Increment update count
        self._update_count += 1
        base_data["update_count"] = self._update_count
        base_data["last_update"] = asyncio.get_event_loop().time()
        
        return base_data
