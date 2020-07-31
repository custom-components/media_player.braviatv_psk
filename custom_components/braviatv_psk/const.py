DOMAIN = 'braviatv_psk'
CONF_12H = "12H"
CONF_24H = "24H"
CONF_PSK = "psk"
CONF_AMP = "amp"
CONF_ANDROID = "android"
CONF_SOURCE_FILTER = "sourcefilter"
CONF_TIME_FORMAT = "time_format"
CONF_USER_LABELS = "user_labels"
CONF_ENABLE_COOKIES = 'enable_cookies'
CONF_USE_CEC_TITLES = 'use_cec_titles'
CONF_USE_CEC_URIS = 'use_cec_uris'
CONF_PIN = 'pin'

from homeassistant.const import (
    CONF_HOST,
    CONF_MAC,
    CONF_NAME,
)

from homeassistant.components.media_player import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

DEFAULT_NAME = "Sony Bravia TV"

USER_SCHEMA = {
    vol.Required(CONF_HOST): str,
    vol.Required(CONF_PSK): str,
    vol.Optional(CONF_MAC): str,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
    vol.Optional(CONF_AMP, default=False): bool,
    vol.Optional(CONF_ANDROID, default=False): bool,
    #vol.Optional(CONF_SOURCE_FILTER, default=[]): vol.All(
    #    cv.ensure_list, [cv.string]
    #),
    vol.Optional(CONF_TIME_FORMAT, default=CONF_24H): vol.In([CONF_12H, CONF_24H]),
    vol.Optional(CONF_USER_LABELS, default=False): bool,
    vol.Required(
        CONF_ENABLE_COOKIES,
        default=False
    ): bool,
    vol.Required(
        CONF_USE_CEC_TITLES,
        default=True
    ): bool,
    vol.Required(
        CONF_USE_CEC_URIS,
        default=True
    ): bool

}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(USER_SCHEMA)
