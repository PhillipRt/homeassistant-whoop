"""The Whoop integration."""
import asyncio
import aiohttp
import logging
import base64
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
        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self.token_url = "https://api.prod.whoop.com/oauth/oauth2/token"
        self.refresh_token = config.get("refresh_token")

    async def get_data(self, endpoint):
        """Retrieve data from the Whoop API."""
        access_token = await self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"https://api.prod.whoop.com/{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                return data

    async def get_access_token(self):
        """Retrieve access token using refresh token."""
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "offline"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.token_url, data=payload) as resp:
                data = await resp.json()
                return data["access_token"]
