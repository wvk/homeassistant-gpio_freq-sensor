"""Platform for sensor integration."""

from homeassistant.const import FREQUENCY_HERTZ
from homeassistant.helpers.entity import Entity
from homeassistant.components import rpi_gpio
from RPi import GPIO
from datetime import datetime, timedelta
import time
import logging

from . import DOMAIN, PLATFORMS

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""

    SCAN_INTERVAL=config.get("scan_interval") or timedelta(seconds=0.25)

    sensors = []
    smoothing = (config.get('smoothing') or 0) / 100
    ports = config.get("ports")
    for port_num, port_name in ports.items():
      sensors.append(
        FrequencySensor(port_num, port_name, smoothing)
      )
    add_entities(sensors)


class FrequencySensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, pin, name, smoothing):
        """Initialize the sensor."""
        self._state  = None
        self._name   = name
        self._reader = reader(pin, smoothing)

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
        return FREQUENCY_HERTZ

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = str(self._reader.frequency())


class reader:
   """
   A class to read pulses and calculate their frequency,
   i.e. how often the pulse happens per second.
   This is partly taken from an example provided by the
   PIGPIO lib at https://abyz.me.uk/rpi/pigpio/python.html
   """
   def __init__(self, pin, weighting=0.0):
      """
      Instantiate with the Pi and gpio of the PWM signal
      to monitor.

      Optionally a weighting may be specified.  This is a number
      between 0 and 1 and indicates how much the old reading
      affects the new reading.  It defaults to 0 which means
      the old reading has no effect.  This may be used to
      smooth the data.
      """
      rpi_gpio.setup_input(pin, "UP")

      if weighting < 0.0:
         weighting = 0.0
      elif weighting > 0.99:
         weighting = 0.99

      self._new = 1.0 - weighting # Weighting for new reading.
      self._old = weighting       # Weighting for old reading.

      self._last_tick = None
      self._period = None
      self._high = None

      GPIO.add_event_detect(pin, GPIO.RISING, callback=self._cbf, bouncetime=1)

   def _cbf(self, gpio):
      tick = datetime.now()

      if self._last_tick is not None:
         delta_t = self.time_since_last_tick(tick)

         if self._period is not None:
            self._period = (self._old * self._period) + (self._new * delta_t)
         else:
            self._period = delta_t

      self._last_tick = tick

   def frequency(self):
      """
      Returns the input frequency.
      """
      if self._last_tick is None or self.time_since_last_tick() > 1.0:
        return 0.0
      elif self._period is not None:
         return round(1.0 / self._period, 4)
      else:
         return 0.0

   def time_since_last_tick(self, tick=None):
      now = tick or datetime.now()
      delta_t = (now - self._last_tick).total_seconds()

      return delta_t
