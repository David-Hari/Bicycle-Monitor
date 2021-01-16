
// Servo wires colours
//---------------------
// Brown  =  Ground
// Red    =  Power Supply
// Orange =  Control Signal


const int SERVO_MIN_ANGLE = 0;    // Degrees
const int SERVO_MAX_ANGLE = 172;
const int SERVO_MIN_PULSE = 500;  // Microseconds
const int SERVO_MAX_PULSE = 2500;

// Range of analog input from potentiometer.
// The full range of analog read is 0-1023, but it's less here because the max voltage is less than 5V.
// I actually measured a wider range when moving it by hand (21 (0.112V) to 649 (3.130V))
// but this is what the servo can actually do when sent the min/max pulses.
// Also note that the numbers are reversed, with the largest number representing 0 degrees.
const int ANALOG_MIN = 620;   // 0 degrees.
const int ANALOG_MAX = 60;    // 172 degrees.


Servo servo;

/*************************************************************************/
/* Start sending pulses to the servo to control it.                      */
/*************************************************************************/
void initializeServo() {
	servo.attach(SERVO_PIN, SERVO_MIN_PULSE, SERVO_MAX_PULSE);
}

/*************************************************************************/
/* Stop sending pulses to the servo. This SHOULD turn off the servo and  */
/* make it "limp", but it does not. Perhaps this brand holds even when   */
/* PWM signal stops.                                                     */
/*************************************************************************/
void stopServo() {
	servo.detach();
}

/*************************************************************************/
/* Read the current position of the servo at the given pin, averaging it */
/* over a number of reads to avoid noise.                                */
/*************************************************************************/
int readAngle(int pin) {
	int value = 0;
	const int NUM_READS = 5;
	for (int i = 0; i < NUM_READS; i++) {
		delay(10);
		value += analogRead(pin);
	}
	int average = value / NUM_READS;
	return map(average, ANALOG_MIN, ANALOG_MAX, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE);
}

/*************************************************************************/
/* Return the currently selected gear.                                   */
/* Error if the servo position does not correspond to any gear.          */
/*************************************************************************/
int readGear() {
	int gearAngle = 0;
	int currentAngle1 = readAngle(FEEDBACK_PIN_1);
	for (int i = 0; i < MAX_GEARS; i++) {
		gearAngle = gearPositions[i];
		if (currentAngle1 >= gearAngle - GEAR_POSITION_THRESHOLD && currentAngle1 <= gearAngle + GEAR_POSITION_THRESHOLD) {
			return i + 1;
		}
	}
	error("Gear not in correct position. Motor 1: " + String(currentAngle1) + "°, Motor 2: " + String(readAngle(FEEDBACK_PIN_2)) + "°");
	return -1;  // Should not normally reach here
}

/*************************************************************************/
/* Move the servo motor to the <toGear> position.                        */
/* Return the new gear number.                                           */
/* Error if the two motors are not in the same position at the end.      */
/*************************************************************************/
int changeGear(int toGear) {
	int currentAngle1, currentAngle2, newAngle;
	int currentGear = readGear();
	if (currentGear < 0) {
		return -1;
	}
	
	// Incrementally move the servo motors with delays in between to control their speed
	currentAngle1 = gearPositions[currentGear-1];
	newAngle = gearPositions[toGear-1];
	if (newAngle >= currentAngle1) {
		for (int angle = currentAngle1; angle <= newAngle; angle++) {
			moveServo(angle);
			delay(GEAR_CHANGE_DELAY);
		}
	}
	else {
		for (int angle = currentAngle1; angle >= newAngle; angle--) {
			moveServo(angle);
			delay(GEAR_CHANGE_DELAY);
		}
	}
	
	// Wait for servos to finish moving.
	long startWaitTime = millis();
	boolean isFinished1 = false;
	boolean isFinished2 = false;
	do {
		currentAngle1 = readAngle(FEEDBACK_PIN_1);
		currentAngle2 = readAngle(FEEDBACK_PIN_2);
		isFinished1 = currentAngle1 >= newAngle - GEAR_POSITION_THRESHOLD && currentAngle1 <= newAngle + GEAR_POSITION_THRESHOLD;
		isFinished2 = currentAngle2 >= newAngle - GEAR_POSITION_THRESHOLD && currentAngle2 <= newAngle + GEAR_POSITION_THRESHOLD;
	} while ((!isFinished1 || !isFinished2) && millis() - startWaitTime < GEAR_CHANGE_WAIT_TIME);

	// Error if one or both servos are still not at the correct angle after waiting.
	if (!isFinished1 || !isFinished2) {
		error("Servo motors not aligned. Gear: " + String(toGear) + ", Motor 1: " + String(currentAngle1) + "°, Motor 2: " + String(currentAngle2) + "°");
	}

	return readGear();
}

/*************************************************************************/
/* Move the servo motor to the given angle.                              */
/*************************************************************************/
void moveServo(int angle) {
	if (angle < 0) {
		angle = 0;
	}
	else if (angle > SERVO_MAX_ANGLE) {
		angle = SERVO_MAX_ANGLE;
	}
	servo.writeMicroseconds(map(angle, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE, SERVO_MIN_PULSE, SERVO_MAX_PULSE));
}
