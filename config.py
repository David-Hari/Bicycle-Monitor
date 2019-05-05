
# Resolution of the display device (not the resolution that the camera is capturing at)
videoDisplayResolution = (1920, 1080)

# Resolution in which to record camera's output (not the resolution the camera is displaying)
videoRecordResolution = (1920, 1080)

displayUpdateInterval = 0.250 # Seconds. How often to update data on screen

# Channel IDs for each paired device. Set to None to enable searching.
heartRatePairing = (21741, 120, 1)
powerPairing = (2920, 11, 5)

# Bike parameters
crankLength = 145.0 # mm

powerGoal = 200       # Watts. Power output to try to achieve
powerRange = 50       # Watts. Show this much more/less than the goal
powerIdealRange = 10  # Watts. Actual power output should be within this range
