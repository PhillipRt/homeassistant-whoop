from aiohttp import ClientSession
from homeassistant.helpers import application_credentials
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Whoop component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Whoop from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = WhoopApiClient(hass, entry.data)
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
    def __init__(self, hass, config):
        self.hass = hass
        self.config = config
        self.websession = ClientSession()
        self.auth = application_credentials.async_get_auth_implementation("whoop")

    async def get_data(self, path):
        access_token = await self.auth.async_get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"https://api.prod.whoop.com/developer/v1/{path}"
        async with self.websession.get(url, headers=headers) as response:
            return await response.json()
