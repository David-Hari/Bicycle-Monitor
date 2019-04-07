"""

Monitors data from ANT+ devices and displays information on screen.

"""

import time
from threading import Timer
import picamera
from PIL import Image, ImageDraw, ImageFont
from ant.core import driver
from ant.core.node import Node, Network, ChannelID
from ant.core.constants import *
from ant.plus.heartrate import *
from ant.plus.power import *

import config


heartRateFile = open(config.heartRateFileName, 'w', encoding='utf-8')
heartRateFile.write('Time,Heart Rate (bpm)')
powerFile = open(config.powerFileName, 'w', encoding='utf-8')
powerFile.write('Time,Instantaneous Power (W),Accumulated Power (W),Pedal Power Ratio,Cadence (rpm)')
torqueFile = open(config.torqueFileName, 'w', encoding='utf-8')
torqueFile.write('Time,Torque Effectiveness,,Pedal Smoothness,')
torqueFile.write(',left,right,left,right')


camera = picamera.PiCamera()
camera.exposure_mode = 'sports'  # To reduce motion blur
camera.framerate = 49  # Highest supported by mode 5
## For more information about camera modes, see
## https://picamera.readthedocs.io/en/release-1.13/fov.html#sensor-modes

fontPath = '/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf'
statusFont = ImageFont.truetype(fontPath, 30)
powerBarFont = ImageFont.truetype(fontPath, 30)

statusTimer = None
statusOverlay = None
powerBarOverlay = None



#################################################################
#                                                               #
#  General functions for displaying things                      #
#                                                               #
#################################################################

def addOverlay(cam, image, position):
    assert position[2] % 32 == 0 and position[3] % 16 == 0
    return cam.add_overlay(image.tobytes(), layer = 3, format = 'rgba',
                           size = image.size, fullscreen = False, window = position)

def displayStatusText(text, timeout=10):
    """
    Draws `text` near the bottom of the screen, then hides it after `timeout` seconds.
    """
    global statusTimer
    global statusOverlay
    if statusTimer is not None:
        statusTimer.cancel()

    image = Image.new('RGBA', (config.videoDisplayResolution[0], 160))
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=statusFont)
    width += 60  # Add some padding
    height += 40
    x = (config.videoDisplayResolution[0] - width) // 2
    draw.rectangle([x,0,x+width,height], fill=(20,20,20,128))
    draw.text((x+30,20), text, font=statusFont, fill=(255,255,255))

    hideStatusText()
    y = config.videoDisplayResolution[1] - image.height
    statusOverlay = addOverlay(camera, image, (0, y, image.width, image.height))
    statusTimer = Timer(timeout, hideStatusText)
    statusTimer.start()

def hideStatusText():
    global statusOverlay
    if statusOverlay is not None:
        camera.remove_overlay(statusOverlay)
        statusOverlay = None

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

def drawPowerBar(power):
    global powerBarOverlay
    spacing = 20  # Leave room for text at the top and bottom
    barHeight = powerBarOverlay.window[3] - (spacing * 2)
    image = Image.new('RGBA', powerBarOverlay.window[2:4])
    draw = ImageDraw.Draw(image)
    fullRange = config.powerRedRange * 2
    clampedPower = clamp(power, config.powerGoal - config.powerRedRange, config.powerGoal + config.powerRedRange)
    colour = (207,16,26)  # red
    if inThreshold(power, config.powerGoal, config.powerGreenRange):
        colour = (31,160,70)  # green
    mid = (barHeight // 2) + spacing
    y = (((config.powerGoal + config.powerRedRange) - clampedPower) / fullRange * barHeight) + spacing
    draw.rectangle([60,mid,140,y], fill=colour)
    drawShadowedText(draw, (5,mid-16), str(config.powerGoal), font=powerBarFont, fill=(255,255,255))
    drawShadowedText(draw, (145,y-16), str(power), font=powerBarFont, fill=(255,255,255))
    powerBarOverlay.update(image.tobytes())



#################################################################
#                                                               #
#  ANT callback functions                                       #
#                                                               #
#################################################################

def devicePaired(deviceProfile, channelId):
    print('Connected to %s (%s)' % (deviceProfile.name, channelId))

def powerMonitorPaired(deviceProfile, channelId):
    devicePaired(deviceProfile, channelId)
    deviceProfile.setCrankLength(config.crankLength)

def searchTimedOut(deviceProfile):
    msg = 'Time-out trying to connect to %s' % deviceProfile.name
    print(msg)
    displayStatusText(msg)

def channelClosed(deviceProfile):
    print('Channel closed for %s' % deviceProfile.name)

def heartRateData(heartRate, eventTime, interval):
    heartRateFile.write('%s,%s\n' % (eventTime, heartRate))

def powerData(eventCount, pedalDifferentiation, pedalPowerRatio,
              cadence, accumulatedPower, instantaneousPower):
    ratio = '' if pedalPowerRatio is None else pedalPowerRatio
    heartRateFile.write('%s,%s,%s,%s,%s\n' % (0, instantaneousPower, accumulatedPower, ratio, cadence))

    #TODO
    #lock power:
    #   power = instantaneousPower

def torqueAndPedalData(eventCount, leftTorque, rightTorque,
                       leftPedalSmoothness, rightPedalSmoothness):
    torqueFile.write('%s,%s,%s,%s,%s\n' % (0, leftTorque, rightTorque, leftPedalSmoothness, rightPedalSmoothness))



#################################################################
#                                                               #
#  Start doing stuff!                                           #
#                                                               #
#################################################################

powerBarOverlay = addOverlay(camera, Image.new('RGBA', (320, 240)), (20, 20, 320, 240))

camera.start_preview()

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
        #    drawPowerBar(power)
        time.sleep(1)
    except KeyboardInterrupt:
        break


print('Shutting down... ', end='')
heartRateFile.close()
antNode.stop()
print('Done')