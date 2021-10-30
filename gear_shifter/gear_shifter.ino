/**
 *  Main program. Checks button state and drives servos to change gear.
 *
 * TODO:
 *  - Stop servo from jumping all over the place when power is cut.
 *
 *  - Could constantly check for errors in main loop.
 *    Change waitForInput() to checkInput(), which will return immediately with either
 *    1, -1, or 0 if time is less than debounce delay.
 *
 *  - Somehow detect if motor is not powered (or at least if there is no feedback signal).
 *    Perhaps analogRead a bunch of times and check if they are all zero.
 */


#include <Servo.h>
#include "common.h"
#include "buttons.h"
#include "servo_control.h"


int currentGear = 0;
boolean debug = false;



/*************************************************************************/
/* The setup function runs once when you press reset or power the board. */
/*************************************************************************/
void setup() {
	pinMode(LED_BUILTIN, OUTPUT);
	initializeButtons();
	Serial.begin(9600);
	
	// Listen for startup message from Pi, or buttons are pressed.
	digitalWrite(LED_BUILTIN, HIGH);
	while (Serial.available() <= 0 && !(debug = areBothButtonsDown())) {}
	if (Serial.available() >= 1) {
		char incomingByte = (char)Serial.read();
		if (incomingByte == 'D') {
			debug = true;
		}
	}
	digitalWrite(LED_BUILTIN, LOW);
	
	if (debug) {
		sendMessage("D", "Debug mode");
		delay(1000);
		testReadPositions();   // This never returns, preventing the main loop from executing
	}
	else {
		// Note: Servo position needs to be set *before* attaching, otherwise it
		// will move to a default position.
		currentGear = readGear();
		moveToGear(currentGear);
		initializeServo();
		sendGearChanged(currentGear);
	}
}


/*************************************************************************/
/* The main loop runs continuously.                                      */
/*************************************************************************/
void loop() {
	int change = waitForInput();

	currentGear += change;          // + is up, - is down
	if (currentGear > MAX_GEARS) {
		currentGear = MAX_GEARS;
	}
	else if (currentGear < 1) {
		currentGear = 1;
	}
	
	moveToGear(currentGear);
	sendGearChanged(currentGear);
}

/*************************************************************************/
/* Used for testing/debugging to determine positions of servo motors.    */
/*************************************************************************/
void testReadPositions() {
	while (true) {
		int angle1 = readAngle(FEEDBACK_PIN_1);
		int angle2 = readAngle(FEEDBACK_PIN_2);
		int gear1 = getGearAtPosition(angle1);
		int gear2 = getGearAtPosition(angle2);
		
		String message = "Angle/Gear - 1: " + String(angle1) + "°, ";
		if (gear1 == -1) {
			message = message + "none";
		}
		else {
			message = message + String(gear1);
		}
		message = message + " - 2: " + String(angle2) + "°, ";
		if (gear2 == -1) {
			message = message + "none";
		}
		else {
			message = message + String(gear2);
		}
		sendMessage("D", message);
		
		delay(200);  // Don't want to run too quickly, serial buffer might fill up
	}
}


/*************************************************************************/
/* The system has entered an error state.                                */
/* Perform any necessary shut-down, then loop indefinitely.              */
/* Blink the LED and periodically send the error message over serial.    */
/*************************************************************************/
void error(String message) {
	unsigned int count = 0;
	if (!debug) {
		stopServo();
	}
	do {
		if (count % 4 == 0) {
			sendError(message);
		}
		// 3 short on/off pulses every second
		for (int i = 0; i < 3; i++) {
			digitalWrite(LED_BUILTIN, HIGH);
			delay(100);
			digitalWrite(LED_BUILTIN, LOW);
			delay(100);
		}
		delay(900);
		count++;
	} while (!debug);
}


/*************************************************************************/
/* Send the given gear number over serial.                               */
/*************************************************************************/
void sendGearChanged(int gear) {
	sendMessage("G", String(gear));
}

/*************************************************************************/
/* Send an error message over serial.                                    */
/*************************************************************************/
void sendError(String message) {
	sendMessage("E", message);
}

/*************************************************************************/
/* Send a message over serial. Type should be a single character.        */
/*************************************************************************/
void sendMessage(String type, String message) {
	if (Serial.availableForWrite() > 0) {
		Serial.print(type);
		Serial.print(message);
		Serial.print("\n");
	}
}