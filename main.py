"""

  Monitors data from ANT+ devices and displays information on screen.

"""

import os
import time
import math
from ant.core import driver
from ant.core.node import Node, Network, ChannelID
from ant.core.constants import *
from ant.core.exceptions import *
from ant.plus.heartrate import *
from ant.plus.power import *
import picamera
import gpsd

import config
import display
import recording


power = 0
heartRate = 0
cpuWarnTemperature = 80  # Degrees C
cpuBadTemperature = 90


#-------------------------------------------------#
#  ANT Callbacks                                  #
#-------------------------------------------------#

def devicePaired(deviceProfile, channelId):
	showMessage(f'Connected to {deviceProfile.name} ({channelId.deviceNumber})')

def powerMonitorPaired(deviceProfile, channelId):
	devicePaired(deviceProfile, channelId)
	deviceProfile.setCrankLength(config.crankLength)

def searchTimedOut(deviceProfile):
	showMessage(f'Could not connect to {deviceProfile.name}')

def channelClosed(deviceProfile):
	print(f'Channel closed for {deviceProfile.name}')


def heartRateData(hr, eventTime, interval):
	global heartRate
	heartRate = hr
	recording.writeHeartRateEvent(eventTime, heartRate)

def powerData(eventCount, pedalPowerRatio, cadence, accumulatedPower, instantaneousPower):
	global power
	power = instantaneousPower
	ratio = '' if pedalPowerRatio is None else pedalPowerRatio
	recording.writePowerEvent(0, instantaneousPower, accumulatedPower, ratio, cadence)

def torqueAndPedalData(eventCount, leftTorque, rightTorque, leftPedalSmoothness, rightPedalSmoothness):
	recording.writeTorqueEvent(0, leftTorque, rightTorque, leftPedalSmoothness, rightPedalSmoothness)



#-------------------------------------------------#
#  Miscellaneous functions                        #
#-------------------------------------------------#

def showMessage(string):
	print(string)
	display.showStatusText(string)

def getCPUTemperature():
	tempString = os.popen('cat /sys/class/thermal/thermal_zone0/temp').readline()
	return 0 if tempString == '' else int(tempString) / 1000.0

def dist(a, b):
	"""
	Calculates distance between two positions.

	:param a: First position as (latitude,longitude) tuple, in degrees
	:param b: Second position as (latitude,longitude) tuple, in degrees
	:return: Distance in meters
	"""
	φ1 = math.radians(a[0])
	φ2 = math.radians(b[0])
	Δλ = math.radians(b[1] - a[1])
	x = Δλ * math.cos((φ1+φ2)/2)
	y = φ2-φ1
	return math.hypot(x, y) * 6371000 # Mean earth radius



#-------------------------------------------------#
#  Initialization                                 #
#-------------------------------------------------#

recording.openFiles()

# https://github.com/dtreskunov/rpi-sensorium/commit/40c6f3646931bf0735c5fe4579fa89947e96aed7
#
# MMALPort has a bug in enable.wrapper, where it always calls
# self._pool.send_buffer(block=False) regardless of the port direction.
# This is in contrast to setup time when it only calls
# self._pool.send_all_buffers(block=False)
# if self._port[0].type == mmal.MMAL_PORT_TYPE_OUTPUT.
# Because of this bug updating an overlay once will log a MMAL_EAGAIN
# error every update. This is safe to ignore as we the user is driving
# the renderer input port with calls to update() that dequeue buffers
# and sends them to the input port (so queue is empty on when
# send_all_buffers(block=False) is called from wrapper).
# As a workaround, monkey patch MMALPortPool.send_buffer and
# silence the "error" if thrown by our overlay instance.
original_send_buffer = picamera.mmalobj.MMALPortPool.send_buffer
def silent_send_buffer(originalSelf, *args, **kwargs):
	try:
		original_send_buffer(originalSelf, *args, **kwargs)
	except picamera.exc.PiCameraMMALError as error:
		if error.status != 14:
			raise error
picamera.mmalobj.MMALPortPool.send_buffer = silent_send_buffer

## For more information about camera modes, see
## https://picamera.readthedocs.io/en/latest/fov.html#sensor-modes
## Note that the mini ("spy") camera only comes in a V1 module.
camera = picamera.PiCamera(sensor_mode=5)
camera.exposure_mode = 'sports'  # To reduce motion blur.
camera.framerate = 49  # Highest supported by mode 5

# Top camera is mounted upside down
camera.vflip = True
camera.hflip = True

display.start(camera)

showMessage('Starting up...')
antNode = Node(driver.USB2Driver())
try:
	antNode.start()
	network = Network(key=NETWORK_KEY_ANT_PLUS, name='N:ANT+')
	antNode.setNetworkKey(NETWORK_NUMBER_PUBLIC, network)

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

	heartRateMonitor.open(ChannelID(*config.heartRatePairing), searchTimeout=300)
	powerMonitor.open(ChannelID(*config.powerPairing), searchTimeout=300)
	showMessage('ANT started. Connecting to devices...')
except ANTException as err:
	showMessage(f'Could not start ANT.\n{err}')

showMessage('Connecting to GPS service...')
gpsd.connect()
time.sleep(1)

display.drawSpeedAndDistance(None, None)
recording.startRecordingVideo(camera)



#-------------------------------------------------#
#  Main loop                                      #
#-------------------------------------------------#

counter = 0
isGpsActive = False
tempWarning = None
gspMessage = None
while True:
	try:
		display.drawPowerBar(power, config.powerGoal, config.powerRange, config.powerIdealRange)

		# Check to see if GPS is active. Give it some time to start up first.
		if not isGpsActive and counter > 40 and counter % 8 == 0:
			try:
				info = gpsd.get_current()
				if info.mode >= 2 and info.sats_valid:  # Check if it has a fix on position
					isGpsActive = True
			except Exception as e:
				gspMessage = display.updateStatusText(gspMessage, str(e), level='warning')

		# Get GPS info once a second after we have a fix
		if isGpsActive and counter % 4 == 0:
			try:
				info = gpsd.get_current()
				if info.mode >= 2 and info.sats_valid:  # Make sure we still have a fix
					recording.writeGPS(info)
					distanceToFinish = dist((info.lat, info.lon), config.finishPosition)
					display.drawSpeedAndDistance(info.hspeed, distanceToFinish)
				else:
					display.drawSpeedAndDistance(None, None)
					isGpsActive = False
			except Exception as e:
				gspMessage = display.updateStatusText(gspMessage, str(e), level='error')

		# Update heart rate once a second
		if counter % 4 == 0:
			display.drawHeartRate(heartRate)

		# Check CPU temperature once every 8 second
		if counter % 32 == 0:
			temperature = getCPUTemperature()

			## For diagnostics
			#data_logging.writeCPUTemperature(temperature)
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


showMessage('Shutting down...')
recording.stopRecordingVideo(camera)
recording.closeFiles()
try:
	antNode.stop()
except ANTException as err:
	showMessage(f'Could not stop ANT.\n{err}')
display.stop()
