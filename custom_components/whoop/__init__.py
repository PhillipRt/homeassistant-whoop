"""The Whoop integration."""
import logging
import requests

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Whoop component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Whoop from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = WhoopApiClient(entry.data)
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    hass.config_entries.async_forward_entry_unload(entry, "sensor")
    del hass.data[DOMAIN][entry.entry_id]
    return True

class WhoopApiClient:
    """Class to communicate with the Whoop API."""

    def __init__(self, config):
        """Initialize the Whoop API client."""
        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self._session = requests.Session()

    def get_data(self, endpoint):
        """Retrieve data from the Whoop API."""
        url = f"https://api-7.whoop.com/{endpoint}"
        response = self._session.get(url, auth=(self.client_id, self.client_secret))
        response.raise_for_status()
        return response.json()
