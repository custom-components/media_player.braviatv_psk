"""Config flow for bravia_psk integration."""
import logging

from .const import (
    DOMAIN, 
    CONF_12H,
    CONF_24H,
    CONF_PSK,
    CONF_AMP,
    CONF_ANDROID,
    CONF_SOURCE_FILTER,
    CONF_TIME_FORMAT,
    CONF_USER_LABELS,
    CONF_PIN,
    CONF_ENABLE_COOKIES,
    CONF_USE_CEC_TITLES,
    CONF_USE_CEC_URIS,
    USER_SCHEMA
)
import voluptuous as vol
from homeassistant import config_entries, core, exceptions
from homeassistant.core import callback
from homeassistant.const import (
    CONF_HOST,
    CONF_MAC,
    CONF_NAME,
)
from braviarc import braviarc

_LOGGER = logging.getLogger(__name__)

USER_VOL_SCHEMA = vol.Schema(USER_SCHEMA)

PIN_SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_PIN,
        ): str
    }
)
            
class BraviaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for bravia_psk."""
    VERSION = 3
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL
    
    _braviarc = None
    _main_input = None

    async def async_step_user(self, info=None):
        _LOGGER.info('Starting config flow: User flow')
        _LOGGER.info('User info: ' + str(info))

        return await self.async_step_main(info)

    async def async_step_complete(self, info=None):
        _LOGGER.info('Completed info: ' + str(info))
        if self._main_input:
            info.update(self._main_input)
        host = info[CONF_HOST]

        return self.async_create_entry(title='Connected to %s' % (host,), data=info)
    
    async def async_step_cookie(self, info=None):
        _LOGGER.info('Starting config flow: User flow')
        _LOGGER.info('Cookie info: ' + str(info))
        self._braviarc.connect(info[CONF_PIN], 'hass', 'Home assistant')
        return await self.async_step_complete(info)

    async def async_step_main(self, info=None):
        _LOGGER.info('Starting config flow: Main flow')
        _LOGGER.info('Main info: ' + str(info))

        if info:
            host = info[CONF_HOST]
            psk = info[CONF_PSK]
            
            if not self._braviarc:
                self._braviarc = braviarc.BraviaRC(host, psk, None)

            info[CONF_NAME] = 'Bravia TV: %s' % (info[CONF_NAME],)

            if info[CONF_ENABLE_COOKIES] and not self._braviarc.is_connected():
                self._braviarc.connect('0000', 'hass', 'Home assistant')
                self._main_input = info
                return self.async_show_form(
                    step_id="cookie",
                    data_schema=PIN_SCHEMA
                )
            else:
                return await self.async_step_complete(info)

        return self.async_show_form(
            step_id="main",
            data_schema=USER_VOL_SCHEMA
        )

