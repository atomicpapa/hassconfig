from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import (PLATFORM_SCHEMA)
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'keep_notes_sensor'

CONF_NAME = 'name'
CONF_USERNAME = 'username'
CONF_PASSWORD = 'password'
CONF_LIST_ID = 'list_id'

SCAN_INTERVAL = timedelta(seconds=10)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_LIST_ID): cv.string
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Google Keep Notes sensor platform."""
    import gkeepapi
    
    name = config.get(CONF_NAME)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    list_id = config.get(CONF_LIST_ID)
    
    keep = gkeepapi.Keep()
    
    keep.login(username, password)

    add_devices([KeepNotesSensor(hass, name, keep, list_id)])

class KeepNotesSensor(Entity):
    def __init__(self, hass, name, keep, list_id):
        self.hass = hass
        self._name = name
        self._state = None
        self._keep = keep
        self._listid = list_id
        self.hass.data[self._name] = {}

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state
        
    @property
    def device_state_attributes(self):
        return self.hass.data[self._name]
        
    @Throttle(SCAN_INTERVAL)    
    def update(self):
        """Update state and attributes."""
        import gkeepapi
        
        keep = self._keep
        keep.sync()
        
        gnote = keep.get(self._listid)
        
        self._state = 'login successful'

        name = gnote.title
        glist_items = gnote.items
        self.hass.data[self._name]['notes'] = {}
        self.hass.data[self._name]['notes']['name'] = name
        self.hass.data[self._name]['notes']['data'] = []
        for item in glist_items:
            self.hass.data[self._name]['notes']['data'].append({'text' : item.text , 'checked' : item.checked})
