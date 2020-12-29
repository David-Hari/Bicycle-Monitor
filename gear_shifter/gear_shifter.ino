#include <Servo.h>
#include "gear_shifter.h"


int currentGear = 0;
boolean debug = false;


// TODO:
//  Stop servo from jumping all over the place when power is cut.

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
		Serial.println("Entering gear shifter debug mode");
		delay(5000);
		Serial.println("Gear shifter debug mode");
		currentGear = 1;
		moveServo(0);
	}
	else {
		currentGear = changeGear(readGear());
	}
	initializeServo();
}

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
/* The system has entered an error state.                                */
/* Perform any necessary shut-down, then loop indefinitely.              */
/* Blink the LED and periodically send the error message over serial.    */
/*************************************************************************/
void error(String message) {
	unsigned int state = HIGH;
	unsigned int count = 0;
	stopServo();
	while (true) {
		if (count % 4 == 0) {
			sendError(message);
		}
		digitalWrite(LED_BUILTIN, state);
		state = !state;
		count++;
		delay(400);
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
