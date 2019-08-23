"""
A component which allows you to get information from noaa weather.gov
For more details about this component, please refer to the documentation at
https://github.com/dcshoecomp/noaa_alerts
"""

import logging
import json

import voluptuous as vol
from datetime import timedelta
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.components.switch import (PLATFORM_SCHEMA)
from homeassistant.const import (CONF_LATITUDE, CONF_LONGITUDE, CONF_SCAN_INTERVAL)
from homeassistant.util import Throttle
from noaa_sdk import noaa

_LOGGER = logging.getLogger(__name__)

__version_ = '0.0.9'

REQUIREMENTS = ['noaa_sdk']

CONF_ZONEID="zoneid"
CONF_URGENCY="urgency"
CONF_SEVERITY="severity"

DEFAULT_ZONEID="LAT,LONG"

ATTR_EVENT = 'event'
ATTR_SEVERITY = 'severity'
ATTR_HEADLINE = 'headline'
ATTR_INSTRUCTION = 'instruction'
ATTR_DESCRIPTION = 'description'

SCAN_INTERVAL = timedelta(seconds=60)

ICON = 'mdi:weather-hurricane'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_ZONEID, default=DEFAULT_ZONEID): cv.string,
    vol.Optional(CONF_LATITUDE): cv.latitude,
    vol.Optional(CONF_LONGITUDE): cv.longitude,
    vol.Optional(CONF_URGENCY): cv.string,
    vol.Optional(CONF_SEVERITY): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    zoneid = str(config.get(CONF_ZONEID))
    latitude = config.get(CONF_LATITUDE, hass.config.latitude)
    longitude = config.get(CONF_LONGITUDE, hass.config.longitude)
    event_urgency = str(config.get(CONF_URGENCY))
    event_severity = str(config.get(CONF_SEVERITY))
    update_interval = config.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)
    add_entities([noaa_alertsSensor(zoneid, event_urgency, event_severity, latitude, longitude, update_interval)], True)

def sortedbyurgencyandseverity(prop):
    if (prop['urgency']).lower() == 'immediate':
        sortedvalue = 1
    elif (prop['urgency']).lower() == 'expected':
        sortedvalue = 10
    elif (prop['urgency']).lower() == 'future':
        sortedvalue = 100
    else:
        sortedvalue = 1000
    if (prop['severity']).lower() == 'extreme':
        sortedvalue = sortedvalue * 1
    elif (prop['severity']).lower() == 'severe':
        sortedvalue = sortedvalue * 2
    elif (prop['severity']).lower() == 'moderate':
        sortedvalue = sortedvalue * 3
    else:
        sortedvalue = sortedvalue * 4
    return sortedvalue

class noaa_alertsSensor(Entity):
    def __init__(self, zoneid, event_urgency, event_severity, latitude, longitude, interval):
        self._zoneid = zoneid
        self.latitude = latitude
        self.longitude = longitude
        self._event_urgency = event_urgency
        self._event_severity = event_severity
        self.update = Throttle(interval)(self._update)

    def _update(self):
        if self._zoneid != 'LAT,LONG':
            params={'zone': self._zoneid}
        else:
            params={'point': '{0},{1}'.format(self.latitude,self.longitude)}
        try:
            nws = noaa.NOAA().alerts(active=1, **params)
            nwsalerts = []
            for alert in nws['features'] :
                nwsalerts.append(alert['properties'])
            self._state = len(nwsalerts)
            self._attributes = {}
            self._attributes['alerts'] = sorted(nwsalerts, key=sortedbyurgencyandseverity)
            self._attributes['urgency'] = self._attributes['alerts'][0]['urgency'] if self._state > 0 else None
            self._attributes['event_type'] = self._attributes['alerts'][0]['event'] if self._state > 0 else None
            self._attributes['event_severity'] = self._attributes['alerts'][0]['severity'] if self._state > 0 else None
            self._attributes['description'] = self._attributes['alerts'][0]['description'] if self._state > 0 else None
            self._attributes['headline'] = self._attributes['alerts'][0]['headline'] if self._state > 0 else None
            self._attributes['instruction'] = self._attributes['alerts'][0]['instruction'] if self._state > 0 else None
            self._attributes['alerts_string'] = json.dumps(self._attributes['alerts'])
        except Exception as err:
            self._state = 'Error'
            self._attributes['alerts'] = None
            self._attributes['urgency'] = None
            self._attributes['event_type'] = None
            self._attributes['event_severity'] = None
            self._attributes['description'] = err
            self._attributes['headline'] = None
            self._attributes['instruction'] = None
            self._attributes['alerts_string'] = None
            _LOGGER.error(err)

    @property
    def name(self):
        name = "NOAA Alerts"
        if self._zoneid != 'LAT,LONG':
            name += ' (' + self._zoneid + ')'
        return name

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return ICON

    @property
    def device_state_attributes(self):
        """Return the attributes of the sensor."""
        return self._attributes

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return None
