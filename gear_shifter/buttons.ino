
#include "buttons.h"

const unsigned long debounceDelay = 100;   // Milliseconds delay before detecting another push
unsigned long lastButtonTime = 0;          // Last time button was pressed or released

Button upButton;
Button downButton;


/*************************************************************************/
/* Initialize the button structures to hold state information.           */
/*************************************************************************/
void initializeButtons() {
	pinMode(UP_BUTTON_PIN, INPUT_PULLUP);
	pinMode(DOWN_BUTTON_PIN, INPUT_PULLUP);
	pinMode(ADJUST_BUTTON_PIN, INPUT_PULLUP);
	upButton.pin = UP_BUTTON_PIN;
	upButton.state = HIGH;
	downButton.pin = DOWN_BUTTON_PIN;
	downButton.state = HIGH;
}


/*************************************************************************/
/* Check if "up" button is held down.                                    */
/*************************************************************************/
boolean isUpButtonPressed() {
	return digitalRead(UP_BUTTON_PIN) == LOW;
}

/*************************************************************************/
/* Check if "down" button is held down.                                  */
/*************************************************************************/
boolean isDownButtonPressed() {
	return digitalRead(DOWN_BUTTON_PIN) == LOW;
}

/*************************************************************************/
/* Check if both buttons are held down. Used for debugging.              */
/*************************************************************************/
boolean areBothButtonsPressed() {
	return isUpButtonPressed() && isDownButtonPressed();
}

/*************************************************************************/
/* Check if adjust "button" is held down/connected. Used for debugging.  */
/*************************************************************************/
boolean isAdjustButtonPressed() {
	return digitalRead(ADJUST_BUTTON_PIN) == LOW;
}


/*************************************************************************/
/* Check button state, return what button was pressed or none.           */
/*************************************************************************/
int checkInput() {
	// Ignore button press if time since last press or release is less
	// than the debounce delay.
	long remainingTime = long(debounceDelay - (millis() - lastButtonTime));
	if (remainingTime > 0) {
		return NONE_PRESSED;
	}

	// Need to check both buttons to maintain the correct state of each
	int event = NONE_PRESSED;
	if (checkButton(upButton)) {
		event = UP_PRESSED;
	}
	if (checkButton(downButton)) {
		event = DOWN_PRESSED;
	}
	return event;
}


/*************************************************************************/
/* Return true if the button has been pressed.                           */
/*************************************************************************/
boolean checkButton(Button &button) {
	int previousState = button.state;
	int currentState = digitalRead(button.pin);

	// Check if button was pressed
	if (previousState == HIGH && currentState == LOW) {
		button.state = currentState;
		lastButtonTime = millis();
		return true;
	}
	// Detect release as well (to maintain the correct state)
	if (previousState == LOW && currentState == HIGH) {
		button.state = currentState;
		lastButtonTime = millis();
	}

	return false;
}
