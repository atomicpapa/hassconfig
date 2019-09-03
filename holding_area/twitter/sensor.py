"""
Support for Twitter-based sensors.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.twitter/
"""

import logging
import re
from datetime import timedelta

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle


_LOGGER = logging.getLogger(__name__)
_COUNT_LIMIT = 200

REQUIREMENTS = ['python-twitter==3.3']
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=30)
CONF_CONSUMER_KEY = 'consumer_key'
CONF_CONSUMER_SECRET = 'consumer_secret'
CONF_ACCESS_TOKEN_KEY = 'access_token_key'
CONF_ACCESS_TOKEN_SECRET = 'access_token_secret'
CONF_SCREEN_NAMES = 'screen_names'
DATA_TWITTER = 'twitter'

"""
SCREEN_NAME_SCHEMA = vol.Schema({
    vol.All(cv.ensure_list, [cv.string])
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_CONSUMER_KEY): cv.string,
    vol.Required(CONF_CONSUMER_SECRET): cv.string,
    vol.Required(CONF_ACCESS_TOKEN_KEY): cv.string,
    vol.Required(CONF_ACCESS_TOKEN_SECRET): cv.string,
    vol.Required(CONF_SCREEN_NAMES): vol.Schema({cv.string: SCREEN_NAME_SCHEMA})
})
"""

def _get_entity_id(screen_name, key):
    return '{} {}'.format(screen_name, key)

def setup_platform(hass, config, add_devices, discover_info=None):
    """Set up the Twitter sensor platform."""
    import twitter
    api = twitter.Api(
        consumer_key=config.get(CONF_CONSUMER_KEY),
        consumer_secret=config.get(CONF_CONSUMER_SECRET),
        access_token_key=config.get(CONF_ACCESS_TOKEN_KEY),
        access_token_secret=config.get(CONF_ACCESS_TOKEN_SECRET),
        tweet_mode='extended')
    try:
        api.VerifyCredentials()
    except twitter.error.TwitterError:
        _LOGGER.error('credential issue')
        return

    hass.data[DATA_TWITTER] = TwitterData(api, config.get(CONF_SCREEN_NAMES))

    def get_keys():
        """Get entity ids based on screen names and group names."""
        for screen_name, regexes in config.get(CONF_SCREEN_NAMES).items():
            for regex in regexes:
                pattern = re.compile(regex)
                for key in pattern.groupindex:
                    yield _get_entity_id(screen_name, key)

    add_devices([TwitterSensor(hass.data[DATA_TWITTER], key) for key in get_keys()], True)


class TwitterData:
    """Queries and stores data from Twitter."""

    def __init__(self, api, screen_names):
        """Initialize data container."""
        self._api = api
        self._screen_names = screen_names
        self.data = {}

    def _query_twitter(self, screen_name, regexes):
        """Scrape tweets by screen name."""
        found = set()
        for tweet in self._api.GetUserTimeline(screen_name=screen_name, count=_COUNT_LIMIT):
            for regex in regexes:
                if regex in found:
                    continue
                matches = re.search(regex, tweet.full_text)
                if not matches:
                    continue
                found.add(regex)
                yield from matches.groupdict().items()

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Update data values on scheduled interval."""
        for screen_name, regexes in self._screen_names.items():
            for key, value in self._query_twitter(screen_name, regexes):
                entity_id = _get_entity_id(screen_name, key)
                self.data[entity_id] = value


class TwitterSensor(Entity):
    """Representation of a Twitter sensor."""

    def __init__(self, twitter, key):
        """Initialize sensor."""
        self._twitter = twitter
        self._key = key
        self._state = None

    @property
    def name(self):
        """Return the name."""
        return self._key

    @property
    def state(self):
        """Return the state."""
        return self._state

    def update(self):
        """Update the sensor state."""
        self._twitter.update()
        self._state = self._twitter.data.get(self._key)
