
#ifndef SERVO_CONTROL_H
#define SERVO_CONTROL_H


/* Digital pins */
const int SERVO_PIN = 4;

/* Analog pins */
const int FEEDBACK_PIN_1 = 4;
const int FEEDBACK_PIN_2 = 5;

/* Config */
const int gearPositions[] = {
	  0, // 1st gear
	 42, // 2nd gear
	 84, // 3rd gear
	126, // 4th gear
	168  // 5th gear
};
const int MAX_GEARS = (sizeof(gearPositions)/sizeof((gearPositions)[0]));
const int GEAR_CHANGE_DELAY = 50;         // Milliseconds to delay for each degree moved.
const int GEAR_CHANGE_WAIT_TIME = 500;    // Milliseconds to wait after changing to make sure gear is in correct position.
const int GEAR_POSITION_THRESHOLD = 8;    // Degrees +/- actual position.


void initializeServo();
void stopServo();
int readAngle(int servoPin);
int getGearAtPosition(int angle);
int readGear();
boolean moveToGear(int toGear);
int moveToNearestGear();
void moveServo(int angle);


#endif   // SERVO_CONTROL_H