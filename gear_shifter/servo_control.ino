
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


Servo servo;

/*************************************************************************/
/* Start sending pulses to the servo to control it.                      */
/*************************************************************************/
void initializeServo() {
	servo.attach(SERVO_PIN);
}

/*************************************************************************/
/* Move the servo motor to the <toGear> position, assuming it is         */
/* currently in the <fromGear> position.                                 */
/*************************************************************************/
void moveServo(int fromGear, int toGear) {
	int currentAngle = gearPositions[fromGear-1];  // TODO: Read actual angle and verify
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