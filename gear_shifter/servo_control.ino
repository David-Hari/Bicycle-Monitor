
const int gearPositions[] = {
	10,  // 1st gear
	32,  // 2nd gear
	54,  // 3rd gear
	76,  // 4th gear
	98,  // 5th gear
	120, // 6th gear
	142  // 7th gear
};
static_assert((sizeof(gearPositions)/sizeof((gearPositions)[0])) == MAX_GEARS, "Number of elements in gearPositions[] does not match MAX_GEARS");

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
	// TODO: Read current angle and verify
	servo.attach(SERVO_PIN, SERVO_MIN_PULSE, SERVO_MAX_PULSE);
}

/*************************************************************************/
/* Reads the current position of the servo, averaging it over a number   */
/* of reads to avoid noise.                                              */
/*************************************************************************/
int readAngle() {
	int value = 0;
	const int NUM_READS = 5;
	for (int i = 0; i < NUM_READS; i++) {
		delay(10);
		value += analogRead(FEEDBACK_PIN);
	}
	int average = value / NUM_READS;
	return map(average, ANALOG_MIN, ANALOG_MAX, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE);
}

/*************************************************************************/
/* Returns the currently selected gear, or -1 if the servo position does */
/* not correspond to any gear.                                           */
/*************************************************************************/
int readGear() {
	return 1;  // TODO: Read current angle to determine gear
}

/*************************************************************************/
/* Move the servo motor to the <toGear> position, assuming it is         */
/* currently in the <fromGear> position.                                 */
/*************************************************************************/
void changeGear(int fromGear, int toGear) {
	int currentAngle = gearPositions[fromGear-1];  // TODO: Read actual angle and fail if it doesn't match
	int newAngle = gearPositions[toGear-1];
	if (newAngle >= currentAngle) {
		for (int angle = currentAngle; angle <= newAngle; angle++) {
			moveServo(angle);
			delay(10);
		}
	}
	else {
		for (int angle = currentAngle; angle >= newAngle; angle--) {
			moveServo(angle);
			delay(10);
		}
	}
}

/*************************************************************************/
/* Move the servo motor to the given angle.                              */
/*************************************************************************/
void moveServo(int angle) {
	if (angle < 0) { angle = 0; } else if (angle > SERVO_MAX_ANGLE) { angle = SERVO_MAX_ANGLE; }
	servo.writeMicroseconds(map(angle, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE, SERVO_MIN_PULSE, SERVO_MAX_PULSE));
}
