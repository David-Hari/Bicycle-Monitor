
/* Digital pins */
const int UP_BUTTON_PIN = 2;
const int DOWN_BUTTON_PIN = 3;
const int SERVO_PIN = 4;

/* Analog pins */
const int FEEDBACK_PIN_1 = 4;
const int FEEDBACK_PIN_2 = 5;

/* Config */
const int MAX_GEARS = 6;
const int GEAR_CHANGE_DELAY = 5;   // Milliseconds to delay for each degree moved

const int E_NO_POSITION = -1;
const int E_NOT_ALIGNED = -2;
const String E_MSG_NO_POSITION = "Gear not in correct position";
const String E_MSG_NOT_ALIGNED = "Servo motors not aligned (different positions)";


struct Button {
	int pin;
	int state;
};


void sendGearChanged(int gear);
void checkError(int num);
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