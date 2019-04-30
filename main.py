"""

  Monitors data from ANT+ devices and displays information on screen.

"""

import time
from ant.core import driver
from ant.core.node import Node, Network, ChannelID
from ant.core.constants import *
from ant.plus.heartrate import *
from ant.plus.power import *

import config
import display
import data_logging




def devicePaired(deviceProfile, channelId):
	print(f'Connected to {deviceProfile.name} ({channelId})')

def powerMonitorPaired(deviceProfile, channelId):
	devicePaired(deviceProfile, channelId)
	deviceProfile.setCrankLength(config.crankLength)

def searchTimedOut(deviceProfile):
	msg = f'Time-out trying to connect to {deviceProfile.name}'
	print(msg)
	display.showStatusText(msg)

def channelClosed(deviceProfile):
	print(f'Channel closed for {deviceProfile.name}')

def heartRateData(heartRate, eventTime, interval):
	data_logging.writeHeartRateEvent(eventTime, heartRate)

def powerData(eventCount, pedalDifferentiation, pedalPowerRatio, cadence, accumulatedPower, instantaneousPower):
	ratio = '' if pedalPowerRatio is None else pedalPowerRatio
	data_logging.writePowerEvent(0, instantaneousPower, accumulatedPower, ratio, cadence)

	#TODO
	#lock power:
	#   power = instantaneousPower

def torqueAndPedalData(eventCount, leftTorque, rightTorque, leftPedalSmoothness, rightPedalSmoothness):
	data_logging.writeTorqueEvent(0, leftTorque, rightTorque, leftPedalSmoothness, rightPedalSmoothness)




data_logging.openFiles()
display.start()

print('Starting up... ', end='')
antNode = Node(driver.USB2Driver())
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

while True:
	try:
		#TODO
		#lock power:
		#    display.drawPowerBar(power, config.powerGoal, config.powerRange, config.powerIdealRange)
		time.sleep(1)
	except KeyboardInterrupt:
		break


print('Shutting down... ', end='')
data_logging.closeFiles()
antNode.stop()
print('Done')