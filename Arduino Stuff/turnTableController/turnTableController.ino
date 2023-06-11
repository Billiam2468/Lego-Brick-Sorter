// Include Arduino Steppher.h library
#include <Stepper.h>

// Define number of steps per rotation:
const int stepsPerRevolution = 2048;

// Wiring Setup:
// Pin 8 to IN1 on driver
// Pin 10 to IN2 on driver
// Pin 9 to IN3 on driver
// Pin 11 to IN4 on driver

// For some reason swapping In2 to pin 10 and IN3 to Pin 9 makes this work correctly

Stepper myStepper = Stepper(stepsPerRevolution, 8, 9, 10, 11);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  myStepper.setSpeed(15);
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println("clockwise");
  myStepper.step(stepsPerRevolution);
  myStepper.step(-stepsPerRevolution);
}
