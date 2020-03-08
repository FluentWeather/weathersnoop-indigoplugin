# Indigo Plugin for WeatherSnoop

This plugin allows you to get data from the WeatherSnoop application into [Indigo](http://www.indigodomo.com). You may create as many “Weather Station” devices as you like - one for each instance of WeatherSnoop that you have (WeatherSnoop 2.x only supports one station at a time, whereas WeatherSnoop 3, 4, and 5 can have multiple stations known as agents).

WeatherSnoop, with it's ability to connect to local weather station hardware (it supports a wide variety of hardware) is a great way to get weather data into Indigo for use in your home automation logic.

Each station will have a variety of device states that hold information that can be used in triggers, conditions, and on control pages.

## Plugin Configuration

The plugin's config dialog allows you to turn on extra debugging information in the Event Log. Unless you're trying to debug a problem it's probably best to leave that unchecked.

## WeatherSnoop 3/4/5 Support

Each agent exposes only the fields that can be supplied by the particular hardware or source that the agent uses. So, a Davis weather station hardware may have different fields available than another station. The plugin will just pass through the data that the agent supplies unmodified in any way. This will make updates seamless - if a new property is added to an existing agent, it will just automatically show up as a custom state - no need to update the plugin.

In WeatherSnoop, make sure that you have “Serve my weather data via HTTP on port” checkbox selected in the Preferences.

### Creating an Agent Device

WeatherSnoop has many great features, one of which is Bonjour discovery which makes device creation a snap:

1. Select `DEVICES` (or one of it's subfolders) from the Outline View
2. Click on the `New…` button
3. In the resulting `Create New Device` dialog, select `WeatherSnoop` from the `Type:` popup
4. Select `WeatherSnoop 3+ Agent` from the `Model:` menu
5. In the resulting `Configure WeatherSnoop 3+ Agent` dialog, you have some options:
 i. First, you must identify the WeatherSnoop instance - the most convenient way is to select it from the `Select WeatherSnoop instance` popup. This popup shows all WeatherSnoop 3+ instances running on your local network. If you don't see your WeatherSnoop or if it's on a different network, click the `Manually enter network address` checkbox, enter the host and port and click `Scan for Agents`.
 ii. Next, the `Select WeatherSnoop agent popup` list should show all agents that WeatherSnoop has open. If there are none in the list, make sure WeatherSnoop is configured to share data and that it has at least one open agent. You can click `Scan for Agents` if you made any changes in WeatherSnoop.
 iii. Once you've selected the appropriate agent, select the field you want displayed in the `State` column of the Device List. Most people will probably select the temperature but you can select whatever you want.
6. Click `Save`
7. Name the timer something useful and close the `Create New Device` dialog

As stated above, the device states presented in the device will vary based on what's provided by the selected agent. Contact Tee-Boy about any data you believe should be available for your agent type that doesn't show up.

## WeatherSnoop 2 Support

For WeatherSnoop 2, we attempted to create a common set of data for all supported weather stations and weather underground. This means that some information may not be available for any given station - if the data isn't available from WeatherSnoop, the value of that particular state will be “- data unavailable -”. There are some exceptions to this rule: specifically, the rain* fields will always be numeric (so that can be safely used in calculations, conditions, etc.). Here's how they work - when a weather station device is first created, these fields will be set to 0. Then based on what rain information we get, they will be set/calculated appropriately. If no rain data is ever received, they will all continue to be 0.

And, while we're on the topic, any value set to “- data unavailable -” that's used in a numeric device state condition (say, a temperature sensor that isn't working), will always return False thus aborting your trigger/schedule. So be careful about using those fields in conditions unless you're positive that they will always be available OR that triggers/schedules that depend on them firing actions won't if the data becomes unavailable.

In WeatherSnoop 2.x, make sure that you have HTTP enabled under the Sharing tab on the Weather Agent configuration window.

### Creating a Weather Station Device

The WeatherSnoop Plugin allows you to create Weather Station devices. To create a new one, switch to the device view and click the New… button. This will bring up the device edit dialog. Select Plugin from the Type: popup. Select WeatherSnoop from the Plugin: popup, and select WeatherSnoop 2 Weather Station from the Model: popup. Click on the Edit Device Settings… button (if it doesn't open by itself) and you'll see the Configure Weather Station dialog. Enter the hostname or IP address and port of the computer running WeatherSnoop 2.x (if it's running on the same server as the Indigo server and you haven't changed the default port in WeatherSnoop, then you can just accept the defaults).

### Device States

You can trigger off of various state changes on a Weather Station - like when the temperature or wind direction change. Some of these states don't make for good triggers but will provide some nice information on a control page.

Weather Station device types provide you with several device states that you can use in the Trigger dialog:

* Forecast - A word or two that describes conditions as supplied by the weather station
* Outdoor Temperature °F - Outdoor temperature in Fahrenheit
* Outdoor Temperature °C - Outdoor temperature in Celsius
* Indoor Temperature °F - Indoor temperature in Fahrenheit
* Indoor Temperature °C - Indoor temperature in Celsius
* Temperature Sensor # °F - Up to 10 different external temperature sensors in Fahrenheit
* Temperature Sensor # °C - Up to 10 different external temperature sensors in Celsius
* Outdoor Relative Humidity - The relative humidity outside
* Indoor Relative Humidity - The relative humidity inside
* Humidity Sensor # - The relative humidity for up to 10 external humidity sensors
* Outdoor Dew Point °F - Outside dew point in Fahrenheit
* Outdoor Dew Point °C - Outside dew point in Celsius
* Indoor Dew Point °F - Inside dew point in Fahrenheit
* Indoor Dew Point °C - Inside dew point in Celsius
* Outdoor Heat Index °F - Outside heat index in Fahrenheit
* Outdoor Heat Index °C - Outside heat index in Celsius
* Indoor Heat Index °F - Inside heat index in Fahrenheit
* Indoor Heat Index °C - Inside heat index in Celsius
* Wind Degrees - Wind direction in degrees
* Wind MPH - Wind speed in miles per hour
* Wind KPH - Wind speed in kilometers per hour
* Wind Knots - Wind speed in knots
* Wind Gust MPH - Wind gust speed in miles per hour
* Wind Gust KPH - Wind gust speed in kilometers per hour
* Wind Gust Knots - Wind gust speed in knots
* Wind Chill °F - Outside wind chill in Fahrenheit
* Wind Chill °C - Outside wind chill in Celsius
* Pressure Trend - A word or two describing the pressure trend
* Pressure (inches) - Pressure in inches
* Pressure (mbar) - Pressure in millibars
* Rain Rate Inches per Hour - The current rain rate in inches per hour
* Rain Rate Millimeters per Hour - The current rain rate in millimeters per hour
* Rain Today Inches - Today's rain total in inches
* Rain Today Millimeters - Today's rain total in millimeters
* Rain Yesterday Inches - Yesterday's rain total in inches
* Rain Yesterday Millimeters - Yesterday's rain total in millimeters
* Rain Two Day Inches - Today's + Yesterday's rain total in inches (useful for sprinkler watering logic)
* Rain Two Day Millimeters - Today's + Yesterday's rain total in millimeters (useful for sprinkler watering logic)
* Rain Month Inches - This month's rain total in inches
* Rain Month Millimeters - This month's rain total in millimeters
* Rain Year Inches - This year's rain total in inches
* Rain Year Millimeters - This year's rain total in millimeters
* Rain Total Inches - The rain total in inches for the life of this station (or it's last reset)
* Rain Total Millimeters - The rain total in millimeters for the life of this station (or it's last reset)
* Location - The name of the station as specified in WeatherSnoop
* Latitude - Latitude of the station as specified in WeatherSnoop
* Longitude - Longitude of the station as specified in WeatherSnoop

## Scripting Support

Here's the plugin ID in case you need to programmatically restart the plugin:

Plugin ID: com.perceptiveautomation.indigoplugin.weathersnoop

## Support and Troubleshooting

For usage or troubleshooting tips discuss this plugin in the [Indigo Domotics forum](https://forums.indigodomo.com/viewforum.php?f=280).


