"""
Support for interface with a Sony Bravia TV.

For more details about this platform, please refer to the documentation at
https://github.com/custom-components/media_player.braviatv_psk
"""
import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_HOST,
    CONF_MAC,
    CONF_NAME,
    STATE_OFF,
    STATE_ON,
)

try:
    from homeassistant.components.media_player import PLATFORM_SCHEMA, MediaPlayerEntity
except ImportError:
    from homeassistant.components.media_player import PLATFORM_SCHEMA
    from homeassistant.components.media_player import (
        MediaPlayerDevice as MediaPlayerEntity,
    )
try:
    from homeassistant.components.media_player.const import (
        MEDIA_TYPE_TVSHOW,
        SUPPORT_NEXT_TRACK,
        SUPPORT_PAUSE,
        SUPPORT_PLAY,
        SUPPORT_PLAY_MEDIA,
        SUPPORT_PREVIOUS_TRACK,
        SUPPORT_SELECT_SOURCE,
        SUPPORT_STOP,
        SUPPORT_TURN_OFF,
        SUPPORT_TURN_ON,
        SUPPORT_VOLUME_MUTE,
        SUPPORT_VOLUME_SET,
        SUPPORT_VOLUME_STEP,
    )
except ImportError:
    from homeassistant.components.media_player import (
        MEDIA_TYPE_TVSHOW,
        SUPPORT_NEXT_TRACK,
        SUPPORT_PAUSE,
        SUPPORT_PLAY,
        SUPPORT_PLAY_MEDIA,
        SUPPORT_PREVIOUS_TRACK,
        SUPPORT_SELECT_SOURCE,
        SUPPORT_STOP,
        SUPPORT_TURN_OFF,
        SUPPORT_TURN_ON,
        SUPPORT_VOLUME_MUTE,
        SUPPORT_VOLUME_SET,
        SUPPORT_VOLUME_STEP,
    )

__version__ = "0.4.0"

_LOGGER = logging.getLogger(__name__)

DOMAIN = "braviatv_psk"

SUPPORT_BRAVIA = (
    SUPPORT_PAUSE
    | SUPPORT_VOLUME_STEP
    | SUPPORT_VOLUME_MUTE
    | SUPPORT_VOLUME_SET
    | SUPPORT_PREVIOUS_TRACK
    | SUPPORT_NEXT_TRACK
    | SUPPORT_TURN_ON
    | SUPPORT_TURN_OFF
    | SUPPORT_PLAY_MEDIA
    | SUPPORT_SELECT_SOURCE
    | SUPPORT_PLAY
    | SUPPORT_STOP
)

DEFAULT_NAME = "Sony Bravia TV"
DEVICE_CLASS_TV = "tv"

# Config file
CONF_12H = "12H"
CONF_24H = "24H"
CONF_PSK = "psk"
CONF_AMP = "amp"
CONF_ANDROID = "android"
CONF_SOURCE_FILTER = "sourcefilter"
CONF_TIME_FORMAT = "time_format"
CONF_USER_LABELS = "user_labels"

# Some additional info to show specific for Sony Bravia TV
TV_WAIT = "TV started, waiting for program info"
TV_APP_OPENED = "App opened"
TV_NO_INFO = "No info (resumed after pause or app opened)"
PLAY_MEDIA_OPTIONS = [
    "Num1",
    "Num2",
    "Num3",
    "Num4",
    "Num5",
    "Num6",
    "Num7",
    "Num8",
    "Num9",
    "Num0",
    "Num11",
    "Num12",
    "Netflix",
    "Red",
    "Green",
    "Yellow",
    "Blue",
    "ChannelUp",
    "ChannelDown",
    "Up",
    "Down",
    "Left",
    "Right",
    "Display",
    "Tv",
    "Confirm",
    "Home",
    "EPG",
    "Return",
    "Options",
    "Exit",
    "Teletext",
    "Input",
    "TvPause",
    "Play",
    "Pause",
    "Stop",
    "HDMI 1",
    "HDMI 2",
    "HDMI 3",
    "HDMI 4",
    "SleepTimer",
    "GooglePlay",
]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PSK): cv.string,
        vol.Optional(CONF_MAC): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_AMP, default=False): cv.boolean,
        vol.Optional(CONF_ANDROID, default=False): cv.boolean,
        vol.Optional(CONF_SOURCE_FILTER, default=[]): vol.All(
            cv.ensure_list, [cv.string]
        ),
        vol.Optional(CONF_TIME_FORMAT, default=CONF_24H): vol.In([CONF_12H, CONF_24H]),
        vol.Optional(CONF_USER_LABELS, default=False): cv.boolean,
    }
)

SERVICE_BRAVIA_COMMAND = "bravia_command"
SERVICE_BRAVIA_OPEN_APP = "bravia_open_app"

ATTR_COMMAND_ID = "command_id"
ATTR_URI = "uri"

BRAVIA_COMMAND_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_COMMAND_ID): cv.string,
    }
)

BRAVIA_OPEN_APP_SCHEMA = vol.Schema(
    {vol.Required(ATTR_ENTITY_ID): cv.entity_id, vol.Required(ATTR_URI): cv.string}
)

registered_devices = []

# pylint: disable=unused-argument


def convert_time_format(time_format, time_raw):
    """Convert time format."""
    if time_format == CONF_12H:
        hours, minutes = time_raw.split(":")
        hours, minutes = int(hours), int(minutes)
        setting = "AM"
        if hours > 12:
            setting = "PM"
            hours -= 12
        elif hours == 0:
            hours = 12
        return "{}:{:02d} {}".format(hours, minutes, setting)
    return time_raw


def lookup_registered_device(entity_id):
    """Lookup registered Bravia device by entity_id."""
    for device in registered_devices:
        if device.entity_id == entity_id:
            return device
    return None


async def async_setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Sony Bravia TV platform."""
    host = config.get(CONF_HOST)
    psk = config.get(CONF_PSK)
    mac = config.get(CONF_MAC)
    name = config.get(CONF_NAME)
    amp = config.get(CONF_AMP)
    android = config.get(CONF_ANDROID)
    source_filter = config.get(CONF_SOURCE_FILTER)
    time_format = config.get(CONF_TIME_FORMAT)
    user_labels = config.get(CONF_USER_LABELS)

    if host is None or psk is None:
        _LOGGER.error("No TV IP address or Pre-Shared Key found in configuration file")
        return

    device = await hass.async_add_executor_job(
        BraviaTVEntity,
        host,
        psk,
        mac,
        name,
        amp,
        android,
        source_filter,
        time_format,
        user_labels,
    )
    add_devices([device])
    registered_devices.append(device)

    await hass.async_add_executor_job(setup_hass_services, hass, android)


def setup_hass_services(hass, android):
    """Create the services for bravia TV."""

    async def async_send_command(call):
        """Send command to TV."""
        command_id = call.data.get(ATTR_COMMAND_ID)
        entity_id = call.data.get(ATTR_ENTITY_ID)
        device = lookup_registered_device(entity_id)
        if device:
            await device.async_send_command(command_id)
        else:
            _LOGGER.warning('No registered Bravia TV with entity_id: %s', entity_id)

    async def async_open_app(call):
        """Open app on TV."""
        uri = call.data.get(ATTR_URI)
        entity_id = call.data.get(ATTR_ENTITY_ID)
        device = lookup_registered_device(entity_id)
        if device:
            await device.async_open_app(uri)
        else:
            _LOGGER.warning('No registered Bravia TV with entity_id: %s', entity_id)

    hass.services.register(
        DOMAIN,
        SERVICE_BRAVIA_COMMAND,
        async_send_command,
        schema=BRAVIA_COMMAND_SCHEMA,
    )

    # Only add the open_app service when TV is Android
    if android:
        hass.services.register(
            DOMAIN,
            SERVICE_BRAVIA_OPEN_APP,
            async_open_app,
            schema=BRAVIA_OPEN_APP_SCHEMA,
        )


class BraviaTVEntity(MediaPlayerEntity):
    """Representation of a Sony Bravia TV."""

    def __init__(
        self,
        host,
        psk,
        mac,
        name,
        amp,
        android,
        source_filter,
        time_format,
        user_labels,
    ):
        """Initialize the Sony Bravia device."""
        _LOGGER.info("Setting up Sony Bravia TV")
        from braviapsk import sony_bravia_psk

        self._braviarc = sony_bravia_psk.BraviaRC(host, psk, mac)
        self._name = name
        self._amp = amp
        self._android = android
        self._source_filter = source_filter
        self._state = STATE_OFF
        self._muted = False
        self._program_name = None
        self._channel_name = None
        self._channel_number = None
        self._source = None
        self._source_list = []
        self._label_list = []
        self._content_mapping = {}
        self._duration = None
        self._content_uri = None
        self._playing = False
        self._start_date_time = None
        self._program_media_type = None
        self._min_volume = None
        self._max_volume = None
        self._volume = None
        self._start_time = None
        self._end_time = None
        self._device_class = DEVICE_CLASS_TV
        self._time_format = time_format
        self._user_labels = user_labels

        if mac:
            self._unique_id = "{}-{}".format(mac, name)
        else:
            self._unique_id = "{}-{}".format(host, name)

        _LOGGER.debug(
            "Set up Sony Bravia TV with IP: %s, PSK: %s, MAC: %s", host, psk, mac
        )

        # self.update()

    async def async_update(self):
        """Update TV info."""
        try:
            power_status = await self.hass.async_add_executor_job(
                self._braviarc.get_power_status
            )
            if power_status in ["active", "standby"]:
                await self._async_refresh_channels()
            if power_status == "active":
                self._state = STATE_ON
                await self._async_refresh_volume()
                playing_info = await self.hass.async_add_executor_job(
                    self._braviarc.get_playing_info
                )
                await self._async_reset_playing_info()
                if playing_info is None or not playing_info:
                    self._program_name = TV_NO_INFO
                else:
                    self._program_name = playing_info.get("programTitle")
                    self._channel_name = playing_info.get("title")
                    self._program_media_type = playing_info.get("programMediaType")
                    self._channel_number = playing_info.get("dispNum")
                    self._source = playing_info.get("title")
                    self._content_uri = playing_info.get("uri")
                    self._duration = playing_info.get("durationSec")
                    self._start_date_time = playing_info.get("startDateTime")
                    # Get time info from TV program
                    if self._start_date_time and self._duration:
                        time_info = await self.hass.async_add_executor_job(
                            self._braviarc.playing_time,
                            self._start_date_time,
                            self._duration,
                        )
                        self._start_time = time_info.get("start_time")
                        self._end_time = time_info.get("end_time")
            elif self._program_name == TV_WAIT:
                # TV is starting up, takes some time before it responds
                _LOGGER.info("TV is starting, no info available yet")
            # elif power_status == "standby":
            #     self._refresh_channels()
            #     self._state = STATE_OFF
            else:
                self._state = STATE_OFF

        except Exception as exception_instance:  # pylint: disable=broad-except
            _LOGGER.debug(
                "No data received from TV. Error message: %s", exception_instance
            )
            self._state = STATE_OFF

    async def _async_reset_playing_info(self):
        self._program_name = None
        self._channel_name = None
        self._program_media_type = None
        self._channel_number = None
        self._source = None
        self._content_uri = None
        self._duration = None
        self._start_date_time = None
        self._start_time = None
        self._end_time = None

    async def _async_refresh_volume(self):
        """Refresh volume information."""
        volume_info = await self.hass.async_add_executor_job(
            self._braviarc.get_volume_info
        )
        if volume_info is not None:
            self._volume = volume_info.get("volume")
            self._min_volume = volume_info.get("minVolume")
            self._max_volume = volume_info.get("maxVolume")
            self._muted = volume_info.get("mute")

    async def _async_refresh_channels(self):
        if not self._source_list:
            self._content_mapping = await self.hass.async_add_executor_job(
                self._braviarc.load_source_list
            )
            self._source_list = []
            if not self._source_filter:  # list is empty
                for key in self._content_mapping:
                    self._source_list.append(key)
            else:
                filtered_dict = {
                    title: uri
                    for (title, uri) in self._content_mapping.items()
                    if any(
                        filter_title in title for filter_title in self._source_filter
                    )
                }
                for key in filtered_dict:
                    self._source_list.append(key)

        if not self._label_list:
            self._label_list = await self.hass.async_add_executor_job(
                self._braviarc.get_current_external_input_status
            )
            if self._label_list:
                for key in self._source_list:
                    label = self._convert_title_to_label(key)
                    if label != key:
                        self._source_list.insert(self._source_list.index(key), label)
                        self._source_list.remove(key)

    @property
    def name(self):
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID of the entity."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def source(self):
        """Return the current input source."""
        return self._convert_title_to_label(self._source)

    @property
    def source_list(self):
        """List of available input sources."""
        return self._source_list

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        if self._volume is not None:
            return self._volume / 100
        return None

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self._muted

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        supported = SUPPORT_BRAVIA
        # Remove volume slider if amplifier is attached to TV
        if self._amp:
            supported = supported ^ SUPPORT_VOLUME_SET
        return supported

    @property
    def media_content_type(self):
        """Content type of current playing media.

        Used for program information below the channel in the state card.
        """
        return MEDIA_TYPE_TVSHOW

    @property
    def media_title(self):
        """Title of current playing media.

        Used to show TV channel info.
        """
        return_value = None
        if self._channel_name is not None:
            if self._channel_number is not None:
                return_value = "{0!s}: {1}".format(
                    self._channel_number.lstrip("0"), self._channel_name
                )
            else:
                return_value = self._channel_name
        return self._convert_title_to_label(return_value)

    @property
    def media_series_title(self):
        """Title of series of current playing media, TV show only.

        Used to show TV program info.
        """
        return_value = None
        if self._program_name is not None:
            if self._start_time is not None and self._end_time is not None:
                return_value = "{0} [{1} - {2}]".format(
                    self._program_name,
                    convert_time_format(self._time_format, self._start_time),
                    convert_time_format(self._time_format, self._end_time),
                )
            else:
                return_value = self._program_name
        else:
            if not self._channel_name:  # This is empty when app is opened
                return_value = TV_APP_OPENED
        return return_value

    @property
    def media_content_id(self):
        """Content ID of current playing media."""
        return self._channel_name

    @property
    def device_class(self):
        """Return the device class of the media player."""
        return self._device_class

    async def async_set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        await self.hass.async_add_executor_job(self._braviarc.set_volume_level, volume)

    async def async_turn_on(self):
        """Turn the media player on.

        Use a different command for Android as WOL is not working.
        """
        if self._android:
            await self.hass.async_add_executor_job(self._braviarc.turn_on_command)
        else:
            await self.hass.async_add_executor_job(self._braviarc.turn_on)

        # Show that TV is starting while it takes time
        # before program info is available
        await self._async_reset_playing_info()
        self._state = STATE_ON
        self._program_name = TV_WAIT

    async def async_turn_off(self):
        """Turn the media player off.

        Use a different command for Android since IRCC is not working reliable.
        """
        if self._state == STATE_OFF:
            return

        if self._android:
            await self.hass.async_add_executor_job(self._braviarc.turn_off_command)
        else:
            await self.hass.async_add_executor_job(self._braviarc.turn_off)

        self._state = STATE_OFF

    async def async_volume_up(self):
        """Volume up the media player."""
        await self.hass.async_add_executor_job(self._braviarc.volume_up)

    async def async_volume_down(self):
        """Volume down media player."""
        await self.hass.async_add_executor_job(self._braviarc.volume_down)

    async def async_mute_volume(self, mute):
        """Send mute command."""
        await self.hass.async_add_executor_job(self._braviarc.mute_volume)

    async def async_select_source(self, source):
        """Set the input source."""
        title = self._convert_label_to_title(source)
        if title in self._content_mapping:
            uri = self._content_mapping[title]
            await self.hass.async_add_executor_job(self._braviarc.play_content, uri)

    async def async_media_play_pause(self):
        """Simulate play pause media player."""
        if self._playing:
            await self.async_media_pause()
        else:
            await self.async_media_play()

    async def async_media_play(self):
        """Send play command."""
        self._playing = True
        await self.hass.async_add_executor_job(self._braviarc.media_play)

    async def async_media_pause(self):
        """Send media pause command to media player.

        Will pause TV when TV tuner is on.
        """
        self._playing = False
        if self._program_media_type == "tv" or self._program_name is not None:
            await self.hass.async_add_executor_job(self._braviarc.media_tvpause)
        else:
            await self.hass.async_add_executor_job(self._braviarc.media_pause)

    async def async_media_next_track(self):
        """Send next track command.

        Will switch to next channel when TV tuner is on.
        """
        if self._program_media_type == "tv" or self._program_name is not None:
            await self.hass.async_add_executor_job(
                self._braviarc.send_command, "ChannelUp"
            )
        else:
            await self.hass.async_add_executor_job(self._braviarc.media_next_track)

    async def async_media_previous_track(self):
        """Send the previous track command.

        Will switch to previous channel when TV tuner is on.
        """
        if self._program_media_type == "tv" or self._program_name is not None:
            await self.hass.async_add_executor_job(
                self._braviarc.send_command, "ChannelDown"
            )
        else:
            await self.hass.async_add_executor_job(self._braviarc.media_previous_track)

    async def async_play_media(self, media_type, media_id, **kwargs):
        """Play media."""
        _LOGGER.debug("Play media: %s (%s)", media_id, media_type)

        if media_id in PLAY_MEDIA_OPTIONS:
            await self.hass.async_add_executor_job(
                self._braviarc.send_command, media_id
            )
        else:
            _LOGGER.warning("Unsupported media_id: %s", media_id)

    async def async_send_command(self, command_id):
        """Send arbitrary command to TV via HA service."""
        if self._state == STATE_OFF and not self._android:
            return
        await self.hass.async_add_executor_job(self._braviarc.send_command, command_id)

    async def async_open_app(self, uri):
        """Open app with given uri."""
        if self._state == STATE_OFF and not self._android:
            return
        await self.hass.async_add_executor_job(self._braviarc.open_app, uri)

    def _convert_title_to_label(self, title):
        return_value = title
        if self._user_labels:
            for item in self._label_list:
                if item["title"] == title and item["label"] != "":
                    return_value = item["label"]
        return return_value

    def _convert_label_to_title(self, label):
        return_value = label
        if self._user_labels:
            for item in self._label_list:
                if item["label"] == label and item["title"] != "":
                    return_value = item["title"]
        return return_value
