
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
const int GEAR_CHANGE_DELAY = 50;         // Milliseconds to delay for each degree moved.
const int GEAR_CHANGE_WAIT_TIME = 500;    // Milliseconds to wait after changing to make sure gear is in correct position.
const int GEAR_POSITION_THRESHOLD = 8;    // Degrees +/- actual position.



struct Button {
	int pin;
	int state;
};


void error(String message);

void sendGearChanged(int gear);
void sendError(String message);
void sendMessage(String type, String message);

void initializeButtons();
boolean areBothButtonsDown();
int waitForInput();

void initializeServo();
void stopServo();
int readAngle(int servoPin);
int readGear();
boolean moveToGear(int toGear);
int moveToNearestGear();
void moveServo(int angle);