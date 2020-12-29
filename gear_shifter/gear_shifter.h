
/* Digital pins */
const int UP_BUTTON_PIN = 2;
const int DOWN_BUTTON_PIN = 3;
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
const int GEAR_CHANGE_DELAY = 5;           // Milliseconds to delay for each degree moved
const int GEAR_POSITION_THRESHOLD = 4;     // Degrees +/- actual position
const int SERVO_ANGLE_DIFF_THRESHOLD = 4;  // Degrees difference between both servos



struct Button {
	int pin;
	int state;
};


void sendGearChanged(int gear);
void error(String message);
void sendError(String message);

void initializeButtons();
boolean areBothButtonsDown();
int waitForInput();

void initializeServo();
void stopServo();
int readAngle(int servoPin);
int readGear();
int changeGear(int toGear);
void moveServo(int angle);