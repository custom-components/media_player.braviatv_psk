"""Sony Bravia TV PSK init file."""
from .const import DOMAIN

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, "media_player"))
    return True