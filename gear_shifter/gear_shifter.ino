/**
 *  Main program. Checks button state and drives servos to change gear.
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

	// Listen for startup message from Pi, or debug button is pressed.
	digitalWrite(LED_BUILTIN, HIGH);
	while (Serial.available() <= 0 && !(debug = isDebugButtonPressed())) {}
	if (Serial.available() >= 1) {
		char incomingByte = (char)Serial.read();
		if (incomingByte == DEBUG_MSG) {
			debug = true;
		}
	}
	if (debug) {
		delay(1000);
		sendMessage(DEBUG_MSG, "Debug mode. Adjust servos with up/down buttons");
		debugLoop();
	}
	else {
		currentGear = readGear();
		if (currentGear > 0) {
			// Note: Servo position needs to be set *before* attaching, otherwise it
			// will move to a default position.
			moveServo(readAngle1());
			initializeServo();
			sendMessage(GEAR_CHANGED_MSG, String(currentGear));
		}
		else {
			delay(2000);
			sendMessage(ERROR_MSG, "Entering debug mode due to invalid gear");
			delay(2000);
			debugLoop();
		}
	}
	digitalWrite(LED_BUILTIN, LOW);
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
			sendMessage(GEAR_CHANGING_MSG, String(currentGear));
			if (moveToGear(currentGear)) {
				sendMessage(GEAR_CHANGED_MSG, String(currentGear));
			}
			else {
				// Error moving to gear. Wait a bit then check what gear it is currently in.
				delay(2000);
				currentGear = readGear();
				sendMessage(GEAR_CHANGED_MSG, String(currentGear));
			}
		}
		else {
			// Check to make sure that gear is still in position.
			int oldGear = currentGear;
			int tempGear = readGear();
			if (tempGear == -1) {
				// Error will have been reported by readGear.
			}
			else if (tempGear != oldGear) {
				sendMessage(ERROR_MSG, "Unexpected gear change from " + String(oldGear) + " to " + String(tempGear));
				sendMessage(GEAR_CHANGED_MSG, String(currentGear));
				currentGear = tempGear;
			}
			// TODO: Somehow detect if motor is not powered (or at least if there is no feedback signal).
			//  Perhaps analogRead a bunch of times and check if they are all zero.
		}
	}
}


/*************************************************************************/
/* The debug loop runs continuously when in debug mode.                  */
/* Used for testing/debugging to determine positions of servo motors.    */
/* Moves the servo motors using the buttons.                             */
/*************************************************************************/
void debugLoop() {
	// Note: Servo position needs to be set *before* attaching, otherwise it
	// will move to a default position.
	int angle = readAngle1();
	moveServo(angle);
	initializeServo();
	int count = 0;
	boolean buttonHeld = false;
	while (true) {
		boolean upPressed = isUpButtonPressed();
		boolean downPressed = isDownButtonPressed();
		if (upPressed || downPressed) {
			if (upPressed) {
				angle--;
			}
			else if (downPressed) {
				angle++;
			}
			angle = clampAngle(angle);
			moveServo(angle);
			if (!buttonHeld) {
				delay(200);   // Delay between first press and repeating
			}
			buttonHeld = true;
		}
		else {
			buttonHeld = false;
		}

		if (count % 4 == 0) {  // Don't run too quickly, serial buffer might fill up
			testReadPositions();
		}
		delay(50);
		count++;
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
/* Report that an error has occurred.                                    */
/*************************************************************************/
void reportError(String message) {
	sendMessage(ERROR_MSG, message);
}


/*************************************************************************/
/* Perform any necessary shut-down, then loop indefinitely.              */
/*************************************************************************/
void shutdown() {
	stopServo();
	while (true) {}
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