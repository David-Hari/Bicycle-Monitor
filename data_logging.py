"""

  Handles logging data to file

"""

heartRateFileName = './data/heart-rate.csv'
powerFileName = './data/power.csv'
torqueFileName = './data/torque.csv'
gpsFileName = './data/location.csv'
cpuTemperatureFileName = './data/cpu_temperature.csv'
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

	heartRateFile = open(heartRateFileName, 'w', encoding='utf-8')
	heartRateFile.write('Time,Heart Rate (bpm)\n')
	powerFile = open(powerFileName, 'w', encoding='utf-8')
	powerFile.write('Time,Instantaneous Power (W),Accumulated Power (W),Pedal Right/Left Power Ratio,Cadence (rpm)\n')
	torqueFile = open(torqueFileName, 'w', encoding='utf-8')
	torqueFile.write('Time,Torque Effectiveness,,Pedal Smoothness,\n')
	torqueFile.write(',left,right,left,right\n')
	gpsFile = open(gpsFileName, 'w', encoding='utf-8')
	gpsFile.write('Time (UTC),Longitude,Latitude,Longitude Precision (m),Latitude Precision (m),Speed (m/s),Speed Precision\n')

	## For diagnostics
	cpuTemperatureFile = open(cpuTemperatureFileName, 'w', encoding='utf-8')
	################

def closeFiles():
	heartRateFile.close()
	powerFile.close()
	torqueFile.close()
	gpsFile.close()

	if cpuTemperatureFile:
		cpuTemperatureFile.close()


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
	gpsFile.write(str(info.lon))
	gpsFile.write(',')
	gpsFile.write(str(info.lat))
	gpsFile.write(',')
	gpsFile.write(str(info.error['x']))
	gpsFile.write(',')
	gpsFile.write(str(info.error['y']))
	gpsFile.write(',')
	gpsFile.write(str(info.hspeed))
	gpsFile.write(',')
	gpsFile.write(str(info.error['s']))
	gpsFile.write('\n')


def writeCPUTemperature(temperature):
	cpuTemperatureFile.write(str(temperature))
	cpuTemperatureFile.write('\n')
