
const unsigned long lastDebounceTime = 0;  // Last time a button was pushed (input went LOW)
const unsigned long debounceDelay = 100;   // Milliseconds delay before detecting another push

int previousUpButtonState = HIGH;
int previousDownButtonState = HIGH;


/*************************************************************************/
/* Continuously check button state, waiting for a press.                 */
/* Return +1 if up button is pressed, -1 if down button.                 */
/*************************************************************************/
int waitForInput() {
	while(true) {
		if (checkUpButton()) {
			return 1;
		}
		else if (checkDownButton()) {
			return -1;
		}
		// NOTE: Delay is just a busy loop, so we might as well read the input
		// continuously without delay. But then we'd have to de-bounce it.
		delay(100);
	}
}

/*************************************************************************/
/* Return true if the button has been pressed.                           */
/*************************************************************************/
boolean checkButton(const int pin, int &previousState) {
	int currentState = digitalRead(pin);

	// Check if button was pressed
	if (previousState == HIGH && currentState == LOW) {
		previousState = currentState;
		return true;
	}
	// Detect release as well (to maintain the correct state)
	if (previousState == LOW && currentState == HIGH) {
		previousState = currentState;
	}

	return false;
}

boolean checkUpButton() {
	return checkButton(UP_BUTTON_PIN, previousUpButtonState);
}

boolean checkDownButton() {
	return checkButton(DOWN_BUTTON_PIN, previousDownButtonState);
}