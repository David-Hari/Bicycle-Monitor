
const int UP_BUTTON_PIN = 2;
const int DOWN_BUTTON_PIN = 3;
const int SERVO_PIN = 4;
const int FEEDBACK_PIN = 5;   // Analog pin
const int MAX_GEARS = 6;
const int GEAR_POSITION_THRESHOLD = 4;  // Degrees +/- actual position

const int E_NO_POSITION = -1;


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
int readAngle();
int readGear();
int changeGear(int toGear);
void moveServo(int angle);