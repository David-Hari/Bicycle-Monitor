
const unsigned long debounceDelay = 200;   // Milliseconds delay before detecting another push
unsigned long lastButtonTime = 0;          // Last time button was pressed or released

Button upButton;
Button downButton;

/*************************************************************************/
/* Initialize the button structures to hold state information.           */
/*************************************************************************/
void initializeButtons() {
	pinMode(UP_BUTTON_PIN, INPUT_PULLUP);
	pinMode(DOWN_BUTTON_PIN, INPUT_PULLUP);
	upButton.pin = UP_BUTTON_PIN;
	upButton.state = HIGH;
	downButton.pin = DOWN_BUTTON_PIN;
	downButton.state = HIGH;
}

/*************************************************************************/
/* Check if both buttons are held down. Used for debugging.              */
/*************************************************************************/
boolean areBothButtonsDown() {
	return digitalRead(UP_BUTTON_PIN) == LOW && digitalRead(DOWN_BUTTON_PIN) == LOW;
}

/*************************************************************************/
/* Continuously check button state, waiting for a press.                 */
/* Return +1 if up button is pressed, -1 if down button.                 */
/*************************************************************************/
int waitForInput() {
	lastButtonTime = millis();
	while (true) {
		if (checkButton(upButton)) {
			return 1;
		}
		else if (checkButton(downButton)) {
			return -1;
		}
		// If time since last button press or release is less than the
		// debounce delay then wait for the remainder of the time.
		long remainingTime = long(debounceDelay - (millis() - lastButtonTime));
		if (remainingTime > 0) {
			delay(remainingTime);
		}
	}
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
