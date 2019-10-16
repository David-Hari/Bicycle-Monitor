#include <Servo.h>


const int GEAR_UP_PIN = 2;
const int GEAR_DOWN_PIN = 3;

Servo servo;
unsigned long lastDebounceTime = 0;  // Last time a button was pushed (input went LOW)
unsigned long debounceDelay = 100;   // Milliseconds delay before detecting another push
//boolean wasGearUpButtonPressed = false;   // To remember the event from an interrupt
//boolean wasGearDownButtonPressed = false; // ditto
volatile int currentGear = 0;

// The setup function runs once when you press reset or power the board
void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(GEAR_UP_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(GEAR_UP_PIN), gearUpButtonPressed, FALLING);
  //servo.attach(4);
}

void loop() {
  Serial.println(currentGear);
  delay(10);
}

void gearUpButtonPressed() {
  // NOTE: This works for button down, but button up also bounces and can generate press events
  unsigned long currentTime = millis();
  if ((currentTime - lastDebounceTime) > debounceDelay) {
    currentGear++;
    lastDebounceTime = currentTime;
  }
}

void gearDownButtonPressed() {
  currentGear--;
}
