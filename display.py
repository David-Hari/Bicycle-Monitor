"""

  General functions for displaying things

"""

from threading import Timer
from recordclass import recordclass  # pip3 install recordclass
from PIL import Image, ImageDraw, ImageFont
import picamera

import config


StatusOverlay = recordclass('StatusOverlay', 'overlay timer yPos')

fontPath = '/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf'
statusFont = ImageFont.truetype(fontPath, 30)
powerBarFont = ImageFont.truetype(fontPath, 30)
statusOverlays = {}
statusIdCounter = 0
statusBackgroundColour = (20,20,20,128)
statusColours = {
	'info': (255,255,255),
	'warning': (255,255,0),
	'error': (255,0,0)
}
powerBarOverlay = None

camera = picamera.PiCamera()
camera.exposure_mode = 'sports'  # To reduce motion blur
camera.framerate = 49  # Highest supported by mode 5
## For more information about camera modes, see
## https://picamera.readthedocs.io/en/release-1.13/fov.html#sensor-modes
## Note that the mini ("spy") camera only comes in a V1 module.


def start():
	global powerBarOverlay
	camera.start_preview()
	powerBarOverlay = addOverlay(Image.new('RGBA', (320, 240)), (20, 20, 320, 240))


def showStatusText(text, timeout=10, level='info'):
	"""
	Draws `text` near the bottom of the screen, then hides it after `timeout` seconds.
	"""
	global statusOverlays
	global statusBackgroundColour
	global statusColours

	print(text)  # For debugging/logging purposes

	image = Image.new('RGBA', (config.videoDisplayResolution[0], 160))
	draw = ImageDraw.Draw(image)
	width, height = draw.textsize(text, font=statusFont)
	width += 60  # Add some padding
	height += 40
	x = (config.videoDisplayResolution[0] - width) // 2
	draw.rectangle([x,0,x+width,height], fill=statusBackgroundColour)
	draw.text((x+30,20), text, font=statusFont, fill=statusColours[level])
	y = config.videoDisplayResolution[1] - image.height
	
	makeStatusTextImage(text, bg=statusBackgroundColour, fg=statusColours[level])
	
	status = StatusOverlay(
		overlay = addOverlay(image, (0, y, image.width, image.height))
		timer = Timer(timeout, hideStatusText, args=id)
		yPos = y
	)
	statusOverlays[statusIdCounter] = status
	statusIdCounter = statusIdCounter + 1
	status.timer.start()

def updateStatusText(id, text, timeout=10, level='info'):

	print(text)  # For debugging/logging purposes
	
	if id is None or id not in statusOverlays:
		return showStatusText(text, timeout, level)
	
	existingStatus = statusOverlays[id]
	


def hideStatusText(id):
	"""
	Hides the status text overlay.
	"""
	global statusOverlays
	if id in statusOverlays:
		camera.remove_overlay(statusOverlays[id].overlay)
		del statusOverlays[id]


def drawPowerBar(power, goalPower, powerRange, idealRange):
	"""
	Draws a bar graph indicating current power production.
	:param power: Current power in Watts
	:param goalPower: Power to try to achieve, in Watts
	:param powerRange: The high and low bounds of the bar chart, in Watts
	:param idealRange: The high and low bounds of the green (good) area, in Watts
	:return:
	"""
	spacing = 20  # Leave room for text at the top and bottom
	barHeight = powerBarOverlay.window[3] - (spacing * 2)
	image = Image.new('RGBA', powerBarOverlay.window[2:4])
	draw = ImageDraw.Draw(image)
	fullRange = powerRange * 2
	clampedPower = clamp(power, goalPower - powerRange, goalPower + powerRange)
	colour = (207,16,26)  # red
	if inThreshold(power, goalPower, idealRange):
		colour = (31,160,70)  # green
	mid = (barHeight // 2) + spacing
	y = (((goalPower + powerRange) - clampedPower) / fullRange * barHeight) + spacing
	draw.rectangle([60,mid,140,y], fill=colour)
	drawShadowedText(draw, (5,mid-16), str(goalPower), font=powerBarFont, fill=(255,255,255))
	drawShadowedText(draw, (145,y-16), str(power), font=powerBarFont, fill=(255,255,255))
	updateOverlay(powerBarOverlay, image)



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


def makeStatusTextImage(text, bg, fg):
	"""
	Creates an image and draws the given text to it.
	"""
	image = Image.new('RGBA', (config.videoDisplayResolution[0], 160))
	draw = ImageDraw.Draw(image)
	width, height = draw.textsize(text, font)
	width += 60  # Add some padding
	height += 40
	x = (config.videoDisplayResolution[0] - width) // 2
	draw.rectangle([x,0,x+width,height], fill=bg)
	drawShadowedText(draw, (x+30,20), text, font=statusFont, fill=fg)
	y = config.videoDisplayResolution[1] - image.height
	return image


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


def inThreshold(value, goal, threshold):
	return goal - threshold < value < goal + threshold
