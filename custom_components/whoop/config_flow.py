"""Config flow for Whoop."""
import logging
import voluptuous as vol
from homeassistant import config_entries, core, exceptions
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN

class OAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    DOMAIN = DOMAIN
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    @property
    def logger(self):
        """Return logger."""
        return logging.getLogger(__name__)

    async def async_step_user(self, user_input=None):
        """Handle a flow start."""
        if self.hass.config_entries.async_entries(DOMAIN):
            return self.async_abort(reason="single_instance_allowed")

        return await self.async_step_discovery(user_input)

    async def async_step_discovery(self, user_input=None):
        """Handle redirection to Whoop website for OAuth2 flow."""
        return await self.async_step_auth()

    async def async_step_auth(self, user_input=None):
        """Handle redirection back from Whoop website after user's approval."""
        return await self.async_step_code(user_input)

    async def async_step_code(self, user_input=None):
        """Handle the reception of the authorization code from Whoop."""
        if user_input is None:
            return self.async_external_step_done(next_step_id="creation")

        return await self.async_step_creation(user_input)

    async def async_step_creation(self, user_input=None, error=None):
        """Handle callback from Whoop API."""
        if user_input is None:
            return self.async_external_step_done(next_step_id="creation")

        return await self.async_oauth_create_entry(user_input)
