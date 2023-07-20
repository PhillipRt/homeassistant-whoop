"""Platform for Whoop sensor integration."""
from datetime import timedelta
from . import WhoopApiClient
import requests
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC

from .const import DOMAIN
SCAN_INTERVAL = timedelta(minutes=10)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Whoop sensor platform."""
    config = {"access_token": config_entry.data["access_token"]}
    api = WhoopApiClient(config)
    sensors = []

    # Create a sensor for each data point we want to track
    for path, name, unit, attributes in [
        ("cycle", "Strain", "strain", [
         "kilojoule", "average_heart_rate", "max_heart_rate"]),
        ("recovery", "Recovery Score", "recovery_score", [
         "resting_heart_rate", "hrv_rmssd_milli", "spo2_percentage", "skin_temp_celsius"]),
        ("sleep", "Sleep Performance", "sleep_performance_percentage", [
         "sleep_consistency_percentage", "sleep_efficiency_percentage", "respiratory_rate"]),
        ("workout", "Workout Strain", "strain", ["average_heart_rate", "max_heart_rate",
         "kilojoule", "distance_meter", "altitude_gain_meter", "altitude_change_meter"]),
        # TODO: Add more data points here
    ]:
        sensors.append(WhoopSensor(api, name, unit, path, attributes))

    # Create a Whoop device based on the User data
    user_data = api.get_data("user")
    device = WhoopDevice(user_data)
    sensors.append(device)

    async_add_entities(sensors, True)


class WhoopSensor(Entity):
    """Representation of a Whoop sensor."""

    def __init__(self, api, name, unit, path, attributes):
        """Initialize the Whoop sensor."""
        self._api = api
        self._name = name
        self._unit = unit
        self._path = path
        self._attributes = attributes
        self._state = None
        self._state_attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._state_attributes

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            data = await self._api.get_data(self._path)
        except requests.HTTPError as ex:
            if ex.response.status_code == 401:  # Unauthorized
                # Refresh the access token
                home_assistant = self.hass
                oauth2_impl = home_assistant.helpers.application_credentials.async_get_auth_implementation(
                    DOMAIN)
                new_token = await oauth2_impl.refresh_token(self._api.access_token)
                # Update the WhoopApiClient with the new access token
                self._api.access_token = new_token
                # Retry the request
                data = await self._api.get_data(self._path)
            else:
                raise

        self._state = data.get(self._unit)  # Extract the state from the data

        # Extract the state attributes from the data
        for attribute in self._attributes:
            self._state_attributes[attribute] = data.get(attribute)



class WhoopDevice(Entity):
    """Representation of a Whoop device."""

    def __init__(self, data):
        """Initialize the Whoop device."""
        self._name = data["email"]
        self._state = "connected"
        self._attributes = {
            "height": data["height"],
            "weight": data["weight"],
            "max_heart_rate": data["max_heart_rate"],
        }

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._state_attributes

    @property
    def device_info(self):
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._name)},
            name=self._name,
            manufacturer="Whoop",
            model="Whoop Strap 4.0",
            sw_version="1.0",
        )
