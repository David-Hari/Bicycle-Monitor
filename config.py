
# Resolution of the display device (not the resolution that the camera is capturing at)
videoDisplayResolution = (1920, 1080)

# Resolution in which to record camera's output (not the resolution the camera is displaying)
videoRecordResolution = (1920, 1080)

# Channel IDs for each paired device. Set to None to enable searching.
heartRatePairing = (21741, 120, 1)
powerPairing = (2920, 11, 5)

# Files to log data to
heartRateFileName = "./heart-rate.csv"
powerFileName = "./power.csv"
torqueFileName = "./torque.csv"

# Bike parameters
crankLength = 145.0 #mm

powerGoal = 200 #Watts
powerGreenRange = 10 #+/- Watts, the high and low bounds of the green (good) area
powerRedRange = 50 #+/- Watts, the high and low bounds of the bar chart