#include <Servo.h>

Servo servo;

// The setup function runs once when you press reset or power the board
void setup() {
  servo.attach(3);
}

// the loop function runs over and over again forever
void loop() {
  servo.write(0);
  delay(1000);
  servo.write(90);
  delay(1000);
  servo.write(180);
  delay(1000);
  servo.write(90);
  delay(1000);
}
