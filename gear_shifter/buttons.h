
#ifndef BUTTONS_H
#define BUTTONS_H


/* Digital pins */
const int UP_BUTTON_PIN = 2;
const int DOWN_BUTTON_PIN = 3;

/* Events */
const int NONE_PRESSED = 0;
const int UP_PRESSED = 1;
const int DOWN_PRESSED = 2;


struct Button {
	int pin;
	int state;
};


void initializeButtons();
boolean areBothButtonsDown();
int waitForInput();


#endif   // BUTTONS_H