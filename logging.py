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
	heartRateFile.write('Time,Heart Rate (bpm)')
	powerFile = open(config.powerFileName, 'w', encoding='utf-8')
	powerFile.write('Time,Instantaneous Power (W),Accumulated Power (W),Pedal Power Ratio,Cadence (rpm)')
	torqueFile = open(config.torqueFileName, 'w', encoding='utf-8')
	torqueFile.write('Time,Torque Effectiveness,,Pedal Smoothness,')
	torqueFile.write(',left,right,left,right')


def closeFiles():
	heartRateFile.close()
	powerFile.close()
	torqueFile.close()


def writeHeartRateEvent(eventTime, heartRate):
	heartRateFile.write('%s,%s\n' % (eventTime, heartRate))


def writePowerEvent(eventTime, instantaneousPower, accumulatedPower, ratio, cadence):
	powerFile.write('%s,%s,%s,%s,%s\n' % (eventTime, instantaneousPower, accumulatedPower, ratio, cadence))


def writeTorqueEvent(eventTime, leftTorque, rightTorque, leftPedalSmoothness, rightPedalSmoothness):
	torqueFile.write('%s,%s,%s,%s,%s\n' % (eventTime, leftTorque, rightTorque, leftPedalSmoothness, rightPedalSmoothness))