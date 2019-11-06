
const int UP_BUTTON_PIN = 2;
const int DOWN_BUTTON_PIN = 3;
const int SERVO_PIN = 4;
const int FEEDBACK_PIN = 5;   // Analog pin
const int MAX_GEARS = 7;


struct Button {
	int pin;
	int state;
};


void sendGearChanging();
void sendGearChanged(int gear);

void initializeButtons();
int waitForInput();

void initializeServo(int gear);
int readAngle();
int readGear();
void changeGear(int fromGear, int toGear);
void moveServo(int angle);