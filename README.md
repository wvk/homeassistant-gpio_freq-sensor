# Homeassistant GPIO Frequency Sensor

This is a Homeassistant sensor for reading the frequency of input signals on Raspberry Pi GIPO pins.

It uses the `rpi_gpio` component to listen for HIGH input levels on any number of RPi GPIO pins and converts the intervals to frequencies. Optionally, signal smoothing can be performed to compensate for minimal random irregularities.

The original purpose for this Sensor was to read the RPM of an old diesel engine using a reflective photoelectric sensor and a piece of duct tape on its V-belt pulley.

## Installation

Clone this repository anywhere on your Homeassistant machine (e.g. in `/tmp`):

    cd /tmp
    git clone git@github.com:wvk/homeassistant-gpio_freq-sensor.git

Copy the `gpio_freq` folder into the `custom_components` folder of your Homeassistant installation:

    cd ./homeassistant-gpio_freq-sensor
    cp -r ./custom_components/gpio_freq <your-homeassistant-base-dir>/custom_components/

### Configuration

Configure your first sensor (e.g. in `configuration.yaml` or `sensors.yaml`, depending on your setup):

    sensors:
      - platform: gpio_freq
        scan_interval: 0.25
        smoothing: 10
        ports:
          27: shaft rotation frequency

#### Options

 * `scan_interval`: This sensor uses local polling to get the current value of the frequency reading. Note: This setting has no impact on the the frequency value itself, which is updated every time the GPIO pin level is `HIGH`. It is therefore possible to have e.g. a 1kHz signal which is read one a second (`scan_interval: 1`). Default value is **0.25**, i.e. four readings per second.
 * `ports`: A list of `<GIPO pin number>: <sensor name>` values.
 * `smoothing`: fraction of previous reading to be 'mixed into' the current reading to smooth the signal. Value must be between 0 and 99 (inclusive). Default value is **0**

