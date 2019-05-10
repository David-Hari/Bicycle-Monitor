"""

  Handles logging data to file

"""

heartRateFileName = './data/heart-rate.csv'
powerFileName = './data/power.csv'
torqueFileName = './data/torque.csv'
cpuTemperatureFileName = './data/cpu_temperature.csv'
heartRateFile = None
powerFile = None
torqueFile = None
cpuTemperatureFile = None


def openFiles():
	global heartRateFile
	global powerFile
	global torqueFile
	global cpuTemperatureFile

	heartRateFile = open(heartRateFileName, 'w', encoding='utf-8')
	heartRateFile.write('Time,Heart Rate (bpm)\n')
	powerFile = open(powerFileName, 'w', encoding='utf-8')
	powerFile.write('Time,Instantaneous Power (W),Accumulated Power (W),Pedal Power Ratio,Cadence (rpm)\n')
	torqueFile = open(torqueFileName, 'w', encoding='utf-8')
	torqueFile.write('Time,Torque Effectiveness,,Pedal Smoothness,\n')
	torqueFile.write(',left,right,left,right\n')
	cpuTemperatureFile = open(cpuTemperatureFileName, 'w', encoding='utf-8')

def closeFiles():
	heartRateFile.close()
	powerFile.close()
	torqueFile.close()


def writeHeartRateEvent(eventTime, heartRate):
	heartRateFile.write(f'{eventTime},{heartRate}\n')

def writePowerEvent(eventTime, instantaneousPower, accumulatedPower, ratio, cadence):
	powerFile.write(f'{eventTime},{instantaneousPower},{accumulatedPower},{ratio},{cadence}\n')

def writeTorqueEvent(eventTime, leftTorque, rightTorque, leftPedalSmoothness, rightPedalSmoothness):
	torqueFile.write(f'{eventTime},{leftTorque},{rightTorque},{leftPedalSmoothness},{rightPedalSmoothness}\n')

def writeCPUTemperature(temperature):
	cpuTemperatureFile.write(f'{temperature}\n')