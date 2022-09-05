// sin/cos draaien


#include <Wire.h>
#include <MultiStepper.h>
#include <AccelStepper.h>

const int MPU = 0x68;

AccelStepper step_y(AccelStepper::DRIVER, 5, 8); // yaw
AccelStepper step_p(AccelStepper::DRIVER, 3, 6); // pitch
AccelStepper step_r(AccelStepper::DRIVER, 4, 7); // roll

void setup() {
  for(int i = 2; i <= 8; i++)
    pinMode(i, OUTPUT);
  digitalWrite(8, LOW);
  step_y.setMaxSpeed(1000);
  step_y.setCurrentPosition(0);
  step_p.setMaxSpeed(1000);
  step_p.setCurrentPosition(0);
  step_r.setMaxSpeed(1000);
  step_r.setCurrentPosition(0);
  Serial.begin(115200); // set baudrate to 115200
  Wire.begin();
  Wire.setClock(400000);
  setup_mpu_6050();
  delay(1000);
}

void loop() {
  // put your main code here, to run repeatedly:
  step_p.moveTo(900*sin((float)millis()/1000));
  step_r.moveTo(960*cos((float)millis()/1000));
  run_steppers();
}


void setup_mpu_6050()
{
  // Activate the MPU-6050
  Wire.beginTransmission(MPU); // Start communicating with the MPU-6050
  Wire.write(0x6B);            // Send the requested starting register
  Wire.write(0x00);            // Set the requested register
  Wire.endTransmission();
  // Configure the accelerometer (+/-2g)
  Wire.beginTransmission(MPU); // Start communicating with the MPU-6050
  Wire.write(0x1C);            // Send the requested starting register
  Wire.write(0x00);            // Set the requested register
  Wire.endTransmission();
  // Configure the gyro (250 degrees per second)
  Wire.beginTransmission(MPU); // Start communicating with the MPU-6050
  Wire.write(0x1B);            // Send the requested starting register
  Wire.write(0x00);            // Set the requested register
  Wire.endTransmission();
}

void run_steppers() {
  step_y.run();
  step_p.run();
  step_r.run();
}
