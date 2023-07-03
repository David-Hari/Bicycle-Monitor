
#ifndef SERVO_CONTROL_H
#define SERVO_CONTROL_H


/* Digital pins */
const int SERVO_PIN = 4;

/* Analog pins */
const int FEEDBACK_PIN_1 = 4;
const int FEEDBACK_PIN_2 = 5;


/* Config */
const int gearPositions[] = {
	166, // 1st gear
	132, // 2nd gear
	 98, // 3rd gear
	 64, // 4th gear
	 41  // 5th gear
};
const int MAX_GEARS = (sizeof(gearPositions)/sizeof((gearPositions)[0]));
const int GEAR_CHANGE_DELAY = 50;         // Milliseconds to delay for each degree moved.
const int GEAR_CHANGE_WAIT_TIME = 500;    // Milliseconds to wait after changing to make sure gear is in correct position.
const int GEAR_POSITION_THRESHOLD = 8;    // Degrees +/- actual position.


void initializeServo();
void stopServo();
int readAngle1();
int readAngle2();
int getGearAtPosition(int angle);
int readGear();
boolean moveToGear(int toGear);
int moveToNearestGear();
void moveServo(int angle);
int clampAngle(int angle);


#endif   // SERVO_CONTROL_H