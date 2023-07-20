from homeassistant.helpers import config_entry_oauth2_flow, network
from aiohttp import ClientSession
from typing import Any

class WhoopOAuth2Implementation(config_entry_oauth2_flow.AbstractOAuth2Implementation):
    def __init__(self, hass, client_id, client_secret):
        self.hass = hass
        self._client_id = client_id
        self._client_secret = client_secret
        self.session = ClientSession()

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def client_secret(self) -> str:
        return self._client_secret


    @property
    def name(self) -> str:
        return "Whoop"

    @property
    def redirect_uri(self) -> str:
        """Return the redirect uri."""
        return f"{network.async_get_url(self.hass)}/auth/external/callback"

    async def async_generate_authorize_url(self, flow_id: str) -> str:
        return f"https://api.prod.whoop.com/oauth/oauth2/auth?response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri}&state={flow_id}"

    async def async_resolve_external_data(self, external_data: Any) -> dict:
        code = external_data.get('code')
        return await self.async_get_token(code)

    async def _async_refresh_token(self, token: dict) -> dict:
        refresh_token = token['refresh_token']
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "offline"
        }
        url = "https://api.prod.whoop.com/oauth/oauth2/token"
        async with self.session.post(url, data=payload) as response:
            return await response.json()

    async def async_get_token(self, code: str) -> dict:
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri
        }
        url = "https://api.prod.whoop.com/oauth/oauth2/token"
        async with self.session.post(url, data=payload) as response:
            return await response.json()
