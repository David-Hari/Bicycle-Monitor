"""

  Handles logging data to file

"""

import os


baseDir = './data/'
heartRateFileName = 'heart-rate.csv'
powerFileName = 'power.csv'
torqueFileName = 'torque.csv'
gpsFileName = 'location.csv'
cpuTemperatureFileName = 'cpu_temperature.csv'
heartRateFile = None
powerFile = None
torqueFile = None
gpsFile = None
cpuTemperatureFile = None


def openFiles():
	global heartRateFile
	global powerFile
	global torqueFile
	global gpsFile
	global cpuTemperatureFile

	os.makedirs(baseDir)
	currentDir = makeUniqueDir(baseDir)

	heartRateFile = open(currentDir + heartRateFileName, 'w', encoding='utf-8')
	heartRateFile.write('Time,Heart Rate (bpm)\n')
	powerFile = open(currentDir + powerFileName, 'w', encoding='utf-8')
	powerFile.write('Time,Instantaneous Power (W),Accumulated Power (W),Pedal Right/Left Power Ratio,Cadence (rpm)\n')
	torqueFile = open(currentDir + torqueFileName, 'w', encoding='utf-8')
	torqueFile.write('Time,Torque Effectiveness,,Pedal Smoothness,\n')
	torqueFile.write(',left,right,left,right\n')
	gpsFile = open(currentDir + gpsFileName, 'w', encoding='utf-8')
	gpsFile.write('Time (UTC),Latitude,Longitude,Latitude Precision (m),Longitude Precision (m),Speed (m/s),Speed Precision\n')

	## For diagnostics
	#cpuTemperatureFile = open(currentDir + cpuTemperatureFileName, 'w', encoding='utf-8')
	################

def closeFiles():
	heartRateFile.close()
	powerFile.close()
	torqueFile.close()
	gpsFile.close()

	if cpuTemperatureFile:
		cpuTemperatureFile.close()

def makeUniqueDir(base):
	"""
	Creates a new directory with a unique number as it's name.
	:param base: The base directory to create it in
	:return: The full path to the new directory
	"""
	num = 1
	while True:
		try:
			os.mkdir(base + str(num))
			return base + str(num) + '/'
		except FileExistsError:
			num = num + 1


def writeHeartRateEvent(eventTime, heartRate):
	heartRateFile.write(str(eventTime))
	heartRateFile.write(',')
	heartRateFile.write(str(heartRate))
	heartRateFile.write('\n')

def writePowerEvent(eventTime, instantaneousPower, accumulatedPower, ratio, cadence):
	powerFile.write(str(eventTime))
	powerFile.write(',')
	powerFile.write(str(instantaneousPower))
	powerFile.write(',')
	powerFile.write(str(accumulatedPower))
	powerFile.write(',')
	powerFile.write(str(ratio))
	powerFile.write(',')
	powerFile.write(str(cadence))
	powerFile.write('\n')

def writeTorqueEvent(eventTime, leftTorque, rightTorque, leftPedalSmoothness, rightPedalSmoothness):
	torqueFile.write(str(eventTime))
	torqueFile.write(',')
	torqueFile.write(str(leftTorque))
	torqueFile.write(',')
	torqueFile.write(str(rightTorque))
	torqueFile.write(',')
	torqueFile.write(str(leftPedalSmoothness))
	torqueFile.write(',')
	torqueFile.write(str(rightPedalSmoothness))
	torqueFile.write('\n')

def writeGPS(info):
	gpsFile.write(str(info.get_time()))
	gpsFile.write(',')
	gpsFile.write(str(info.lat))
	gpsFile.write(',')
	gpsFile.write(str(info.lon))
	gpsFile.write(',')
	gpsFile.write(str(info.error['y']))
	gpsFile.write(',')
	gpsFile.write(str(info.error['x']))
	gpsFile.write(',')
	gpsFile.write(str(info.hspeed))
	gpsFile.write(',')
	gpsFile.write(str(info.error['s']))
	gpsFile.write('\n')


def writeCPUTemperature(temperature):
	cpuTemperatureFile.write(str(temperature))
	cpuTemperatureFile.write('\n')
