/**
 *  Main program. Checks button state and drives servos to change gear.
 *
 * TODO:
 *  - Could constantly check for servo alignment in main loop.
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
	digitalWrite(LED_BUILTIN, LOW);
	while (Serial.available() <= 0 && !(debug = areBothButtonsDown())) {}
	if (Serial.available() >= 1) {
		char incomingByte = (char)Serial.read();
		if (incomingByte == DEBUG_MSG) {
			debug = true;
		}
	}
	digitalWrite(LED_BUILTIN, HIGH);

	if (debug) {
		sendMessage(DEBUG_MSG, "Debug mode");
		delay(1000);
		if (isAdjustButtonDown()) {
			adjustPositionsLoop();
		}
		else {
			testReadPositionsLoop();
		}
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
	if (Serial.available() >= 1) {
		char incomingByte = (char)Serial.read();
		if (incomingByte == SHUTDOWN_MSG) {
			sendMessage(ACKNOWLEDGE_MSG, "Shutting down.");
			shutdown();
		}
	}
	else {
		int buttonPressed = checkInput();
		if (buttonPressed != NONE_PRESSED) {
			if (buttonPressed == UP_PRESSED) {
				if (currentGear < MAX_GEARS) {
					currentGear++;
				}
			}
			else if (buttonPressed == DOWN_PRESSED) {
				if (currentGear > 1) {
					currentGear--;
				}
			}
			moveToGear(currentGear);
			sendGearChanged(currentGear);
		}
	}
}

/*************************************************************************/
/* Used for testing/debugging to determine positions of servo motors.    */
/*************************************************************************/
void testReadPositionsLoop() {
	while (true) {
		testReadPositions();
		delay(200);  // Don't run too quickly, serial buffer might fill up
	}
}

void testReadPositions() {
	int angle1 = readAngle1();
	int angle2 = readAngle2();
	int gear1 = getGearAtPosition(angle1);
	int gear2 = getGearAtPosition(angle2);

	String message = "Angle/Gear   1: " + String(angle1) + "°, ";
	if (gear1 == -1) {
		message = message + "none";
	}
	else {
		message = message + String(gear1);
	}
	message = message + "   2: " + String(angle2) + "°, ";
	if (gear2 == -1) {
		message = message + "none";
	}
	else {
		message = message + String(gear2);
	}
	sendMessage(DEBUG_MSG, message);
}

/*************************************************************************/
/* Moves the servo motors using the buttons.                             */
/* Used for determining the motor angles of each gear position.          */
/*************************************************************************/
void adjustPositionsLoop() {
	// Note: Servo position needs to be set *before* attaching, otherwise it
	// will move to a default position.
	int angle = readAngle1();
	moveServo(angle);
	initializeServo();
	while (true) {
		int buttonPressed = checkInput();
		if (buttonPressed != NONE_PRESSED) {
			if (buttonPressed == UP_PRESSED) {
				angle++;
			}
			else if (buttonPressed == DOWN_PRESSED) {
				angle--;
			}
			angle = clampAngle(angle);
			moveServo(angle);
		}

		testReadPositions();
		delay(200);
	}
}


/*************************************************************************/
/* The system has entered an error state.                                */
/* Perform any necessary shut-down, then loop indefinitely.              */
/* Blink the LED and periodically send the error message over serial.    */
/*************************************************************************/
void error(String message) {
	unsigned int count = 0;
	stopServo();
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
/* Perform any necessary shut-down, then loop indefinitely.              */
/*************************************************************************/
void shutdown() {
	stopServo();
	digitalWrite(LED_BUILTIN, LOW);
	while (true) {}
}


/*************************************************************************/
/* Send the given gear number over serial.                               */
/*************************************************************************/
void sendGearChanged(int gear) {
	sendMessage(GEAR_CHANGED_MSG, String(gear));
}

/*************************************************************************/
/* Send an error message over serial.                                    */
/*************************************************************************/
void sendError(String message) {
	sendMessage(ERROR_MSG, message);
}

/*************************************************************************/
/* Send a message over serial. Type is defined in header file.           */
/*************************************************************************/
void sendMessage(char type, String message) {
	if (Serial.availableForWrite() > 0) {
		Serial.print(type);
		Serial.print(message);
		Serial.print("\n");
	}
}