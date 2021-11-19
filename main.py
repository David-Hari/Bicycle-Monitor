"""

  Monitors data from ANT+ devices and displays information on screen.

"""

import time
import math
from serial import Serial

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


# Gear changer message codes
STARTUP_MSG        = 'S';
SHUTDOWN_MSG       = 'X';
ACKNOWLEDGE_MSG    = 'A';
ERROR_MSG          = 'E';
DEBUG_MSG          = 'D';
GEAR_CHANGING_MSG  = 'C';
GEAR_CHANGED_MSG   = 'G';

original_send_buffer = None
tempMessage = None
gpsMessage = None
gearMessage = None
gearComms = None
heartRateMonitor = None
powerMonitor = None
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
	recording.log(f'Channel closed for {deviceProfile.name}')


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
#  Message functions                              #
#-------------------------------------------------#

def showMessage(string, err=None):
	if err: recording.log(string + '    ' + str(err))
	else: recording.log(string)
	display.showStatusText(string, level=('error' if err is not None else 'info'))


def showHighTemperatureMessage(value):
	global tempMessage
	statusLevel = 'error' if temperature > cpuBadTemperature else 'warning'
	string = f'CPU temperature at {value}°C'
	recording.log(string)
	tempMessage = display.updateStatusText(tempMessage, string, level=statusLevel)


def showGpsMessage(string, level):
	global gpsMessage
	recording.log(string)
	gpsMessage = display.updateStatusText(gpsMessage, string, level=level)


def showGearMessage(string, err=None, level='info'):
	global gearMessage
	if err: recording.log(string + '    ' + str(err))
	else: recording.log(string)
	gearMessage = display.updateStatusText(gearMessage, string, level)



#-------------------------------------------------#
#  Gear shifter functions                         #
#-------------------------------------------------#

def readFromGearShifter():
	"""
	Attempts to read from the gear shifter, connecting to it if not already connected.

	:return: data or None if there is no data available
	"""
	global gearComms

	if gearComms is None:
		try:
			# A timeout of 0 means non-blocking mode, read() returns immediately with whatever is in the buffer.
			gearComms = Serial('/dev/serial/by-id/usb-Arduino_LLC_Arduino_Micro-if00', 9600, timeout=0)
			gearComms.write(STARTUP_MSG.encode('utf-8'))
		except Exception as error:
			showGearMessage('Could not connect to gear shifter.', error, level='error')
			return None

	try:
		numBytes = gearComms.in_waiting  # This throws if not connected
		if numBytes > 1:
			return gearComms.read(numBytes)
	except Exception as error:
		showGearMessage('Could not read from gear shifter. Attempting to reconnect.', error, level='error')
		try:
			gearComms.close()
			gearComms.open()
			gearComms.write(STARTUP_MSG.encode('utf-8'))
		except Exception as error2:
			showGearMessage('Could not connect to gear shifter.', error2, level='error')

	return None


def handleGearShifterComms(data):
	"""
	Read serial communication from gear shifter.
	Update the gear number if necessary, and display any errors.

	:param data: Bytes from the serial port
	"""
	# Perhaps make the gear number go grey when gear is changing.
	# Send 'C<num>' from Arduino, where <num> is the new gear.
	# drawGearNumber could accept an isChanging parameter.
	buffer = data.decode('utf-8')
	for line in filter(None, buffer.split('\n')):
		commsType, value = line[:1], line[1:]
		if commsType == GEAR_CHANGED_MSG:
			display.drawGearNumber(int(value))
		elif commsType == ACKNOWLEDGE_MSG:
			recording.log(f'Gear shifter acknowledged message. Response: {value}')
		else:
			level = 'info'
			if commsType == ERROR_MSG:
				level = 'error'
			elif commsType == DEBUG_MSG:
				level = 'debug'
			showGearMessage(f'Gear shifter: {value}', level=level)



#-------------------------------------------------#
#  Miscellaneous functions                        #
#-------------------------------------------------#

def getCPUTemperature():
	with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
		tempString = f.read()
		temp = 0 if tempString == '' else int(tempString) / 1000.0
	return temp


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
def patchPiCamera():
	global original_send_buffer
	original_send_buffer = picamera.mmalobj.MMALPortPool.send_buffer
	def silent_send_buffer(originalSelf, *args, **kwargs):
		try:
			original_send_buffer(originalSelf, *args, **kwargs)
		except picamera.exc.PiCameraMMALError as error:
			if error.status != 14:
				raise error
	picamera.mmalobj.MMALPortPool.send_buffer = silent_send_buffer



#-------------------------------------------------#
#  Initialization                                 #
#-------------------------------------------------#

recording.openFiles()

patchPiCamera()

## For more information about camera modes, see
## https://picamera.readthedocs.io/en/latest/fov.html#sensor-modes
## Note that the mini ("spy") camera only comes in a V1 module.
camera = picamera.PiCamera(sensor_mode=5)
camera.exposure_mode = 'sports'  # To reduce motion blur.
camera.framerate = 49  # Highest supported by mode 5


display.start(camera)

showMessage('Starting up ANT...')
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
except ANTException as error:
	showMessage('Could not start ANT.', error)

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
while True:
	try:
		# Update the power info on display
		display.drawPowerBar(power, config.powerGoal, config.powerRange, config.powerIdealRange)

		# Check to see if GPS is active. Give it some time to start up first.
		if not isGpsActive and counter > 40 and counter % 8 == 0:
			try:
				info = gpsd.get_current()
				if info.mode >= 2 and info.sats_valid:  # Check if it has a fix on position
					isGpsActive = True
			except Exception as e:
				showGpsMessage(str(e), level='warning')

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
				showGpsMessage(str(e), level='error')

		# Update heart rate once a second
		if counter % 4 == 0:
			display.drawHeartRate(heartRate)

		# Read serial communication from gear shifter, and update display if necessary
		gearData = readFromGearShifter()
		if gearData is not None:
			handleGearShifterComms(gearData)

		# Check CPU temperature once every 8 second
		if counter % 32 == 0:
			temperature = getCPUTemperature()

			## For diagnostics
			#recording.writeCPUTemperature(temperature)
			################

			if temperature > cpuWarnTemperature:
				showHighTemperatureMessage(temperature)

		counter = counter + 1

		# NOTE: If this time is changed, all the modulo operands will have to be changed too.
		time.sleep(0.250)  # 250ms
	except KeyboardInterrupt:
		break



recording.log('Shutting down...')

if gearComms is not None:
	try:
		gearComms.write(SHUTDOWN_MSG.encode('utf-8'))
	except Exception as error:
		recording.log('Could not safely stop gear shifter.    ' + str(error))

try:
	recording.stopRecordingVideo(camera)
except Exception as error:
	recording.log('Error during video recording.    ' + str(error))

try:
	if heartRateMonitor is not None:
		heartRateMonitor.close()
	if powerMonitor is not None:
		powerMonitor.close()
	antNode.stop()
except ANTException as error:
	recording.log('Could not stop ANT.    ' + str(error))

display.stop()
recording.closeFiles()
