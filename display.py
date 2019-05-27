"""

  General functions for displaying things

"""

from threading import Timer
from recordclass import recordclass
from PIL import Image, ImageDraw, ImageFont
import picamera

import config


StatusOverlay = recordclass('StatusOverlay', 'overlay timer yPos height')

camera = None
fontPath = '/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf'
boldFontPath = '/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf' #TODO
statusFont = ImageFont.truetype(fontPath, 35)
powerBarFont = ImageFont.truetype(fontPath, 35)
titleFont = ImageFont.truetype(boldFontPath, 35)
statusOverlayHeight = 160   # Max height of image for overlay. Must be a multiple of 16.
statusPadding = 10          # Size between each status message, in pixels.
statusBackgroundColour = (20,20,20,128)
statusColours = {
	'info': (255,255,255),
	'warning': (255,128,0),
	'error': (255,0,0)
}
statusOverlays = {}
statusIdCounter = 0
maxStatusOverlays = 4   # Don't flood the screen with messages
powerBarOverlay = None
gpsOverlay = None
heartRateOverlay = None
powerUnderColour = (207,16,26)
powerIdealColour = (31,160,70)
powerOverColour = (239, 122, 0)


def start():
	global camera
	global powerBarOverlay

	monkeyPatchPiCamera()

	## For more information about camera modes, see
	## https://picamera.readthedocs.io/en/latest/fov.html#sensor-modes
	## Note that the mini ("spy") camera only comes in a V1 module.
	camera = picamera.PiCamera(sensor_mode=5)
	#camera.exposure_mode = 'sports'  # To reduce motion blur. May not be needed.
	camera.framerate = 49  # Highest supported by mode 5

	camera.start_preview(fullscreen=True)
	powerBarOverlay = addOverlay(Image.new('RGBA', (320, 240)), (20, 20, 320, 240))


def stop():
	camera.stop_preview()


def showStatusText(text, timeout=10, level='info'):
	"""
	Draws status text near the bottom of the screen.
	Any existing status overlays still on screen will be pushed up.
	:param text: The text to show
	:param timeout: Text will be hidden after this many seconds
	:param level: Status level. One of: 'info', 'warning' or 'error'.
	:return: Id of the status that has been added to the screen
	"""
	global statusOverlays
	global statusIdCounter
	global statusColours
	global statusPadding

	print(text)  # For debugging/logging purposes

	image, size = makeStatusTextImage(text, statusColours[level])
	y = config.videoDisplayResolution[1] - size[1] - (statusPadding * 2)

	# Push existing overlays up to make room for this one
	for key, each in statusOverlays.items():
		each.yPos = each.yPos - size[1] - statusPadding
		w = each.overlay.window   # Tuple of x,y,w,h
		each.overlay.window = (w[0], each.yPos, w[2], w[3])

	thisId = statusIdCounter
	statusIdCounter = statusIdCounter + 1
	status = StatusOverlay(
		overlay = addOverlay(image, (0, y, image.width, image.height)),
		timer = Timer(timeout, hideStatusText, args=[thisId]),
		yPos = y,
		height = size[1]
	)
	statusOverlays[thisId] = status
	status.timer.start()

	return thisId


def updateStatusText(statusId, text, timeout=10, level='info'):
	"""
	Updates an existing status overlay with new text.
	If the overlay does not exist, a new one will be created.
	:param statusId: Id of the existing status
	:param text: The new text to show
	:param timeout: Text will be hidden after this many seconds
	:param level: Status level if new overlay. One of: 'info', 'warning' or 'error'.
	:return: The id of the new or existing status
	"""
	global statusColours

	print(text)  # For debugging/logging purposes

	if statusId is None or statusId not in statusOverlays:
		return showStatusText(text, timeout, level)

	existingStatus = statusOverlays[statusId]
	existingStatus.timer.cancel()
	image, size = makeStatusTextImage(text, statusColours[level])
	updateOverlay(existingStatus.overlay, image)
	existingStatus.timer = Timer(timeout, hideStatusText, args=[statusId])
	existingStatus.timer.start()

	return statusId


def hideStatusText(statusId):
	"""
	Hides a status text overlay.
	:param statusId: Id of the status to hide
	"""
	global statusOverlays

	if statusId in statusOverlays:
		existingStatus = statusOverlays[statusId]
		thisY = existingStatus.yPos
		thisHeight = existingStatus.height
		camera.remove_overlay(existingStatus.overlay)
		if existingStatus.timer:
			existingStatus.timer.cancel()  # Make sure timer is stopped
		del statusOverlays[statusId]

		# Move down any overlays above this one
		for key, each in statusOverlays.items():
			if each.yPos < thisY:
				each.yPos = each.yPos + thisHeight + statusPadding
				w = each.overlay.window   # Tuple of x,y,w,h
				each.overlay.window = (w[0], each.yPos, w[2], w[3])


def drawPowerBar(power, goalPower, powerRange, idealRange):
	"""
	Draws a bar graph indicating current power production.
	:param power: Current power in Watts
	:param goalPower: Power to try to achieve, in Watts
	:param powerRange: The high and low bounds of the bar chart, in Watts
	:param idealRange: The high and low bounds of the green (good) area, in Watts
	"""
	global powerBarOverlay
	global powerUnderColour
	global powerIdealColour
	global powerOverColour

	spacing = 20  # Leave room for text at the top and bottom
	barHeight = powerBarOverlay.window[3] - (spacing * 2)
	image = Image.new('RGBA', powerBarOverlay.window[2:4])
	draw = ImageDraw.Draw(image)
	fullRange = powerRange * 2
	clampedPower = clamp(power, goalPower - powerRange, goalPower + powerRange)
	mid = (barHeight // 2) + spacing
	y = ((goalPower + powerRange - clampedPower) / fullRange * barHeight) + spacing
	idealHeight = idealRange / fullRange * barHeight
	idealTop = mid - idealHeight
	idealBottom = mid + idealHeight
	draw.rectangle([75, idealTop, 125, idealBottom], fill=powerIdealColour)
	if power < goalPower - idealRange:
		draw.rectangle([75,idealBottom,125,y], fill=powerUnderColour)
	elif power > goalPower + idealRange:
		draw.rectangle([75,idealTop,125,y], fill=powerOverColour)
	draw.line([70,y,130,y], fill=(0,0,0), width=3)
	drawShadowedText(draw, (0,mid-20), str(goalPower), font=powerBarFont, fill=(255,255,255))
	drawShadowedText(draw, (140,y-20), str(int(power)), font=powerBarFont, fill=(255,255,255))
	updateOverlay(powerBarOverlay, image)


def updateSpeedAndDistance(speed, distance):
	"""
	Draws the speed on screen
	:param speed: Speed in meters per second
	:param distance: Distance to end in meters
	"""
	# TODO: Show speed and dist in both km and miles
	#  If None, draw '--'
	global gpsOverlay
	pass


def updateHeartRate(heartRate):
	"""
	Draws heart rate on screen
	:param heartRate:
	"""
	global heartRateOverlay
	pass



### Private methods ###

def addOverlay(image, position):
	"""
	Adds a region of the screen that can be drawn to.
	:param image: Initial image to draw
	:param position: x,y position of the top-left corner of the overlay
	:return: The overlay object
	"""
	assert position[2] % 32 == 0 and position[3] % 16 == 0
	return camera.add_overlay(image.tobytes(), layer = 3, format = 'rgba', size = image.size, fullscreen = False, window = position)


def updateOverlay(overlay, image):
	overlay.update(image.tobytes())


def makeStatusTextImage(text, colour):
	"""
	Creates an image and draws the given text to it.
	"""
	global statusFont
	global statusOverlayHeight
	global statusBackgroundColour

	image = Image.new('RGBA', (config.videoDisplayResolution[0], statusOverlayHeight))
	draw = ImageDraw.Draw(image)
	textWidth, textHeight = draw.textsize(text, font=statusFont)
	textWidth += 60  # Add some padding
	textHeight += 40
	x = (config.videoDisplayResolution[0] - textWidth) // 2
	draw.rectangle([x,0,x+textWidth,textHeight], fill=statusBackgroundColour)
	drawShadowedText(draw, (x+30,20), text, font=statusFont, fill=colour)
	return image, (textWidth, textHeight)


def drawShadowedText(draw, position, text, font, fill=(255,255,255), shadow=(0,0,0)):
	x = position[0]
	y = position[1]
	r = 3
	draw.text((x, y-r), text, font=font, fill=shadow)
	draw.text((x+r, y), text, font=font, fill=shadow)
	draw.text((x, y+r), text, font=font, fill=shadow)
	draw.text((x-r, y), text, font=font, fill=shadow)
	draw.text(position, text, font=font, fill=fill)


def clamp(value, minValue, maxValue):
	return min(max(value, minValue), maxValue)



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
def monkeyPatchPiCamera():
	original_send_buffer = picamera.mmalobj.MMALPortPool.send_buffer

	def silent_send_buffer(originalSelf, *args, **kwargs):
		try:
			original_send_buffer(originalSelf, *args, **kwargs)
		except picamera.exc.PiCameraMMALError as error:
			if error.status != 14:
				raise error

	picamera.mmalobj.MMALPortPool.send_buffer = silent_send_buffer