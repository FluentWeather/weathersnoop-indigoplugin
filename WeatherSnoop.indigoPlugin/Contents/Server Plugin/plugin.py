#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2016, Perceptive Automation, LLC. All rights reserved.
# http://www.indigodomo.com
#
# Todo: 
#	• allow user to specify what temp measurement to show in "State" column - indoor/outdoor and F or C

################################################################################
# Imports
################################################################################
try:
    import indigo
except:
    pass

try:
    import json
except:
    import simplejson as json

import requests
import urlparse
from xml.dom.minidom import parseString
from datetime import datetime
import time
import Queue
import browseBonjour
import urllib2   # only used for WS2 stations
import traceback
import re

################################################################################
# Globals
################################################################################
kTimeout = 5
kServiceType = "_http._tcp"
kWs2FileName = u"/weather.xml"
kWeatherSnoop3String = u"WeatherSnoop 3"
kWeatherSnoop4String = u"WeatherSnoop 4"
kWeatherSnoop5String = u"WeatherSnoop 5"
kFluentWeatherString = u"Fluent Weather"
kUnavailableString = u"unavailable"
kWs2FieldMap = {"forecast":'forecast:value',
    "temperatureF":'temperature:outdoor:value%type=F',
    "temperatureC":'temperature:outdoor:value%type=C',
    "temperatureIndoorF":'temperature:indoor:value%type=F',
    "temperatureIndoorC":'temperature:indoor:value%type=C',
    "temperatureSensor01F":'temperature:extra%id=1:value%type=F',
    "temperatureSensor01C":'temperature:extra%id=1:value%type=C',
    "temperatureSensor02F":'temperature:extra%id=2:value%type=F',
    "temperatureSensor02C":'temperature:extra%id=2:value%type=C',
    "temperatureSensor03F":'temperature:extra%id=3:value%type=F',
    "temperatureSensor03C":'temperature:extra%id=3:value%type=C',
    "temperatureSensor04F":'temperature:extra%id=4:value%type=F',
    "temperatureSensor04C":'temperature:extra%id=4:value%type=C',
    "temperatureSensor05F":'temperature:extra%id=5:value%type=F',
    "temperatureSensor05C":'temperature:extra%id=5:value%type=C',
    "temperatureSensor06F":'temperature:extra%id=6:value%type=F',
    "temperatureSensor06C":'temperature:extra%id=6:value%type=C',
    "temperatureSensor07F":'temperature:extra%id=7:value%type=F',
    "temperatureSensor07C":'temperature:extra%id=7:value%type=C',
    "temperatureSensor08F":'temperature:extra%id=8:value%type=F',
    "temperatureSensor08C":'temperature:extra%id=8:value%type=C',
    "temperatureSensor09F":'temperature:extra%id=9:value%type=F',
    "temperatureSensor09C":'temperature:extra%id=9:value%type=C',
    "temperatureSensor10F":'temperature:extra%id=10:value%type=F',
    "temperatureSensor10C":'temperature:extra%id=10:value%type=C',
    "humidity":'humidity:outdoor:value',
    "humidityIndoor":'humidity:indoor:value',
    "humiditySensor01":'humidity:extra%id=1:value',
    "humiditySensor02":'humidity:extra%id=2:value',
    "humiditySensor03":'humidity:extra%id=3:value',
    "humiditySensor04":'humidity:extra%id=4:value',
    "humiditySensor05":'humidity:extra%id=5:value',
    "humiditySensor06":'humidity:extra%id=6:value',
    "humiditySensor07":'humidity:extra%id=7:value',
    "humiditySensor08":'humidity:extra%id=8:value',
    "humiditySensor09":'humidity:extra%id=9:value',
    "humiditySensor10":'humidity:extra%id=10:value',
    "dewPointF":'dewPoint:outdoor:value%type=F',
    "dewPointC":'dewPoint:outdoor:value%type=C',
    "dewPointIndoorF":'dewPoint:indoor:value%type=F',
    "dewPointIndoorC":'dewPoint:indoor:value%type=C',
    "heatIndexF":'heatIndex:outdoor:value%type=F',
    "heatIndexC":'heatIndex:outdoor:value%type=C',
    "heatIndexIndoorF":'heatIndex:indoor:value%type=F',
    "heatIndexIndoorC":'heatIndex:indoor:value%type=C',
    "windDegrees":'wind:direction:value',
    "windMPH":'wind:speed:value%type=mph',
    "windKPH":'wind:speed:value%type=kph',
    "windKnots":'wind:speed:value%type=kn',
    "windGustMPH":'wind:gust:value%type=mph',
    "windGustKPH":'wind:gust:value%type=kph',
    "windGustKnots":'wind:gust:value%type=kn',
    "windChillF":'windChill:value%type=F',
    "windChillC":'windChill:value%type=C',
    "pressureInches":'barometricPressure:value%type=inHg',
    "pressureMillibars":'barometricPressure:value%type=mb',
    "pressureTrend":'barometricTrend:value',
    "rainRateInches":'rain:rate:value%type=in/hr',
    "rainRateMillimeters":'rain:rate:value%type=mm/hr',
    "rainTodayInches":'rain:day:value%type=in',
    "rainTodayMillimeters":'rain:day:value%type=mm',
    "rainMonthInches":'rain:month:value%type=in',
    "rainMonthMillimeters":'rain:month:value%type=mm',
    "rainYearInches":'rain:year:value%type=in',
    "rainYearMillimeters":'rain:year:value%type=mm',
    "rainTotalInches":'rain:total:value%type=in',
    "rainTotalMillimeters":'rain:total:value%type=mm',
    "soilTemperatureSensor01F":'temperature:soil%id=1:value%type=F',
    "soilTemperatureSensor01C":'temperature:soil%id=1:value%type=C',
    "soilTemperatureSensor02F":'temperature:soil%id=2:value%type=F',
    "soilTemperatureSensor02C":'temperature:soil%id=2:value%type=C',
    "soilTemperatureSensor03F":'temperature:soil%id=3:value%type=F',
    "soilTemperatureSensor03C":'temperature:soil%id=3:value%type=C',
    "soilTemperatureSensor04F":'temperature:soil%id=4:value%type=F',
    "soilTemperatureSensor04C":'temperature:soil%id=4:value%type=C',
    "soilMoistureSensor01":'moistures:soil%id=1:value',
    "soilMoistureSensor02":'moistures:soil%id=2:value',
    "soilMoistureSensor03":'moistures:soil%id=3:value',
    "soilMoistureSensor04":'moistures:soil%id=4:value',
    "leafTemperatureSensor01F":'temperature:leaf%id=1:value%type=F',
    "leafTemperatureSensor01C":'temperature:leaf%id=1:value%type=C',
    "leafTemperatureSensor02F":'temperature:leaf%id=2:value%type=F',
    "leafTemperatureSensor02C":'temperature:leaf%id=2:value%type=C',
    "leafTemperatureSensor03F":'temperature:leaf%id=3:value%type=F',
    "leafTemperatureSensor03C":'temperature:leaf%id=3:value%type=C',
    "leafTemperatureSensor04F":'temperature:leaf%id=4:value%type=F',
    "leafTemperatureSensor04C":'temperature:leaf%id=4:value%type=C',
    "leafMoistureSensor01":'moistures:leaf%id=1:value',
    "leafMoistureSensor02":'moistures:leaf%id=2:value',
    "leafMoistureSensor03":'moistures:leaf%id=3:value',
    "leafMoistureSensor04":'moistures:leaf%id=4:value',
    "uvIndex":'uvIndex:value',
    "solarRadiation":'solarRadiation:value',
    "location":'station:name:value',
    "latitude":'station:location:latitude:decimal',
    "longitude":'station:location:longitude:decimal'}

########################################
# Plugin shared methods
########################################
def getWindDirectionCardinal(windDirectionDegrees):
    windCardinal = ("N","North")
    if windDirectionDegrees in range(11,33):
        windCardinal = ("NNE","North Northeast")
    elif windDirectionDegrees in range(34,55):
        windCardinal = ("NE","Northeast")
    elif windDirectionDegrees in range(56,78):
        windCardinal = ("ENE","East Northeast")
    elif windDirectionDegrees in range(79,100):
        windCardinal = ("E","East")
    elif windDirectionDegrees in range(101,123):
        windCardinal = ("ESE","East Southeast")
    elif windDirectionDegrees in range(124,145):
        windCardinal = ("SE","Southeast")
    elif windDirectionDegrees in range(146,168):
        windCardinal = ("SSE","South Southeast")
    elif windDirectionDegrees in range(169,190):
        windCardinal = ("S","South")
    elif windDirectionDegrees in range(191,213):
        windCardinal = ("SSW","South Southwest")
    elif windDirectionDegrees in range(214,235):
        windCardinal = ("SW","Southwest")
    elif windDirectionDegrees in range(236,258):
        windCardinal = ("WSW","West Southwest")
    elif windDirectionDegrees in range(259,280):
        windCardinal = ("W","West")
    elif windDirectionDegrees in range(281,303):
        windCardinal = ("WNW","West Northwest")
    elif windDirectionDegrees in range(304,325):
        windCardinal = ("NW","Northwest")
    elif windDirectionDegrees in range(326,348):
        windCardinal = ("NNW","North Northwest")
    return windCardinal

def isValidHostname(hostname):
    if len(hostname) > 255 or len(hostname) < 1:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))

################################################################################
class Plugin(indigo.PluginBase):
    ########################################
    # Class properties
    ########################################

    ########################################
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        super(Plugin, self).__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        self.debug = pluginPrefs.get("showDebugInfo", False)
        self.deviceList = []
        self.localWsServers = {}
        self.bonjourBrowserCommandQueue = Queue.Queue()
        self.bonjourBrowser = browseBonjour.BonjourBrowserThread(self.logger.debug, kServiceType, self.bonjourBrowserCommandQueue, kTimeout)
        self.bonjourBrowser.start()
        self.siteFieldCache = {}
        self.deviceStateCache = {}

    ########################################
    def deviceStartComm(self, device):
        self.logger.debug("Starting device: " + device.name)
        # We check to see if the cache created by the config dialog has
        # inserted new dynamic states - if so, replace the ones cached
        # in pluginProps with the new ones then delete them from the cache.
        # We could avoid this if we could write arbitrary plugin props from
        # within the dialog methods.
        if device.deviceTypeId == "ws3station" and (device.pluginProps["wsAgent"] in self.siteFieldCache):
            props = device.pluginProps
            props["dynamicStates"] = self.buildDynamicDeviceStates(self.siteFieldCache[props["wsAgent"]])
            device.replacePluginPropsOnServer(props)
            # TODO: if we want to be clever we could attempt to guess from the "displayState" property
            # what kind of icon to show. By default we'll just show temp sensor (see last line of method).
            device.stateListOrDisplayStateIdChanged()
            del self.siteFieldCache[props["wsAgent"]]
            self.logger.debug("  self.siteFieldCache:\n%s" % unicode(self.siteFieldCache.keys()))
        if device.id not in self.deviceList:
            # we added the soil temp so if the current device doesn't have one
            # force it to reload the states
            self.update(device)
            self.deviceList.append(device.id)
            # and also force the right device state icon to show:
            if device.deviceTypeId == "station" or device.deviceTypeId == "ws3station":
                device.updateStateImageOnServer(indigo.kStateImageSel.TemperatureSensor)

    ########################################
    def deviceStopComm(self, device):
        self.logger.debug("Stopping device: " + device.name)
        if device.id in self.deviceList:
            self.deviceList.remove(device.id)

    ########################################
    def buildDynamicDeviceStates(self, properties):
        newStateList = indigo.List()
        for property in sorted(properties.keys()):
            valueDict = properties[property]
            if len(valueDict["values"]) > 1:
                for value in valueDict["values"]:
                    newState = indigo.Dict()
                    newState["Disabled"] = False
                    newState["Key"] = "%s_%s" % (property, value["unit"])
                    newState["StateLabel"] = "%s in %s" %(valueDict["name"], value["label"])
                    newState["TriggerLabel"] = "%s in %s" %(valueDict["name"], value["label"])
                    if value["type"] == "int" or value["type"] == "float":
                        newState["Type"] = 100
                    else:
                        newState["Type"] = 150
                    newStateList.append(newState)
            else:
                value = valueDict["values"][0]
                newState = indigo.Dict()
                newState["Disabled"] = False
                newState["Key"] = property
                newState["StateLabel"] = valueDict["name"]
                newState["TriggerLabel"] = valueDict["name"]
                if value["type"] == "int" or value["type"] == "float":
                    newState["Type"] = 100
                else:
                    newState["Type"] = 150
                newStateList.append(newState)
        return newStateList

    ########################################
    def getDeviceStateList(self, dev):
        self.logger.debug("getDeviceStateList called")
        newStateList = indigo.List()
        if dev.deviceTypeId in self.devicesTypeDict:
            newStateList = self.devicesTypeDict[dev.deviceTypeId][u"States"]
        if dev.deviceTypeId == "ws3station":
            if "dynamicStates" in dev.pluginProps:
                # OK, so there's no cache most likely because the device just started up
                # and we haven't done an update yet or WeatherSnoop isn't available. In
                # this case we get the cached ones and add them to the built-in states.
                newStateList.extend(dev.pluginProps["dynamicStates"])
        if len(newStateList):
            return newStateList
        return None

    ########################################
    def getDeviceDisplayStateId(self, dev):
        if dev.deviceTypeId == "ws3station":
            # Return the selected state id to display
            return dev.pluginProps.get("displayState", None)
        # for old stations just return temperatureF
        return "temperatureF"

    def didDeviceCommPropertyChange(self, origDev, newDev):
        # We really only need to restart the weather station device if the address changes. We
        # do store other data in the props that changes fairly regularly and we don't need to
        # restart the device each time one of those changes.
        # if origDev.pluginProps["wsInstance"] != newDev.pluginProps["uri"]:
        #     return True
        if origDev.pluginProps['address'] != newDev.pluginProps['address']:
            return True
        return False

    ########################################
    # Dynamic list and callback methods
    ########################################
    def getWSList(self, filter="", valuesDict=None, typeId="", targetId=0):
#	self.logger.debug("getWSList valuesDict: %s" % str(valuesDict))
        itemList = []
        for server, url in self.localWsServers.items():
            itemList.append((server, server))
        if len(itemList) == 0:
            itemList.append(("none", "- no weathersnoop servers available -"))
        self.logger.debug("server popup list: %s" % unicode(itemList))
        return itemList

    ########################################
    def getWSAgentList(self, filter="", valuesDict=None, typeId="", targetId=0):
#	self.logger.debug("getWSAgentList valuesDict: %s" % str(valuesDict))
        itemList = []
        # Get sites.json, open each one to get the name, build the list
        if valuesDict.get("manual", False):
            invalidFields = False
            if not isValidHostname(valuesDict.get("host", "localhost")):
                self.logger.error("Invalid host name specified")
                invalidFields = True
            try:
                if int(valuesDict.get("port", "8000")) > 65535 or int(valuesDict.get("port", "8000")) < 1:
                    self.logger.error("Invalid port number specified")
                    invalidFields = True
            except:
                self.logger.error("Invalid port number specified")
                invalidFields = True
            if invalidFields:
                if len(itemList) == 0:
                    itemList.append(("none", "- no agents available -"))
                return itemList
            server = "%s:%s" % (valuesDict.get("host", "localhost"), valuesDict.get("port", "8000"))
        else:
            server = self.localWsServers.get(valuesDict.get("wsInstance", None), None)
# 		self.logger.debug("server: %s" % server)
        if server:
            url = "http://{}/api/v1/sites.json".format(server)
            try:
                self.logger.debug("url: %s" % url)
                reply = requests.get(url, timeout=5)
                sitesDict = reply.json()
                self.logger.debug("sitesDict: %s" % unicode(sitesDict))
                for siteDict in sitesDict["sites"]:
                    uri = ""
                    try:
                        uri = siteDict["uri"]
                        self.logger.debug("uri for site: %s" % uri)
                        # In WeatherSnoop 3.1.5, they dropped the "https://hostname:port" part of the URIs for some reason
                        # so we need to check to see if the URI start with a / and prepend the protocol/host/port part
                        if uri.startswith("/"):
                            uri = "http://{}{}".format(server, uri)
                            self.logger.debug("new uri: {}".format(uri))
                        siteInformation = self.getWs3SiteData(uri)
                        # WS4 change: siteInformation["agent"]["site"]["name"]
                        name = siteInformation["agent"]["site"]["name"]
                        valuesDict["siteName"] = name
                        props = siteInformation["agent"]["properties"]
                        if "name" in siteDict:
                            agent = siteDict["name"]
                        else:
                            agent = siteDict["agentName"]
                        itemList.append((uri, "%s (%s)" % (name, agent)))
                        self.siteFieldCache[uri] = props
                    except Exception as exc:
                        self.logger.error("Couldn't get information for site - check WeatherSnoop for issues: %s" % uri)
                        self.logger.error("Exception: %s" % exc)
            except Exception, e:
                self.logger.exception("Error getting site information from WeatherSnoop. Make sure that you have a valid IP:Port specified and that WeatherSnoop 3 is running.")
        if len(itemList) == 0:
            itemList.append(("none", "- no agents available -"))
        return itemList

    ########################################
    def getStateList(self, filter="", valuesDict=None, typeId="", targetId=0):
        self.logger.debug("getStateList targetId: %s" % unicode(targetId))
        self.logger.debug("getStateList valuesDict: %s" % unicode(valuesDict))
        itemList = [("none", "- no states available -")]
        if "wsAgent" in valuesDict:
            props = self.siteFieldCache.get(valuesDict["wsAgent"], None)
            self.logger.debug("getStateList siteFieldCache: %s" % unicode(self.siteFieldCache))
            if not props:
                try:
                    siteInformation = self.getWs3SiteData(valuesDict["wsAgent"])
                    props = props = siteInformation["agent"]["properties"]
                except:
                    pass
            if props:
                states = self.buildDynamicDeviceStates(props)
                self.logger.debug("getStateList states: %s" % unicode(states))
                if states:
                    keyList = [(value["Key"], value['StateLabel']) for value in states]
                    if keyList:
                        itemList = keyList
        self.logger.debug("getStateList itemList: %s" % unicode(itemList))
        return itemList

    ########################################
    def stationSelected(self, valuesDict, typeId="", devId=None):
        self.logger.debug("stationSelected called")
        pass

    ########################################
    def agentSelected(self, valuesDict, typeId="", devId=None):
        self.logger.debug("agentSelected called")
        pass

    ########################################
    def scanForAgents(self, valuesDict, typeId, devId):
        self.logger.debug("scanForAgents called: %s" % unicode(valuesDict))
        if valuesDict["wsInstance"] == "" and not valuesDict["manual"]:
            self.logger.error("No valid WeatherSnoop instance selected")

    ########################################
    # Prefs dialog methods
    ########################################
    def closedPrefsConfigUi(self, valuesDict, userCancelled):
        # Since the dialog closed we want to set the debug flag - if you don't directly use
        # a plugin's properties (and for debugLog we don't) you'll want to translate it to
        # the appropriate stuff here.
        if not userCancelled:
            self.debug = valuesDict.get("showDebugInfo", False)
            if self.debug:
                indigo.server.log("Debug logging enabled")
            else:
                indigo.server.log("Debug logging disabled")

    ########################################
    def runConcurrentThread(self):
        self.logger.debug("Starting concurrent tread")
        self.lastCheck = int(time.time())
        try:
            while True:
                try:
                    # Check the dns queue to see if we need to update our server list
                    while not self.bonjourBrowserCommandQueue.empty():
                        command = self.bonjourBrowserCommandQueue.get()
                        self.logger.debug("command: %s" % unicode(command))
                        # WS4: look for either the WS3 or WS4 string in the bonjour broadcast
                        if command[1].startswith(kWeatherSnoop3String) or command[1].startswith(kWeatherSnoop4String) or command[1].startswith(kWeatherSnoop5String) or command[1].startswith(kFluentWeatherString):
                            instanceKey = "%s@%s:%s" % (command[1], command[2], command[3])
                            if command[0] == "add":
                                self.localWsServers[instanceKey] = "%s:%s" % (command[2], command[3])
                                self.logger.debug("Server list: %s" % unicode(self.localWsServers))
                            else:
                                del self.localWsServers[instanceKey]
                                self.logger.debug("Server list: %s" % unicode(self.localWsServers))
                except:
                    pass
                self.sleep(2)
                if (int(time.time()) - self.lastCheck) > 30:
                    # now we cycle through each station
                    for deviceId in self.deviceList:
                        # call the update method with the device instance
                        self.update(indigo.devices[deviceId])
                    self.lastCheck = int(time.time())
        except self.StopThread:
            self.logger.debug("Received StopThread - shutting down the dns browser")
            if self.bonjourBrowser:
                self.bonjourBrowser.stopThread()

    ########################################
    def getWs3SiteData(self, url):
        reply = requests.get(url)
        siteInformation = reply.json()
        return siteInformation

    ########################################
    def update(self,device):
        localPropsCopy = device.pluginProps
        localPropsUpdated = False
        # self.logger.debug("Updating device: " + device.name)
        if device.deviceTypeId == "ws3station":
            # update the fields
            try:
                keyValueList = []
                agentInformation = self.getWs3SiteData(localPropsCopy["wsAgent"])
                if "dataVersion" in agentInformation:
                    siteInformation = agentInformation["agent"]["site"]
                    props = agentInformation["agent"]["properties"]
                    self.updateWs3KeyValueList(device, agentInformation["agent"], "name", propKey="agent", keyValueList=keyValueList)
                    keyValueList.append(
                        {'key': "uri", 'value': urlparse.urlparse(localPropsCopy["wsAgent"]).path}
                    )
                else:
                    # Old WS3 stuff
                    siteInformation = agentInformation["site"]
                    props = siteInformation["properties"]
                    self.updateWs3KeyValueList(device, siteInformation, "agent", keyValueList=keyValueList)
                    self.updateWs3KeyValueList(device, siteInformation, "uri", keyValueList=keyValueList)
                # Get the fixed state values
                self.updateWs3KeyValueList(device, agentInformation["software"], "version", keyValueList=keyValueList)
                self.updateWs3KeyValueList(device, siteInformation, "name", keyValueList=keyValueList)
                self.updateWs3KeyValueList(device, siteInformation, "location", keyValueList=keyValueList)
                self.updateWs3KeyValueList(device, siteInformation, "longitude", keyValueList=keyValueList)
                self.updateWs3KeyValueList(device, siteInformation, "latitude", keyValueList=keyValueList)
                self.updateWs3KeyValueList(device, siteInformation, "elevation", keyValueList=keyValueList)

                newStateList = self.buildDynamicDeviceStates(props)
                statesDiff = self.diffStatesList(localPropsCopy["dynamicStates"], newStateList)
                if statesDiff:
                    if len(keyValueList) > 0:	# Before we add new states better go ahead and push updates first.
                        device.updateStatesOnServer(keyValueList)
                        keyValueList = []
                    self.logger.debug("  update added states:\n%s" % unicode(statesDiff["addedStates"]))
                    self.logger.debug("  update deleted states:\n%s" % unicode(statesDiff["deletedStates"]))
                    self.logger.debug("  update: updating props on the server")
                    localPropsCopy["dynamicStates"] = newStateList
                    device.replacePluginPropsOnServer(localPropsCopy)
                    device.stateListOrDisplayStateIdChanged()

                # Update the states with the new data
                for stateIdBase, stateDict in props.items():
                    uiVal = ""
                    valuesList = stateDict["values"]
                    for valueDict in valuesList:
                        if len(valuesList) == 1:
                            stateKey = stateIdBase
                        else:
                            stateKey = "%s_%s" % (stateIdBase, valueDict["unit"])

                        # If there's a unit, let's pull it out and append it to the uiVal
                        if "unit" in valueDict:
                            unit = valueDict["unit"]
                            if unit != "-":
                                if unit == "F":
                                    uiVal = " °F"
                                elif unit == "C":
                                    uiVal = " °C"
                                elif unit == "pct":
                                    uiVal = "%"
                                elif unit == "deg":
                                    if valueDict.get("type", "int") == "float":
                                        uiVal = "° (%s)" % getWindDirectionCardinal(float(valueDict.get("value", 0.0)))[0]
                                    else:
                                        uiVal = "° (%s)" % getWindDirectionCardinal(int(valueDict.get("value", 0)))[0]
                                else:
                                    uiVal = " %s" % unit
                        self.updateWs3KeyValueList(device, valueDict, "value", valueDict["type"], stateKey, uiVal, keyValueList=keyValueList)

                if len(keyValueList) > 0:
                    device.updateStatesOnServer(keyValueList)
            except Exception as exc:
                stack_trace = traceback.format_exc(10)
                if device.errorState != kUnavailableString:
                    self.logger.error("Couldn't get site information from WeatherSnoop for device \"%s\" - check to see if WeatherSnoop is running correctly." % device.name)
                    device.setErrorStateOnServer(kUnavailableString)
                    self.logger.debug("Error specifics:\n%s" % traceback.format_exc(10))
        else:
            # download the file
            theUrl = u"http://" + device.pluginProps["address"] + kWs2FileName
            try:
                self.logger.debug("    Getting weather.xml")
                f = urllib2.urlopen(theUrl)
            except urllib2.HTTPError, e:
                self.logger.exception("Error getting station %s data" % device.name)
                return
            except urllib2.URLError, e:
                self.logger.exception("Error getting station \"%s\" data (WeatherSnoop isn't running or the agent isn't running)" % device.name)
                return
            except Exception, e:
                self.logger.exception("Unknown error for device %s" % device.name)
                return
            self.logger.debug("    Got weather.xml")
            theXml = f.read()
            #self.logger.debug(theXml)
            theDocTree = parseString(theXml)
            keyValueList = []
            for state,fieldName in kWs2FieldMap.iteritems():
                # longitude and latitude are the only two elements that don't stop with <value> so
                # we need to pass in <decimal>, which is the final element name that contains the
                # actual value
                if (state == "longitude") or (state == "latitude"):
                    finalElement = "decimal"
                else:
                    finalElement = "value"
                newValueTup = self.getValueFromElement(theDocTree, fieldName, finalElement)
                self.logger.debug("    Updating device: state=%s fieldName=%s newValueTup=%s" % (state, fieldName, unicode(newValueTup)))
                newValue = newValueTup[0]
                if newValue.startswith("%%"):
                    newValue = "- data unavailable -"
                if (newValue == "Uninitialized") or (newValue.startswith("-9999")):
                    newValue = "- data unavailable -"
                if ((state.find("Inches") != -1) and (newValue == "- data unavailable -") and (state != "pressureInches")):
                    newValue = 0.00
                if ((state.find("Millimeters") != -1) and (newValue == "- data unavailable -")):
                    newValue = 0
                if newValueTup[1] != "":
                    # we got a new timestamp, so let's do a little sanity checking
                    # first, put it into a form where we can use strptime to get a real python date
                    newValueDateString = ' '.join(newValueTup[1].split(' ')[0:2])
                    thisUpdate = datetime.strptime(newValueDateString,"%Y-%m-%d %H:%M:%S")
                    #self.logger.debug("        newValueDateString=%s thisUpdate:=%s" % (newValueDateString, str(thisUpdate)))
                    # here's where we need to check the timestamp - if it's older than 24 hours
                    # update the state with "- data unavailable -"
                    if finalElement == "value":
                        # get the current value string from pluginProps
                        if state+"-ts" in device.pluginProps:
                            # get the date
                            lastUpdate = datetime.strptime(device.pluginProps[state+"-ts"], "%Y-%m-%d %H:%M:%S")
                            elapsedTime = thisUpdate - lastUpdate
                            curDateTime = datetime.now()
                            ageDelta = curDateTime - thisUpdate
                            ageInDays = ageDelta.days
                            #self.logger.debug("        Updating device: lastUpdate=%s elapsedTime=%s" % (str(lastUpdate),str(elapsedTime)))
                            elapsedTimeInHours = elapsedTime.seconds/60/60 # calculate elapsed time in whole hours
                            #self.logger.debug("        elapsedTimeInHours=%i ageInDays=%i" % (elapsedTimeInHours, ageInDays))
                            # Skip soil and leaf temps - they apparently can stay constant over 24 hours
                            if (not state.startswith("leaf")) and (not state.startswith("soil")):
                                if ((elapsedTimeInHours > 23) or (ageInDays > 0)) and (not state.startswith("rain")):
                                    # The data is older than 24 hours, so we want to mark it as unavailable unless it's a rain field
                                    newValue = "- data unavailable -"
                                else:
                                    # if it's rainToday* and we just rolled over to the next day, reset rain yesterday
                                    if (state == 'rainTodayInches') or (state == 'rainTodayMillimeters'):
                                        if curDateTime.day != lastUpdate.day:
                                            # we rolled over the day mark, so we need to save off the old value into
                                            # yesterday's value
                                            if state == 'rainTodayInches':
                                                self.updateKeyValueList(device, 'rainYesterdayInches', device.states['rainTodayInches'], keyValueList)
                                                self.logger.debug("        midnight crossed, setting yesterday to %s inches" % (device.states['rainTodayInches'],))
                                            if state == 'rainTodayMillimeters':
                                                self.updateKeyValueList(device, 'rainYesterdayMillimeters', device.states['rainTodayMillimeters'], keyValueList)
                                                self.logger.debug("        midnight crossed, setting yesterday to %s millimeters" % (device.states['rainTodayMillimeters'],))
                                        localPropsCopy[state+"-ts"] = curDateTime.strftime("%Y-%m-%d %H:%M:%S")
                                    else:
                                        localPropsCopy[state+"-ts"] = newValueDateString
                                    localPropsUpdated = True
                        else:
                            # date doesn't exist, so add the date and continue to the update
                            localPropsCopy[state+"-ts"] = newValueDateString
                            localPropsUpdated = True
                            elapsedTime = datetime.now() - thisUpdate
                            if elapsedTime.days > 0:
                                # The data is older than 24 hours, so we want to mark it as unavailable
                                if ((state.find("Inches") != -1) and (state != "pressureInches")):
                                    newValue = 0.00
                                elif (state.find("Millimeters") != -1):
                                    newValue = 0
                                else:
                                    newValue = "- data unavailable -"
                self.updateKeyValueList(device, state, newValue, keyValueList)
                if state == 'rainTodayInches':
                    device.refreshFromServer()
                    try:
                        rainYesterdayInches = float(device.states['rainYesterdayInches'])
                    except:
                        rainYesterdayInches = 0.00
                    if newValue != "- data unavailable -":
                        self.updateKeyValueList(device, 'rainTwoDayInches', str(float(newValue) + rainYesterdayInches), keyValueList)
                    else:
                        self.logger.debug("    current rain data is not available")
                        self.updateKeyValueList(device, 'rainTwoDayInches', rainYesterdayInches, keyValueList)
                elif state == 'rainTodayMillimeters':
                    device.refreshFromServer()
                    try:
                        rainYesterdayMillimeters = int(device.states['rainYesterdayMillimeters'])
                    except:
                        rainYesterdayMillimeters = 0
                    if newValue != "- data unavailable -":
                        self.updateKeyValueList(device, 'rainTwoDayMillimeters', str(int(float(newValue)) + rainYesterdayMillimeters), keyValueList)
                    else:
                        self.logger.debug("    current rain data is not available")
                        self.updateKeyValueList(device, 'rainTwoDayMillimeters', rainYesterdayMillimeters, keyValueList)
            if len(keyValueList) > 0:
                device.updateStatesOnServer(keyValueList)
        if localPropsUpdated:
            device.replacePluginPropsOnServer(localPropsCopy)

    ########################################
    def diffStatesList(self, oldStates, newStates):
        oldStatesList = map(lambda state: state["Key"], oldStates)
        newStatesList = map(lambda state: state["Key"], newStates)
        oldStatesLost = list(set(oldStatesList) - set(newStatesList))
        newStatesLost = list(set(newStatesList) - set(oldStatesList))
        if oldStatesLost or newStatesLost:
            return {"deletedStates": oldStatesLost, "addedStates": newStatesLost}
        return None

    ########################################
    def updateWs3KeyValueList(self, device, dictionary, property, type="string", propKey=None, uiVal=u"", keyValueList=None):
        places = -1
        if not propKey:
            propKey = property
        if property in dictionary:
            newValue = None
            try:
                if type == "float":
                    newValue = float(dictionary[property])
                    places = 2
                elif type == "int":
                    newValue = int(dictionary[property])
                else:
                    newValue = dictionary[property]
            except:
                self.logger.debug("WeatherSnoop device \"%s\" reports an incorrect value type for state \"%s\" (can't be converted from string to %s)." % (device.name, propKey, type))
                newValue = dictionary[property]
            valueString = unicode(newValue)
            uiValueString = "".format(valueString, uiVal)
            keyValueList.append({'key':propKey, 'value':newValue, 'uiValue':uiValueString, 'decimalPlaces':places})
        else:
            self.logger.error("WeatherSnoop device \"%s\" no longer contains data for state %s." % (device.name, propKey))
            keyValueList.append({'key':propKey, 'value':"- data unavailable -"})

    ########################################
    def updateKeyValueList(self, device, state, newValue, keyValueList):
        if (newValue != device.states[state]):
            keyValueList.append({'key':state, 'value':newValue})

    ########################################
    # UI Validate, Close, and Actions defined in Actions.xml:
    ########################################
    def validateDeviceConfigUi(self, valuesDict, typeId, devId):
        self.logger.debug("validateDeviceConfigUi devId: %s" % str(devId))
        errorsDict = indigo.Dict()
        errorFound = False
        manualEntry = valuesDict.get("manual", False) if typeId == "ws3station" else True
        if manualEntry:
            if "host" not in valuesDict:
                errorsDict["host"] = 'You must specify a host name or IP address if you choose to manually enter network information. Use "localhost" if WeatherSnoop is running on the same machine as the Indigo server.'
            else:
                if not isValidHostname(valuesDict["host"]):
                    errorsDict["host"] = 'You must specify a host name or IP address if you choose to manually enter network information. Use "localhost" if WeatherSnoop is running on the same machine as the Indigo server.'
            if "port" not in valuesDict:
                errorsDict["host"] = 'You must specify a port number if you choose to manually enter network information. "8000" is the default port number for WeatherSnoop.'
            else:
                try:
                    if int(valuesDict.get("port", "8000")) > 65535 or int(valuesDict.get("port", "8000")) < 1:
                        errorsDict["host"] ="Invalid port number specified"
                except:
                    errorsDict["host"] ="Invalid port number specified"
            valuesDict['address'] = valuesDict["host"] + ":" + valuesDict["port"]
        if typeId == "ws3station":
            if ("wsInstance" not in valuesDict or valuesDict["wsInstance"] == "") and not manualEntry:
                errorsDict["wsInstance"] = "You must either select a station or manually enter host information."
            # make sure they've selected an agent and a state field
            self.logger.debug("wsAgent: %s" % valuesDict["wsAgent"])
            p = re.compile(r'http\:\/\/(.*)\/.*.json')
            m = p.match(valuesDict["wsAgent"])
            if m:
                valuesDict["address"] = m.group(1)
            else:
                errorsDict["wsAgent"] = "You must select an agent. If you manually selected an agent you can scan for agents by pressing the 'Scan for Agents' button above."
            if "displayState" not in valuesDict or valuesDict["displayState"] == "":
                errorsDict["displayState"] = "You must select a state to display in the state column."
        if len(errorsDict) > 0:
            return (False, valuesDict, errorsDict)
        else:
            if typeId == "ws3station":
                self.siteFieldCache = {valuesDict["wsAgent"]: self.siteFieldCache[valuesDict["wsAgent"]]}
            return (True, valuesDict)

    ########################################
    def getValueFromElement(self, xmlDoc,elementDescriptor,finalTag):
        theReturnValue = "- data unavailable -"
        theTimeStamp = ""
        curElem = xmlDoc.getElementsByTagName("xml")[0]
        hierarchy = elementDescriptor.split(":")
        try:
            for element in hierarchy:
                if element.startswith(finalTag):
                    # need to split out any attributes that are specified (like "type") so
                    # we can get the right element
                    valueSplit = element.split("%")
                    if len(valueSplit) > 1:
                        # there is an attribute that we have to look for, so there are multiple <finalTag> elements
                        valueAttrName = valueSplit[1].split("=")[0]
                        valueAttrValue = valueSplit[1].split("=")[1]
                        # there is an attribute that we have to look for, so there are multiple elements
                        valueList = curElem.getElementsByTagName(valueSplit[0])
                        for tempValueElem in valueList:
                            val = tempValueElem.attributes[valueAttrName].value
                            if valueAttrValue == val:
                                theReturnValue = tempValueElem.childNodes[0].data
                                break
                    else:
                        # there is only one <finalTag> element so just get it's value
                        theReturnValue = curElem.getElementsByTagName(finalTag)[0].childNodes[0].data
                    # we've gotten to the value - need to pull out the time element as well
                    try:
                        theTimeStamp = curElem.getElementsByTagName('time')[0].childNodes[0].data
                    except:
                        # if it doesn't have a time element just skip it
                        pass
                else:
                    # this is one of the middle elements
                    # look to see if it has an attribute, which means we have to look for a specific element
                    elementSplit = element.split("%")
                    #self.logger.debug("Split elements: %s" % elementSplit)
                    if len(elementSplit) > 1:
                        attrs = elementSplit[1].split("=")
                        attrName = attrs[0]
                        attrValue = attrs[1]
                        # there is an attribute that we have to look for, so there are multiple elements
                        elemList = curElem.getElementsByTagName(elementSplit[0])
                        if len(elemList) == 0:
                            # the element wasn't found - so we just return the defaults
                            return (theReturnValue, theTimeStamp)
                        for tempElem in elemList:
                            val = tempElem.attributes[attrName].value
                            if attrValue == val:
                                curElem = tempElem
                                break
                    else:
                        # no attributes so we just get the first one
                        curElem = curElem.getElementsByTagName(element)[0]
        except:
            # got an error parsing the XML - just bail
            pass
        return (theReturnValue, theTimeStamp)

    ########################################
    # Menu Methods
    ########################################
    def toggleDebugging(self):
        if self.debug:
            indigo.server.log("Turning off debug logging")
            self.pluginPrefs["showDebugInfo"] = False
        else:
            indigo.server.log("Turning on debug logging")
            self.pluginPrefs["showDebugInfo"] = True
        self.debug = not self.debug


