"""

  Handles logging data to file

"""

import config


heartRateFile = None
powerFile = None
torqueFile = None


def openFiles():
	global heartRateFile
	global powerFile
	global torqueFile

	heartRateFile = open(config.heartRateFileName, 'w', encoding='utf-8')
	heartRateFile.write('Time,Heart Rate (bpm)\n')
	powerFile = open(config.powerFileName, 'w', encoding='utf-8')
	powerFile.write('Time,Instantaneous Power (W),Accumulated Power (W),Pedal Power Ratio,Cadence (rpm)\n')
	torqueFile = open(config.torqueFileName, 'w', encoding='utf-8')
	torqueFile.write('Time,Torque Effectiveness,,Pedal Smoothness,\n')
	torqueFile.write(',left,right,left,right\n')


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