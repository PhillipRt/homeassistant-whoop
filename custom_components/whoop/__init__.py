"""The Whoop integration."""
import asyncio
import aiohttp
import logging
import requests

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
PLATFORMS = ["sensor"]

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
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok



class WhoopApiClient:
    """Class to communicate with the Whoop API."""

    def __init__(self, config):
        """Initialize the Whoop API client."""
        self.access_token = config["access_token"]


    async def get_data(self, endpoint):
        """Retrieve data from the Whoop API."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"https://api.prod.whoop.com/{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                return data

    