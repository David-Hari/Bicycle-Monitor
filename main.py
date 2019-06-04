"""

  Monitors data from ANT+ devices and displays information on screen.

"""

import os
import time
from ant.core import driver
from ant.core.node import Node, Network, ChannelID
from ant.core.constants import *
from ant.core.exceptions import *
from ant.plus.heartrate import *
from ant.plus.power import *
import gpsd

import config
import display
import data_logging


power = 0
heartRate = 0
cpuWarnTemperature = 80  # Degrees C
cpuBadTemperature = 90
tempWarning = None
gspWarning = None
#TODO: powerUpdateMutex = something


def devicePaired(deviceProfile, channelId):
	display.showStatusText(f'Connected to {deviceProfile.name} ({channelId.deviceNumber})')

def powerMonitorPaired(deviceProfile, channelId):
	devicePaired(deviceProfile, channelId)
	deviceProfile.setCrankLength(config.crankLength)

def searchTimedOut(deviceProfile):
	display.showStatusText(f'Could not connect to {deviceProfile.name}')

def channelClosed(deviceProfile):
	display.showStatusText(f'Channel closed for {deviceProfile.name}')


def heartRateData(hr, eventTime, interval):
	global heartRate
	heartRate = hr
	data_logging.writeHeartRateEvent(eventTime, heartRate)

def powerData(eventCount, pedalPowerRatio, cadence, accumulatedPower, instantaneousPower):
	global power
	power = instantaneousPower
	ratio = '' if pedalPowerRatio is None else pedalPowerRatio
	data_logging.writePowerEvent(0, instantaneousPower, accumulatedPower, ratio, cadence)

def torqueAndPedalData(eventCount, leftTorque, rightTorque, leftPedalSmoothness, rightPedalSmoothness):
	data_logging.writeTorqueEvent(0, leftTorque, rightTorque, leftPedalSmoothness, rightPedalSmoothness)


def getCPUTemperature():
	tempString = os.popen('cat /sys/class/thermal/thermal_zone0/temp').readline()
	return 0 if tempString == '' else int(tempString) / 1000.0



data_logging.openFiles()
display.start()


print('Starting up...')
antNode = Node(driver.USB2Driver())
try:
	antNode.start()
	network = Network(key=NETWORK_KEY_ANT_PLUS, name='N:ANT+')
	antNode.setNetworkKey(NETWORK_NUMBER_PUBLIC, network)
	print('Done.')

	heartRateMonitor = HeartRate(antNode, network,
	                     {'onDevicePaired': devicePaired,
	                      'onSearchTimeout': searchTimedOut,
	                      'onChannelClosed': channelClosed,
	                      'onHeartRateData': heartRateData})
	powerMonitor = BicyclePower(antNode, network,
	                     {'onDevicePaired': powerMonitorPaired,
	                      'onSearchTimeout': searchTimedOut,
	                      'onChannelClosed': channelClosed,
	                      'onPowerData': powerData,
	                      'onTorqueAndPedalData': torqueAndPedalData})

	heartRateMonitor.open(ChannelID(*config.heartRatePairing))
	powerMonitor.open(ChannelID(*config.powerPairing))
except ANTException as err:
	display.showStatusText(f'Could not start ANT.\n{err}')


print('Connecting to GPS service...')
gpsd.connect()
time.sleep(1)
print('Done.')


display.updateSpeedAndDistance(None, None)

counter = 0
while True:
	try:
		#TODO: lock powerUpdateMutex?
		display.drawPowerBar(power, config.powerGoal, config.powerRange, config.powerIdealRange)

		# Check GPS stuff once a second. But give it some time to start up first.
		if counter > 200 and counter % 4 == 0:
			try:
				info = gpsd.get_current()
				if info.mode >= 2 and info.sats_valid:  # Check if it has a fix on position
					data_logging.writeGPS(info)
					# TODO:
					#   - Store end lat,lon in config
					#   - Get (info.lat, info.lon)
					#   - Calculate distance in meters
					display.updateSpeedAndDistance(info.hspeed, 0)
				else:
					display.updateSpeedAndDistance(None, None)
					if counter < 600 and counter % 32 == 0:
						gspWarning = display.updateStatusText(gspWarning, 'GPS cannot get a fix on location',
					                                          level='warning', timeout=10)
			except UserWarning as e:
				print(e)

		# Update heart rate once a second
		if counter % 4 == 0:
			display.updateHeartRate(heartRate)

		# Check CPU temperature once every 8 second
		if counter % 32 == 0:
			temperature = getCPUTemperature()

			## For diagnostics
			data_logging.writeCPUTemperature(temperature)
			################

			if temperature > cpuWarnTemperature:
				statusLevel = 'error' if temperature > cpuBadTemperature else 'warning'
				tempWarning = display.updateStatusText(tempWarning, f'CPU temperature at {temperature}°C',
				                                       level=statusLevel, timeout=10)

		counter = counter + 1

		# NOTE: If this time is changed, all the modulo operands will have to be changed too.
		time.sleep(0.250)  # 250ms
	except KeyboardInterrupt:
		break


print('Shutting down...')
data_logging.closeFiles()
try:
	antNode.stop()
	print('Done.')
except ANTException as err:
	print(f'Could not stop ANT.\n{err}')
display.stop()