#include <Arduino.h>
#include <AccelStepper.h>
#include <ctype.h>

// Chasis robot setup
#define DIR_Z 6
#define STEP_Z 3
#define DIR_X 5
#define STEP_X 2

#define X_LIMIT 9
#define Z_LIMIT 10

#define STEPPER_ENABLE 8

#define X_MAX_DEGREES 270L
#define Z_MAX_DEGREES 180L

// 1/4 microstepping
// #define X_STEPS_DEGREE (13500/180)
// #define Z_STEPS_DEGREE (13550/180)

// 1/16 microstepping
#define X_STEPS_DEGREE (54000/180)
#define Z_STEPS_DEGREE (54200/180)

// 1/32 microstepping
// #define X_STEPS_DEGREE (108000/180)
// #define Z_STEPS_DEGREE (108400/180)

long POS_X = 0;
long POS_Z = 0;
long MIN_X = 500;
long MIN_Z = 500;
long MAX_X = X_MAX_DEGREES*X_STEPS_DEGREE;
long MAX_Z = Z_MAX_DEGREES*Z_STEPS_DEGREE;

// Define some steppers and the pins the will use
AccelStepper x_stepper(AccelStepper::FULL2WIRE, DIR_X, STEP_X);
AccelStepper z_stepper(AccelStepper::FULL2WIRE, DIR_Z, STEP_Z);

void runSteppers() {
  x_stepper.run();
  z_stepper.run();
}

void finishMovement() {
  digitalWrite(STEPPER_ENABLE, LOW);
  while(x_stepper.distanceToGo() != 0 || z_stepper.distanceToGo() != 0) {
    runSteppers();
  }
}

bool isValidAngle(char array[]) {
  int dotCount = 0;

  for(int i = 0; i < sizeof(array); i++) {
    if(isDigit(array[i])) continue;
    if(array[i] == '.' && dotCount++ < 1) continue;
    return false;
  }

  return true;
}

void autoHome() {
  x_stepper.setMaxSpeed(10000.0);
  x_stepper.setAcceleration(5000.0);
  x_stepper.setPinsInverted(true, false, false);

  z_stepper.setMaxSpeed(10000.0);
  z_stepper.setAcceleration(5000.0);

  x_stepper.setSpeed(-10000);
  while(!digitalRead(X_LIMIT)) {
    x_stepper.runSpeed();
  }
  x_stepper.stop();
  x_stepper.setCurrentPosition(0);

  z_stepper.setSpeed(-10000);
  while(!digitalRead(Z_LIMIT)) {
    z_stepper.runSpeed();
  }
  z_stepper.stop();
  z_stepper.setCurrentPosition(0);

  x_stepper.setMaxSpeed(1500.0);
  x_stepper.setAcceleration(5000.0);
  x_stepper.moveTo(MIN_X);
  POS_X = MIN_X;

  z_stepper.setMaxSpeed(1500.0);
  z_stepper.setAcceleration(5000.0);
  z_stepper.moveTo(MIN_Z);
  POS_Z = MIN_Z;

  finishMovement();
}


void setup() {
  Serial.begin(115200);

  pinMode(DIR_X, OUTPUT);
  pinMode(DIR_Z, OUTPUT);
  pinMode(STEP_X, OUTPUT);
  pinMode(STEP_Z, OUTPUT);

  pinMode(STEPPER_ENABLE, OUTPUT);

  pinMode(X_LIMIT, INPUT_PULLUP);
  pinMode(Z_LIMIT, INPUT_PULLUP);

  autoHome();

  Serial.println("setup_done");
}

void loop()
{
  while(Serial.available() > 0) {
    // Since this loop can take quite long to ensure stability and smoothness in the video
    // the steppers should check to run the steppers as often as possible. This is repeated
    // throughout this loop.
    runSteppers();

    String input = Serial.readStringUntil('\n');

    runSteppers();

    if(sizeof(input) < 1) return;
    if(input.indexOf(';') == -1) return;

    String x_string = input.substring(0, input.indexOf(';'));
    String z_string = input.substring(input.indexOf(';') + 1, input.indexOf('\n'));

    runSteppers();

    char x_array[x_string.length()+1];
    char z_array[z_string.length()+1];

    x_string.toCharArray(x_array, x_string.length()+1);
    z_string.toCharArray(z_array, z_string.length()+1);

    runSteppers();

    // Check if the values are valid floats
    if(!(isValidAngle(x_array) && isValidAngle(z_array))) {
      return;
    }

    runSteppers();

    // Convert both char arrays to floats to be used in calculations.
    double x_angle = atof(x_array);
    double z_angle = atof(z_array);

    runSteppers();

    long NEW_POS_X = x_angle * X_STEPS_DEGREE;
    long NEW_POS_Z = z_angle * Z_STEPS_DEGREE;

    // Make sure minimum values are not exceeded.
    if(NEW_POS_X < MIN_X) NEW_POS_X = MIN_X;
    if(NEW_POS_Z < MIN_Z) NEW_POS_Z = MIN_Z;

    runSteppers();

    long SPEED_X = abs(NEW_POS_X - x_stepper.currentPosition());
    long SPEED_Z = abs(NEW_POS_Z - z_stepper.currentPosition());

    x_stepper.setMaxSpeed(SPEED_X);
    z_stepper.setMaxSpeed(SPEED_Z);

    // Make the desired location five times as far so the camera keeps moving in case of a lost packet.
    POS_X = NEW_POS_X; //+ (2*(NEW_POS_X - x_stepper.currentPosition()));
    POS_Z = NEW_POS_Z; //+ (2*(NEW_POS_Z - z_stepper.currentPosition()));

    // Make sure maximum degrees are not exceeded.
    if(POS_X > MAX_X) POS_X = MAX_X;
    if(POS_Z > MAX_Z) POS_Z = MAX_Z;

    x_stepper.moveTo(POS_X);
    z_stepper.moveTo(POS_Z);
    digitalWrite(STEPPER_ENABLE, LOW);
  }

  // This function should run at least once in the interval of steps to ensure stability.
  runSteppers();

  if(x_stepper.distanceToGo() == 0 && z_stepper.distanceToGo() == 0) {
    digitalWrite(STEPPER_ENABLE, HIGH);
  }
  
  if(digitalRead(X_LIMIT)) {
    Serial.println("X_LIMIT SWITCH HIT!");

    x_stepper.stop();
    x_stepper.setCurrentPosition(0);

    x_stepper.moveTo(MIN_X);
    POS_X = MIN_X;

    finishMovement();
  }

  if(digitalRead(Z_LIMIT)) {
    Serial.println("Z_LIMIT SWITCH HIT!");

    z_stepper.stop();
    z_stepper.setCurrentPosition(0);

    z_stepper.moveTo(MIN_Z);
    POS_Z = MIN_Z;

    Serial.println(z_stepper.distanceToGo());

    finishMovement();
  }
}

