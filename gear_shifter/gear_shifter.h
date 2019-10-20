
const int UP_BUTTON_PIN = 2;
const int DOWN_BUTTON_PIN = 3;
const int SERVO_PIN = 4;
const int MAX_GEARS = 7;

int waitForInput();
void sendGearChanging();
void sendGearChanged(int gear);
void setupServo(int gear);
void moveServo(int fromGear, int toGear);