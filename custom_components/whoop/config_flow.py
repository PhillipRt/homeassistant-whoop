"""Config flow for Whoop."""
import logging
import voluptuous as vol
from homeassistant import config_entries, core, exceptions
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN

class OAuth2FlowHandler(config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN):
    """Provide a config flow for OAuth2."""

    DOMAIN = DOMAIN
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)

    async def async_step_user(self, user_input=None):
        """Handle a flow start."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["client_id"],
                data={
                    "client_id": user_input["client_id"],
                    "client_secret": user_input["client_secret"]
                }
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("client_id"): str,
                    vol.Required("client_secret"): str,
                }
            ),
            errors=errors,
        )

    async def async_step_creation(self, user_input=None):
        """Handle a flow start."""
        if user_input is not None:
            return self.async_external_step_done(user_input)

        return await super().async_step_creation(user_input)

    async def async_oauth_create_entry(self, data: dict) -> dict:
        """Create an entry for the flow."""
        return self.async_create_entry(title=self.flow_impl.name, data=data)

    async def async_get_access_token(self) -> str:
        """Return a valid access token."""
        auth_implementation = self.hass.helpers.application_credentials.async_get_auth_implementation(DOMAIN)
        return await auth_implementation.async_get_access_token()
