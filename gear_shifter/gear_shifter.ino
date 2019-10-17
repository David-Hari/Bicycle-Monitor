#include <Servo.h>


const int UP_BUTTON_PIN = 2;
const int DOWN_BUTTON_PIN = 3;
const int SERVO_PIN = 4;
const unsigned long lastDebounceTime = 0;  // Last time a button was pushed (input went LOW)
const unsigned long debounceDelay = 100;   // Milliseconds delay before detecting another push

int previousUpButtonState = HIGH;
int previousDownButtonState = HIGH;
int currentGear = 0;
Servo servo;

// The setup function runs once when you press reset or power the board
void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(UP_BUTTON_PIN, INPUT_PULLUP);
  //pinMode(DOWN_BUTTON_PIN, INPUT_PULLUP);
  Serial.begin(9600);
  //servo.attach(SERVO_PIN);
}

void loop() {
  if (checkUpButton()) {
    currentGear++;
    Serial.println(currentGear);
    blinkLED();
  }
  else if (checkDownButton()) {
    currentGear--;
    Serial.println(currentGear);
    blinkLED();
  }
  delay(100);
}

// Returns true if the button has been pressed
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

void blinkLED() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
}
