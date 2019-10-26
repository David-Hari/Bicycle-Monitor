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
	initializeButtons();
	initializeServo();
	Serial.begin(9600);
	currentGear = readGear();
	sendGearChanged(currentGear);
}

/*************************************************************************/
/* The main loop runs continuously.                                      */
/*************************************************************************/
void loop() {
	int change = waitForInput();
	int previousGear = currentGear;
	currentGear += change;   // + or -, up or down
	if (currentGear > MAX_GEARS) {  // Bounds checking
		currentGear = MAX_GEARS;
	}
	else if (currentGear < 1) {
		currentGear = 1;
	}
	sendGearChanging();
	moveServo(previousGear, currentGear);
	sendGearChanged(currentGear);
}


/*************************************************************************/
/* Send an indication that the gear is currently changing.               */
/*************************************************************************/
void sendGearChanging() {
	Serial.println("#");
}

/*************************************************************************/
/* Send the given gear number over serial.                               */
/*************************************************************************/
void sendGearChanged(int gear) {
	Serial.println(gear);
}

