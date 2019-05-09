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

import config
import display
import data_logging


cpuWarnTemperature = 80  # Degrees C
cpuBadTemperature = 90


def devicePaired(deviceProfile, channelId):
	display.showStatusText(f'Connected to {deviceProfile.name} ({channelId.deviceNumber})')

def powerMonitorPaired(deviceProfile, channelId):
	devicePaired(deviceProfile, channelId)
	deviceProfile.setCrankLength(config.crankLength)

def searchTimedOut(deviceProfile):
	display.showStatusText(f'Time-out trying to connect to {deviceProfile.name}')

def channelClosed(deviceProfile):
	display.showStatusText(f'Channel closed for {deviceProfile.name}')


def heartRateData(heartRate, eventTime, interval):
	data_logging.writeHeartRateEvent(eventTime, heartRate)

def powerData(eventCount, pedalDifferentiation, pedalPowerRatio, cadence, accumulatedPower, instantaneousPower):
	ratio = '' if pedalPowerRatio is None else pedalPowerRatio
	data_logging.writePowerEvent(0, instantaneousPower, accumulatedPower, ratio, cadence)

	#TODO
	#lock displayUpdateMutex:
	#   power = instantaneousPower   <-- calculate average since last displayed

def torqueAndPedalData(eventCount, leftTorque, rightTorque, leftPedalSmoothness, rightPedalSmoothness):
	data_logging.writeTorqueEvent(0, leftTorque, rightTorque, leftPedalSmoothness, rightPedalSmoothness)


def getCPUTemperature():
	tempString = os.popen('cat /sys/class/thermal/thermal_zone0/temp').readline()
	return int(tempString) / 1000.0



#displayUpdateMutex = something

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

	#heartRateMonitor.open(ChannelID(*config.heartRatePairing))
	powerMonitor.open(ChannelID(*config.powerPairing))
except ANTException as err:
	display.showStatusText(f'Could not start ANT.\n{err}')

tempWarning = None
counter = 0
while True:
	try:
		#TODO
		#lock displayUpdateMutex:
		#    display.drawPowerBar(power, config.powerGoal, config.powerRange, config.powerIdealRange)
		#    display.drawGPSStuff()

		# Check GPS stuff once a second
		#if counter % 32 == 0:
		#    gsp get speed
		#    update display

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
		time.sleep(0.250)  # 250ms
	except KeyboardInterrupt:
		break


print('Shutting down...')
data_logging.closeFiles()
try:
	antNode.stop()
	print('Done.')
except ANTException as err:
	display.showStatusText(f'Could not stop ANT.\n{err}')