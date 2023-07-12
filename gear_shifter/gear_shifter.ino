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

	// Listen for startup message from Pi, or buttons are pressed.
	digitalWrite(LED_BUILTIN, HIGH);
	while (Serial.available() <= 0 && !(debug = areBothButtonsPressed())) {}
	if (Serial.available() >= 1) {
		char incomingByte = (char)Serial.read();
		if (incomingByte == DEBUG_MSG) {
			debug = true;
		}
	}
	if (debug) {
		delay(1000);
		if (isAdjustButtonPressed()) {
			sendMessage(DEBUG_MSG, "Adjust mode");
			adjustPositionsLoop();
		}
		else {
			sendMessage(DEBUG_MSG, "Test mode");
			testReadPositionsLoop();
		}
	}
	else {
		// Note: Servo position needs to be set *before* attaching, otherwise it
		// will move to a default position.
		currentGear = readGear();
		moveToGear(currentGear);
		initializeServo();
		sendMessage(GEAR_CHANGED_MSG, String(currentGear));
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
		}
		else {
			// Check to make sure that gear is still in position
			int oldGear = currentGear;
			currentGear = readGear();
			if (currentGear != oldGear) {
				sendMessage(ERROR_MSG, "Unexpected gear change from " + String(oldGear) + " to " + String(currentGear));
				sendMessage(GEAR_CHANGED_MSG, String(currentGear));
			}
			// TODO: Somehow detect if motor is not powered (or at least if there is no feedback signal).
			//  Perhaps analogRead a bunch of times and check if they are all zero.
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
			if (!buttonHeld) {  // Delay between first press and repeating
				delay(200);
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


/*************************************************************************/
/* Report that an error has occurred.                                    */
/*************************************************************************/
void reportError(String message) {
	sendMessage(ERROR_MSG, message);
	digitalWrite(LED_BUILTIN, HIGH);
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
/* Send a message over serial. Type is defined in header file.           */
/*************************************************************************/
void sendMessage(char type, String message) {
	if (Serial.availableForWrite() > 0) {
		Serial.print(type);
		Serial.print(message);
		Serial.print("\n");
	}
}