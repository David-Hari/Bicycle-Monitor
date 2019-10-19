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
	waitForInput();
	sendUpdate();
	moveServo(currentGear);
}


/*************************************************************************/
/* Send the current gear number over serial communication.               */
/*************************************************************************/
void sendUpdate() {
	Serial.println(currentGear);
}



void turnOnLED() {
	digitalWrite(LED_BUILTIN, HIGH);
}

void turnOffLED() {
	digitalWrite(LED_BUILTIN, LOW);
}
