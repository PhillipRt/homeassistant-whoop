from aiohttp import ClientSession
from . import WhoopOAuth2Implementation
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
import logging

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Whoop component."""
    auth_implementation = obtain_whoop_auth_from_config(hass, config)
    _LOGGER = logging.getLogger(__name__)
    if auth_implementation is None:
        _LOGGER.error("Unable to obtain Whoop authenticate implementation")
        return False

    # Continue with your setup...
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, config: dict):
    """Set up Whoop from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = WhoopApiClient(hass, entry.data, obtain_whoop_auth_from_config(hass, config))
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

def obtain_whoop_auth_from_config(hass: HomeAssistant, config: dict):
        client_id = config.get("client_id")
        client_secret = config.get("client_secret")

        if client_id is None or client_secret is None:
            return None

        return WhoopOAuth2Implementation(hass, client_id, client_secret)

class WhoopApiClient:
    def __init__(self, hass, config, auth):
        self.hass = hass
        self.config = config
        self.websession = ClientSession()
        self.auth = auth

    async def get_data(self, path):
        access_token = await self.auth.async_get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"https://api.prod.whoop.com/developer/v1/{path}"
        async with self.websession.get(url, headers=headers) as response:
            return await response.json()
