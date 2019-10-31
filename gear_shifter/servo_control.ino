
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

// Range of analog input from potentiometer (Full range of analog read is 0-1023).
const int ANALOG_MIN = 21;   // 0.112V
const int ANALOG_MAX = 649;  // 3.130V


Servo servo;

/*************************************************************************/
/* Start sending pulses to the servo to control it.                      */
/*************************************************************************/
void initializeServo() {
	servo.attach(SERVO_PIN, 500, 2500);
}

/*************************************************************************/
/* Reads the current position of the servo, averaging it over a number   */
/* of reads to avoid noise.                                              */
/*************************************************************************/
int readAnalogAverage() {
	int value = 0;
	for (int i = 0; i < 3; i++) {
		delay(10);
		value += analogRead(FEEDBACK_PIN);
	}
	return value / 3;
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
void moveServo(int fromGear, int toGear) {
	int currentAngle = gearPositions[fromGear-1];  // TODO: Read actual angle and fail if it doesn't match
	int newAngle = gearPositions[toGear-1];
	if (newAngle >= currentAngle) {
		for (int angle = currentAngle; angle <= newAngle; angle++) {
			servo.write(angle);
			delay(10);
		}
	}
	else {
		for (int angle = currentAngle; angle >= newAngle; angle--) {
			servo.write(angle);
			delay(10);
		}
	}
}
