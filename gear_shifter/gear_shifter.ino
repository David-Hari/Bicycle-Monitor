#include <Servo.h>
#include "gear_shifter.h"


int currentGear = 0;


/*************************************************************************/
/* The setup function runs once when you press reset or power the board. */
/*************************************************************************/
void setup() {
	pinMode(LED_BUILTIN, OUTPUT);
	pinMode(UP_BUTTON_PIN, INPUT_PULLUP);
	pinMode(DOWN_BUTTON_PIN, INPUT_PULLUP);
	Serial.begin(9600);
	setupServo();
	currentGear = 1;
}

/*************************************************************************/
/* The main loop runs continuously.                                      */
/*************************************************************************/
void loop() {
	int change = waitForInput();
	currentGear += change;   // + or -, up or down
	if (currentGear > MAX_GEARS) {  // Bounds checking
		currentGear = MAX_GEARS;
	}
	else if (currentGear < 1) {
		currentGear = 1;
	}
	sendUpdate(currentGear);
	moveServo(currentGear);
}


/*************************************************************************/
/* Send the given gear number over serial communication.                 */
/*************************************************************************/
void sendUpdate(int gear) {
	Serial.println(gear);
}



void turnOnLED() {
	digitalWrite(LED_BUILTIN, HIGH);
}

void turnOffLED() {
	digitalWrite(LED_BUILTIN, LOW);
}
