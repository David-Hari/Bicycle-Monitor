
#ifndef SERVO_CONTROL_H
#define SERVO_CONTROL_H


/* Digital pins */
const int SERVO_PIN = 4;

/* Analog pins */
const int FEEDBACK_PIN_1 = 4;
const int FEEDBACK_PIN_2 = 5;


/* Config */
const int gearPositions[] = {
	169, // 1st gear
	140, // 2nd gear
	107, // 3rd gear
	 76, // 4th gear
	 46, // 5th gear
	 23  // 6th gear
};
const int MAX_GEARS = (sizeof(gearPositions)/sizeof((gearPositions)[0]));
const int GEAR_CHANGE_DELAY = 50;         // Milliseconds to delay for each degree moved.
const int GEAR_CHANGE_WAIT_TIME = 1000;   // Milliseconds to wait after changing to make sure gear is in correct position.
const int READ_ANGLE_THRESHOLD = 10;      // Degrees +/- relative to gear position that servos must be in to be considered in gear when reading.
const int MOVE_ANGLE_THRESHOLD = 8;       // Degrees +/- relative to gear that servos must be in to be considered moved to that gear.
const int ALIGNMENT_THRESHOLD = 6;        // Degrees +/- that each servo must be from each other to be considered aligned.


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