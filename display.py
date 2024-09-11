"""

  General functions for displaying things

"""

from threading import Timer, Lock
from PIL import Image, ImageDraw, ImageFont

import config


class StatusOverlay:
	def __init__(self, overlay, timer, yPos, height):
		self.overlay = overlay
		self.timer = timer
		self.yPos = yPos
		self.height = height


camera = None
fontPath = '/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf'
boldFontPath = '/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf'
heartImage = Image.open('./heart.png').convert('RGBA')
titleFont = ImageFont.truetype(boldFontPath, 60)
statusFont = ImageFont.truetype(fontPath, 35)
infoFont = ImageFont.truetype(fontPath, 80)
gearFont = ImageFont.truetype(fontPath, 160)
powerFont = ImageFont.truetype(fontPath, 40)
textPrimaryColour = (255, 255, 255)
textDimColour = (128, 128, 128)
statusBackgroundColour = (20, 20, 20, 128)
statusColours = {
	'info': (255, 255, 255),
	'warning': (255, 128, 0),
	'error': (255, 0, 0)
}
powerUnderColour = (207, 16, 26)
powerIdealColour = (31, 160, 70)
powerOverColour = (239, 122, 0)
statusOverlayHeight = 160   # Max height of image for overlay. Must be a multiple of 16.
statusPadding = 10          # Size between each status message, in pixels.
statusOverlays = {}
statusIdCounter = 0
overlaysMutex = Lock()
powerBarOverlay = None
gpsOverlay = None
heartRateOverlay = None
gearOverlay = None



def start(piCamera):
	global camera
	global powerBarOverlay
	global gpsOverlay
	global heartRateOverlay
	global gearOverlay

	camera = piCamera
	camera.start_preview(fullscreen=True)
	powerBarOverlay = addOverlay(Image.new('RGBA', (256, 240)), (10, 10, 256, 240))
	gpsOverlay = addOverlay(Image.new('RGBA', (512, 256)), (20, 800, 512, 256))
	heartRateOverlay = addOverlay(Image.new('RGBA', (256, 128)), (1780, 20, 256, 128))
	gearOverlay = addOverlay(Image.new('RGBA', (256, 256)), (1740, 860, 256, 256))


def stop():
	camera.stop_preview()


def showStatusText(text, timeout=10, level='info'):
	"""
	Draws status text near the bottom of the screen.
	Any existing status overlays still on screen will be pushed up.

	:param text: The text to show
	:param timeout: Text will be hidden after this many seconds
	:param level: Status level. One of: 'info', 'warning' or 'error'.
	:return: Id of the status that has been added to the screen.
	"""
	global statusOverlays
	global statusIdCounter

	image, size = makeStatusTextImage(text, statusColours[level])
	y = config.videoDisplayResolution[1] - size[1] - (statusPadding * 2)

	with overlaysMutex:
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

	:param statusId: ID of the existing status
	:param text: The new text to show
	:param timeout: Text will be hidden after this many seconds
	:param level: Status level if new overlay. One of: 'info', 'warning' or 'error'.
	:return: The id of the new or existing status
	"""
	if statusId is None:
		return showStatusText(text, timeout, level)

	with overlaysMutex:
		existingStatus = statusOverlays.get(statusId)
	if existingStatus is not None:
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

	with overlaysMutex:
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


def drawPower(power, goalPower):
	"""
	:param power: Current power in Watts.
	:param goalPower: Power to try to achieve, in Watts.
	"""
	global powerBarOverlay

	image = Image.new('RGBA', powerBarOverlay.window[2:4])
	draw = ImageDraw.Draw(image)

	textWidth1, textHeight1 = draw.textsize('Power', font=titleFont)
	textWidth2, textHeight2 = draw.textsize('000', font=powerFont)
	textWidth = max(textWidth1, textWidth2)
	textHeight = textHeight1 + textHeight2

	draw.rectangle((0, 0, textWidth+40, textHeight+60), fill=statusBackgroundColour)
	drawShadowedText(draw, (20, 10), 'Power', font=titleFont)
	drawShadowedText(draw, (105, textHeight1+35), str(int(power)), font=powerFont, align='r')
	updateOverlay(powerBarOverlay, image)


def drawSpeedAndDistance(speed, distance):
	"""
	:param speed: Speed in meters per second.
	:param distance: Distance to end in meters.
	"""
	global gpsOverlay

	image = Image.new('RGBA', gpsOverlay.window[2:4])
	draw = ImageDraw.Draw(image)

	drawShadowedText(draw, (0, 0), 'Speed', font=titleFont)
	kmhText = '--' if speed is None else str(int(speed*3.6))
	mphText = '--' if speed is None else str(int(speed*2.237))
	drawShadowedText(draw, (2, 70), kmhText + ' km/h', font=infoFont)
	drawShadowedText(draw, (2, 160), mphText + ' mph', font=infoFont)

	# Disable drawing distance for now.
	#drawShadowedText(draw, (200, 0), 'Dist.', font=titleFont)
	#kmText = '--' if distance is None else '{0:.2f}'.format(distance/1000)
	#miText = '--' if distance is None else '{0:.2f}'.format(distance/1609.344)
	#drawShadowedText(draw, (202, 50), kmText + ' km', font=infoFont)
	#drawShadowedText(draw, (202, 90), miText + ' mi.', font=infoFont)

	updateOverlay(gpsOverlay, image)


def drawHeartRate(heartRate):
	"""
	:param heartRate:
	"""
	global heartRateOverlay

	image = Image.new('RGBA', heartRateOverlay.window[2:4])
	image.paste(heartImage, (0, 3, 40, 43))
	draw = ImageDraw.Draw(image)
	drawShadowedText(draw, (45, 2), str(int(heartRate)), font=infoFont)
	updateOverlay(heartRateOverlay, image)


def drawGearNumber(gear, isChanging=False):
	"""
	:param gear: The number of gear the bike is currently in.
	:param isChanging: True if the bike is in the process of changing to this gear.
	"""
	global gearOverlay

	image = Image.new('RGBA', gearOverlay.window[2:4])
	draw = ImageDraw.Draw(image)
	text = str(gear)
	textWidth, textHeight = draw.textsize(text, font=gearFont)
	textColour = textDimColour if isChanging else textPrimaryColour
	draw.rectangle((0, 0, textWidth+60, textHeight+40), fill=statusBackgroundColour)
	drawShadowedText(draw, (30, 0), text, fill=textColour, font=gearFont)
	updateOverlay(gearOverlay, image)



### Private methods ###

def addOverlay(image, position):
	"""
	Adds a region of the screen that can be drawn to.

	:param image: Initial image to draw.
	:param position: x,y position of the top-left corner of the overlay.
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
	image = Image.new('RGBA', (config.videoDisplayResolution[0], statusOverlayHeight))
	draw = ImageDraw.Draw(image)
	textWidth, textHeight = draw.textsize(text, font=statusFont)
	textWidth += 60  # Add some padding
	textHeight += 40
	x = (config.videoDisplayResolution[0] - textWidth) // 2
	draw.rectangle((x, 0, x+textWidth, textHeight), fill=statusBackgroundColour)
	drawShadowedText(draw, (x+30, 20), text, font=statusFont, fill=colour)
	return image, (textWidth, textHeight)


def drawShadowedText(draw, position, text, font, fill=textPrimaryColour, shadow=(0, 0, 0), align='l'):
	x = position[0]
	y = position[1]
	r = 3
	anchor = align + 'a'  # 'a' = ascender, 'l'/'r' = left/right
	draw.text((x, y-r), text, font=font, fill=shadow, anchor=anchor)
	draw.text((x+r, y), text, font=font, fill=shadow, anchor=anchor)
	draw.text((x, y+r), text, font=font, fill=shadow, anchor=anchor)
	draw.text((x-r, y), text, font=font, fill=shadow, anchor=anchor)
	draw.text(position, text, font=font, fill=fill, anchor=anchor)


def clamp(value, minValue, maxValue):
	return min(max(value, minValue), maxValue)
