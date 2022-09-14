from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant import core
from homeassistant import exceptions
from homeassistant.const import CONF_API_KEY
from homeassistant.const import CONF_NAME

from .const import CONF_DEVICETRACKER_ID
from .const import CONF_EXTENDED_ATTR
from .const import CONF_HOME_ZONE
from .const import CONF_LANGUAGE
from .const import CONF_MAP_PROVIDER
from .const import CONF_MAP_ZOOM
from .const import CONF_OPTIONS
from .const import DEFAULT_EXTENDED_ATTR
from .const import DEFAULT_HOME_ZONE
from .const import DEFAULT_MAP_PROVIDER
from .const import DEFAULT_MAP_ZOOM
from .const import DEFAULT_OPTION
from .const import DOMAIN  # pylint:disable=unused-import


_LOGGER = logging.getLogger(__name__)
MAP_PROVIDER_OPTIONS = ["apple", "google", "osm"]

# Note the input displayed to the user will be translated. See the
# translations/<lang>.json file and strings.json. See here for further information:
# https://developers.home-assistant.io/docs/config_entries_config_flow_handler/#translations
# At the time of writing I found the translations created by the scaffold didn't
# quite work as documented and always gave me the "Lokalise key references" string
# (in square brackets), rather than the actual translated value. I did not attempt to
# figure this out or look further into it.
DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_DEVICETRACKER_ID): str,
        vol.Optional(CONF_API_KEY): str,
        vol.Optional(CONF_OPTIONS, default=DEFAULT_OPTION): str,
        vol.Optional(CONF_HOME_ZONE, default=DEFAULT_HOME_ZONE): str,
        vol.Optional(CONF_MAP_PROVIDER, default=DEFAULT_MAP_PROVIDER): vol.In(
            MAP_PROVIDER_OPTIONS
        ),
        vol.Optional(CONF_MAP_ZOOM, default=int(DEFAULT_MAP_ZOOM)): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=20)
        ),
        vol.Optional(CONF_LANGUAGE): str,
        # vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
        vol.Optional(CONF_EXTENDED_ATTR, default=DEFAULT_EXTENDED_ATTR): bool,
    }
)


async def validate_input(hass: core.HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    # Validate the data can be used to set up a connection.

    # This is a simple example to show an error in the UI for a short hostname
    # The exceptions are defined at the end of this file, and are used in the
    # `async_step_user` method below.
    ##if len(data["host"]) < 3:
    ##    raise InvalidHost

    ##hub = Hub(hass, data["host"])
    # The dummy hub provides a `test_connection` method to ensure it's working
    # as expected
    ##result = await hub.test_connection()
    ##if not result:
    # If there is an error, raise an exception to notify HA that there was a
    # problem. The UI will also show there was a problem
    ##raise CannotConnect

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    # "Title" is what is displayed to the user for this hub device
    # It is stored internally in HA as part of the device config.
    # See `async_step_user` below for how this is used
    return {"title": data[CONF_NAME]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    # Pick one of the available connection classes in homeassistant/config_entries.py
    # This tells HA if it should be asking for updates, or it'll be notified of updates
    # automatically. This example uses PUSH, as the dummy hub will notify HA of
    # changes.
    ##CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # This goes through the steps to take the user through the setup process.
        # Using this it is possible to update the UI and prompt for additional
        # information. This example provides a single form (built from `DATA_SCHEMA`),
        # and when that has some validated input, it calls `async_create_entry` to
        # actually create the HA config entry. Note the "title" value is returned by
        # `validate_input` above.
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidHost:
                # The error string is set here, and should be translated.
                # This example does not currently cover translations, see the
                # comments on `DATA_SCHEMA` for further details.
                # Set the error on the `host` field, not the entire form.
                errors["host"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
