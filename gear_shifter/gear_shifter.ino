#include <Servo.h>


const int UP_BUTTON_PIN = 2;
const int DOWN_BUTTON_PIN = 3;
const int SERVO_PIN = 4;
const unsigned long lastDebounceTime = 0;  // Last time a button was pushed (input went LOW)
const unsigned long debounceDelay = 100;   // Milliseconds delay before detecting another push

int previousUpButtonState = HIGH;
int previousDownButtonState = HIGH;
int currentGear = 0;
Servo servo;


/*************************************************************************/
/* The setup function runs once when you press reset or power the board. */
/*************************************************************************/
void setup() {
	pinMode(LED_BUILTIN, OUTPUT);
	pinMode(UP_BUTTON_PIN, INPUT_PULLUP);
	//pinMode(DOWN_BUTTON_PIN, INPUT_PULLUP);
	Serial.begin(9600);
	//servo.attach(SERVO_PIN);
}

/*************************************************************************/
/* The main loop runs continuously.                                      */
/*************************************************************************/
void loop() {
	waitForInput();
	sendUpdate();
	moveServo();
}


/*************************************************************************/
/* Continuously check button state waiting for a press. Once pressed,    */
/* increment/decrement gear number and return.                           */
/*************************************************************************/
void waitForInput() {
	while(true) {
		if (checkUpButton()) {
			currentGear++;
			return;
		}
		else if (checkDownButton()) {
			currentGear--;
			return;
		}
		// NOTE: Delay is just a busy loop, so we might as well read the input
		// continuously without delay. But then we'd have to de-bounce it.
		delay(100);
	}
}

/*************************************************************************/
/* Send the current gear number over serial communication.               */
/*************************************************************************/
void sendUpdate() {
	Serial.println(currentGear);
}

/*************************************************************************/
/* Move the servo motor to the current gear position.                    */
/*************************************************************************/
void moveServo() {
}


/*************************************************************************/
/* Return true if the button has been pressed.                           */
/*************************************************************************/
boolean checkButton(const int pin, int &previousState) {
	int currentState = digitalRead(pin);

	// Check if button was pressed
	if (previousState == HIGH && currentState == LOW) {
		previousState = currentState;
		return true;
	}
	// Detect release as well (to maintain the correct state)
	if (previousState == LOW && currentState == HIGH) {
		previousState = currentState;
	}

	return false;
}

boolean checkUpButton() {
	return checkButton(UP_BUTTON_PIN, previousUpButtonState);
}

boolean checkDownButton() {
	return checkButton(DOWN_BUTTON_PIN, previousDownButtonState);
}


void turnOnLED() {
	digitalWrite(LED_BUILTIN, HIGH);
}

void turnOffLED() {
	digitalWrite(LED_BUILTIN, LOW);
}
