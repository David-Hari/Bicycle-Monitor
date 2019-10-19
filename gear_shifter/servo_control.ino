
const int gearPositions[] = {
	10,  // 1st gear
	32,  // 2nd gear
	54,  // 3rd gear
	76,  // 4th gear
	98,  // 5th gear
	120, // 6th gear
	142  // 7th gear
};

Servo servo;

void setupServo() {
	servo.attach(SERVO_PIN);
}

/*************************************************************************/
/* Move the servo motor to the given gear position.                      */
/*************************************************************************/
void moveServo(int gear) {
	servo.write(gearPositions[gear-1]);
}