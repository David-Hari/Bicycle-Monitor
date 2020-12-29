
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

const int GEAR_POSITION_THRESHOLD = 4;     // Degrees +/- actual position
const int SERVO_ANGLE_DIFF_THRESHOLD = 1;  // Degrees +/- difference between both servos


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
/* Return the currently selected gear, or an error code if the servo     */
/* position does not correspond to any gear.                             */
/*************************************************************************/
int readGear() {
	int currentAngle1 = readAngle(FEEDBACK_PIN_1);
	int currentAngle2 = readAngle(FEEDBACK_PIN_2);
	int angleDiff = currentAngle1 - currentAngle2;
	if (angleDiff > SERVO_ANGLE_DIFF_THRESHOLD || angleDiff < -SERVO_ANGLE_DIFF_THRESHOLD) {
		return E_NOT_ALIGNED;
	}
	int gearAngle = 0;
	for (int i = 0; i < MAX_GEARS; i++) {
		gearAngle = gearPositions[i];
		if (currentAngle1 >= gearAngle - GEAR_POSITION_THRESHOLD && currentAngle1 <= gearAngle + GEAR_POSITION_THRESHOLD) {
			return i + 1;
		}
	}
	return E_NO_POSITION;
}

/*************************************************************************/
/* Move the servo motor to the <toGear> position.                        */
/* Return the new gear number or -1 on error.                            */
/*************************************************************************/
int changeGear(int toGear) {
	int currentGear = readGear();
	if (currentGear < 0) {
		return currentGear;  // Variable is error code
	}
	int currentAngle = gearPositions[currentGear-1];
	int newAngle = gearPositions[toGear-1];
	if (newAngle >= currentAngle) {
		for (int angle = currentAngle; angle <= newAngle; angle++) {
			moveServo(angle);
			delay(GEAR_CHANGE_DELAY);
			// TODO: Perhaps check both angles here too.
		}
	}
	else {
		for (int angle = currentAngle; angle >= newAngle; angle--) {
			moveServo(angle);
			delay(GEAR_CHANGE_DELAY);
		}
	}
	for (int i = 0; readGear() != toGear && i < 200; i++) {}  // Wait for gear to move
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
