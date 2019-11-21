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
//  Find out why gearPositionError happens sometimes when changing gears (perhaps quickly).
//  Stop servo from jumping all over the place when power is cut.
//  Make sure servo.detach cuts power to the servo (I'm not sure it does). 

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
	sendGearChanging();
	currentGear = changeGear(currentGear);
	if (currentGear == -1 && !debug) {  // Skip gear check in debug
		gearPositionError();
	}
	sendGearChanged(currentGear);
}

/*************************************************************************/
/* Send an indication that the gear is currently changing.               */
/*************************************************************************/
void sendGearChanging() {
	if (Serial.availableForWrite() > 0) {
		Serial.println("#");
	}
}

/*************************************************************************/
/* Send the given gear number over serial.                               */
/*************************************************************************/
void sendGearChanged(int gear) {
	if (Serial.availableForWrite() > 0) {
		Serial.println(gear);
	}
}

/*************************************************************************/
/* Send an error message over serial.                                    */
/*************************************************************************/
void sendError(String message) {
	if (Serial.availableForWrite() > 0) {
		Serial.println("E" + message);
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
	error();
}