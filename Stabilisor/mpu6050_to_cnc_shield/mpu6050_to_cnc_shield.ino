 // sin/cos draaien


#include <Wire.h>
#include <MultiStepper.h>
#include <AccelStepper.h>

long yaw_pos;
long pitch_pos;

float ratio = 0.8f; // 0.01 -> really fast   0.99 -> really slow
int num_readings = 50; // amount of reading the accelerometer makes
float oldPitch = 0; 
float oldRoll = 0;
float x_angle = 0;
float z_angle = 0;
float threshold = 1.3f; //threshold you can change via user interface

typedef struct YawPitchRoll_t {
  float yaw;
  float pitch;
  float roll;
} YawPitchRoll_s;

typedef struct Acc_t {
  int32_t x;
  int32_t y;
  int32_t z;
} Acc_s;

const int MPU = 0x68;
const int yaw_limit_sw = 9; // arduino pin 9, CNC shield X-/X+
const int pitch_limit_sw = 10; // arduino pin 10, CNC shield Y-/Y+
const int roll_limit_sw = 11; // arduino pin 11, CNC shield Z-/Z+
const int microstepping_multiplier = 8; // e.g. 1/16th microstepping -> set to 16
const float yaw_offset = -45.0f, pitch_offset = 2.4f, roll_offset = 0.0f; // degree

AccelStepper step_y(AccelStepper::DRIVER, 2, 5); // yaw
AccelStepper step_p(AccelStepper::DRIVER, 3, 6); // pitch
AccelStepper step_r(AccelStepper::DRIVER, 4, 7); // roll

void setup() {
  Serial.begin(115200); // set baudrate to 115200
  Serial.setTimeout(1);
  
  for(int i = 2; i <= 8; i++) // set driver step/dir pins and drive enable pin to output
    pinMode(i, OUTPUT);
  digitalWrite(8, LOW); // drive enabled, active at low level
  pinMode(yaw_limit_sw, INPUT_PULLUP);
  pinMode(pitch_limit_sw, INPUT_PULLUP);
  pinMode(roll_limit_sw, INPUT_PULLUP);

  //Initialisation of Steppemotors 17HS4023
  step_y.setMaxSpeed(2000);
  step_y.setAcceleration(1000);
  step_y.setPinsInverted(true, false,false);
  step_y.setCurrentPosition(0);
  
  step_p.setMaxSpeed(9000);
  step_p.setAcceleration(9000);
  step_p.setPinsInverted(true, false, false); // direction inverted, step normal, enable normal
  step_p.setCurrentPosition(0);
  
  step_r.setMaxSpeed(3000);
  step_r.setAcceleration(1500);
  step_r.setPinsInverted(true, false, false); // direction inverted, step normal, enable normal
  step_r.setCurrentPosition(0);
  //step_p.setMinPulseWidth(20);

  Wire.begin();
  Wire.setClock(400000);
  setup_mpu_6050();
  autohome();
}

void autohome() {

  step_y.enableOutputs();
  
  /*step_y.setSpeed(150);// * microstepping_multiplier); Old code used for calibration for yaw
  while(digitalRead(yaw_limit_sw) == HIGH) {
    step_y.runSpeed();
  }

  step_y.setCurrentPosition(500);// * microstepping_multiplier);
  step_y.moveTo(0);
  while(step_p.run()) {
    // block while moving
  }*/
  
  step_p.enableOutputs(); // Calibrate pitch
  step_p.setSpeed(-200 * microstepping_multiplier);
  while(digitalRead(pitch_limit_sw) == HIGH) {
    step_p.runSpeed();
  }
  step_p.setCurrentPosition(-125 * microstepping_multiplier);
  step_p.moveTo(0); 
  while(step_p.run()) {
    // block while moving
  }

  step_r.enableOutputs(); // Calibrate roll
  step_r.setSpeed(70 * microstepping_multiplier);
  while(digitalRead(roll_limit_sw) == HIGH) {
    step_r.runSpeed();
  }
  step_r.setCurrentPosition(90 * microstepping_multiplier); //285
  step_r.moveTo(0);
  while(step_r.run()) {
    // block while moving
  }
}

void loop() {
  while(Serial.available() > 0) {
    // Since this loop can take quite long to ensure stability and smoothness in the video
    // the steppers should check to run the steppers as often as possible. This is repeated
    // throughout this loop.
    run_steppers();

    String input = Serial.readStringUntil('\n');

    run_steppers();

   // Serial.println("recieved: " + input);

    // Slice received string into x,z,threshold
    String x_string = input.substring(0, input.indexOf(':'));
    String z_string = input.substring(input.indexOf(':')+1, input.indexOf(';'));  //input.indexOf('\n')
    String user_input = input.substring(input.indexOf(';')+1, input.indexOf('\n'));
//  step_p.moveTo(900*sin((float)millis()/1000));
//  step_r.moveTo(960*cos((float)millis()/1000));
    run_steppers();

    if(user_input == "n"){
        // do nothing      
      } else {
        //ratio = user_input.toInt();
        threshold = user_input.toFloat(); //threshold
      }

    //Serial.println("X: " + x_string);//sometime returns 1
    //Serial.println("Z: " + z_string);
     
    char x_array[x_string.length()+1];
    char z_array[z_string.length()+1];

    run_steppers();

    x_string.toCharArray(x_array, x_string.length()+1);
    z_string.toCharArray(z_array, z_string.length()+1);

    run_steppers();

    // Constrains for the received angles so they can only make real turns
    if(atof(x_array) <= 359){
        x_angle = atof(x_array);
      }
    if(atof(z_array) <= 45){
        z_angle = atof(z_array);
      }

    Serial.print("X: ");
    Serial.println(x_angle);
    Serial.print("Z: ");
    Serial.println(z_angle);
    
    run_steppers();

    // Calculate angle to steps for the motor
    yaw_pos = ((x_angle*8)/1.8)*5.049891;// 180 = 4000 | 180 = 4,000 15 *0.72 44-45*4= 176|180
    //yaw_pos = ((-x_angle*8)/0.36);
    pitch_pos = ((-z_angle*8)/1.8) * 10;// * microstepping_multiplier; 38 tandwielen

    run_steppers();
  }                               

  //read accelerometer
  static Acc_s acc = read_mpu_6050_data();
  Acc_s tmp_acc = {.x = 0, .y = 0, .z = 0};
  for(int i = 0; i < num_readings; i++) {
    Acc_s reading = read_mpu_6050_data();
    tmp_acc.x += reading.x;
    tmp_acc.y += reading.y;
    tmp_acc.z += reading.z;
    //delay(1);
    delayMicroseconds(150); //changing this value changes the speed of stabilisation (lower = faster but less accurate)
    run_steppers();
  }
  //float ratio = 0.8f; // 0.01 -> really fast   0.99 -> really slow
  acc.x *= ratio;
  acc.y *= ratio;
  acc.z *= ratio;
  acc.x += (1.0f - ratio) * (tmp_acc.x/num_readings);
  acc.y += (1.0f - ratio) * (tmp_acc.y/num_readings);
  acc.z += (1.0f - ratio) * (tmp_acc.z/num_readings); 

  acc.x += (tmp_acc.x/num_readings);
  acc.y += (tmp_acc.y/num_readings);
  acc.z += (tmp_acc.z/num_readings); 

  run_steppers();
  
  YawPitchRoll_s ypr = calculate_pitch_roll_from_acc(acc);

  run_steppers();

  ypr.yaw += yaw_offset;
  ypr.pitch += pitch_offset;
  ypr.roll += roll_offset;
  ypr.yaw = constrain(ypr.yaw, -15.0f, 15.0f);
  ypr.pitch = constrain(ypr.pitch, -20.0f, 20.0f);
  ypr.roll = constrain(ypr.roll, -15.0f, 15.0f);
 /* Serial.print("yaw:");
  Serial.print(yaw_pos);
  Serial.print("\tpitch:");
  Serial.print(ypr.pitch);
  Serial.print("\troll:");
  Serial.print(ypr.roll);
  Serial.println();*/
  run_steppers();

  //Move motors to calulated positions
  //int step_y_setpoint = ypr.yaw * (160.0f/15.0f * 200 * microstepping_multiplier / 360);
  step_y.moveTo(yaw_pos);

  if(ypr.pitch - oldPitch <= threshold && ypr.pitch - oldPitch >= -threshold) { ypr.pitch = oldPitch;}  //use threshold
  int step_p_setpoint = ypr.pitch * (160.0f/15.0f * 200 * microstepping_multiplier / 360); // <gear ratio> * <steps per stepper revolution> * microstepping / 360 = steps per degree
  int calcPitch = pitch_pos - step_p_setpoint;
  calcPitch = constrain(calcPitch, -1000, 1050);
  step_p.moveTo(calcPitch);
  
  if(ypr.roll - oldRoll <= threshold && ypr.roll - oldRoll >= -threshold) { ypr.roll = oldRoll;}  //use threshold
  int step_r_setpoint = ypr.roll * (160.0f/15.0f * 60 * microstepping_multiplier / 360); //80
  step_r.moveTo(-step_r_setpoint);
  
  run_steppers();
  int delay_in_ms = 25;
  static unsigned long timestamp = millis();
  while(timestamp + delay_in_ms > millis()) {
    run_steppers();
  }
  timestamp += delay_in_ms;
}

void run_steppers() {
  step_y.run();
  step_p.run();
  step_r.run();
}


// written by Gaurish Arkesteyn
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

YawPitchRoll_s calculate_pitch_roll_from_acc(Acc_s acc) {
  YawPitchRoll_s ypr;
  //fypr.yaw = calcYaw(acc.x, acc.y, acc.z);
  ypr.pitch = PitchRoll(acc.y, acc.x, acc.z);
  ypr.roll = -PitchRoll(acc.x, acc.y, acc.z);
  return ypr;
}

// written by Gaurish Arkesteyn
// function to calculate the pitch and roll: https://engineering.stackexchange.com/questions/3348/calculating-pitch-yaw-and-roll-from-mag-acc-and-gyro-data
// Formula: pitch = 180 * atan (accelerationX/sqr(accelerationY * accelerationY + accelerationZ * accelerationZ))/PI;
// Formula: roll = 180 * atan (accelerationY/sqr(accelerationX * accelerationX + accelerationZ * accelerationZ))/PI;
float PitchRoll(float A, float B, float C)
{
  float DataA, DataB, R_Value;
  DataA = A;
  DataB = sqrt((B * B) + (C * C));

  R_Value = atan2(DataA, DataB);
  R_Value = R_Value * 180 / PI;
 
  return R_Value;
}


// written by Gaurish Arkesteyn, modified by Henkjan Veldhoven
Acc_s read_mpu_6050_data()
{
  Wire.beginTransmission(MPU);             // Start communicating with the MPU-6050
  Wire.write(0x3B);                        // Send the requested starting register
  Wire.endTransmission();                  // End the transmission
  Wire.requestFrom(MPU, 6, true);         // request a total of 14 registers
  //read from the MPU6050 registers and store the data in the predefined variables
  Acc_s acc;
  acc.x = Wire.read() << 8 | Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)
  acc.y = Wire.read() << 8 | Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  acc.z = Wire.read() << 8 | Wire.read();  // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
  //  temp = Wire.read() << 8 | Wire.read();   // 0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)
  //  gyro_x = Wire.read() << 8 | Wire.read(); // 0x43 (GYRO_XOUT_H) & 0x44 (GYRO_XOUT_L)
  //  gyro_y = Wire.read() << 8 | Wire.read(); // 0x45 (GYRO_YOUT_H) & 0x46 (GYRO_YOUT_L)
  //  gyro_z = Wire.read() << 8 | Wire.read(); // 0x47 (GYRO_ZOUT_H) & 0x48 (GYRO_ZOUT_L)
  return acc;
}
