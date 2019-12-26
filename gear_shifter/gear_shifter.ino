#include <Servo.h>
#include "gear_shifter.h"


int currentGear = 0;
boolean debug = false;


/*************************************************************************/
/* The setup function runs once when you press reset or power the board. */
/*************************************************************************/
void setup() {
	pinMode(LED_BUILTIN, OUTPUT);
	initializeButtons();
	Serial.begin(9600);
	delay(3000);
	debug = areBothButtonsDown();
	// Note: Servo position needs to be set *before* attaching, otherwise it
	// will move to a default position.
	if (debug) {
		currentGear = 1;
		moveServo(0);
	}
	else {
		currentGear = changeGear(readGear());
		if (currentGear == -1) {
			gearPositionError();
		}
	}
	initializeServo();
}

// TODO:
//  Stop servo from jumping all over the place when power is cut.

/*************************************************************************/
/* The main loop runs continuously.                                      */
/*************************************************************************/
void loop() {
	int change = waitForInput();
	currentGear += change;   // + is up, - is down
	if (currentGear > MAX_GEARS) {
		currentGear = MAX_GEARS;
	}
	else if (currentGear < 1) {
		currentGear = 1;
	}
	currentGear = changeGear(currentGear);
	if (currentGear == E_NO_POSITION) {
		gearPositionError();
	}
	sendGearChanged(currentGear);
}

/*************************************************************************/
/* Send the given gear number over serial.                               */
/*************************************************************************/
void sendGearChanged(int gear) {
	if (Serial.availableForWrite() > 0) {
		Serial.print("G");
		Serial.print(gear);
		Serial.print("\n");
	}
}

/*************************************************************************/
/* Send an error message over serial.                                    */
/*************************************************************************/
void sendError(String message) {
	if (Serial.availableForWrite() > 0) {
		Serial.print("E");
		Serial.print(message);
		Serial.print("\n");
	}
}

/*************************************************************************/
/* Blink the LED to indicate an error.                                   */
/*************************************************************************/
void error() {
	unsigned int state = HIGH;
	while (true) {
		digitalWrite(LED_BUILTIN, state);
		state = !state;
		delay(400);
	}
}

/*************************************************************************/
/* Indicate that there is an error with the gear position.               */
/*************************************************************************/
void gearPositionError() {
	stopServo();
	sendError("Gear not in correct position");
	if (!debug) {
		error();
	}
}