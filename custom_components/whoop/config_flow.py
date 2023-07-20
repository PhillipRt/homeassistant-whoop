"""Config flow for Whoop."""
import voluptuous as vol
from homeassistant import config_entries, core, exceptions
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN


class OAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Config flow to handle Whoop OAuth2 authentication."""

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

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required("client_id"): str,
                        vol.Required("client_secret"): str,
                    }
                ),
            )

        try:
            info = await validate_input(self.hass, user_input)
            return self.async_create_entry(title=info["title"], data=user_input)
        except CannotConnect:
            return self.async_abort(reason="cannot_connect")
        except InvalidAuth:
            return self.async_abort(reason="invalid_auth")
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            return self.async_abort(reason="unknown")

    async def async_step_creation(self, user_input=None):
        """Handle callback from Whoop API."""
        return await self.async_step_user()

async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect."""
    # TODO: validate the input
    return {"title": f"Whoop {data['client_id']}"}
