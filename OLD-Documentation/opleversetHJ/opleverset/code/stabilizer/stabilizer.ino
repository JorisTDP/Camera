/* Gaurish Arkesteyn
  This code is for stabilizing a platform
*/

#include <Wire.h> //library for I2C communication
#include <PWMServo_I.h> //custom lib to invert the pulse because of how the PCB is created

// Declaring global variables:
const int MPU = 0x68; //MPU6050 I2C adress
//position at which te servo start, to hold the platform horizontal at the start
const int STARTPOS_X = 89;
const int STARTPOS_Y = 90;
//define the minimum pulse width and maximum pulse width changed it to block min- and maximum angle
const int MINPWM = 500;
const int MAXPWM = 2500;
//calculated offset
const int PITCH_OFFSET = 7;
const int ROLL_OFFSET = 10;
//variables for storing the raw data of the MPU6050
int16_t  acc_x, acc_y, acc_z;//, temp, gyro_x, gyro_y, gyro_z;
//varialbles for storing the calculated roll and pitch
//float pitch = 0.0;
//float roll = 0.0;
//variables for time management
long loop_timer;
// Instantiate the two servo's
PWMServo_I ServoPitch_X, ServoRoll_Y;

typedef struct acc_struct {
  int32_t x;
  int32_t y;
  int32_t z;
} acc_t;

typedef struct pid_params_stuct {
  float kp, ki, kd;
  float error_integral;
  float previous_error;
} pid_params_t;

void setup()
{
  Serial.begin(115200); // set baudrate to 115200
  Wire.begin();               // Start I2C as master
  Wire.setClock(400000); //set the MPU sample freq to 400kHz
  //attach the servo's to pin 3 and 4 with a minimum pulse width of 500 uS and max pulse wdith of 2500 uS
  ServoPitch_X.attach(3, MINPWM, MAXPWM);
  ServoRoll_Y.attach(4, MINPWM, MAXPWM);
  //write the start position to the servo
  ServoPitch_X.write(STARTPOS_X);
  ServoRoll_Y.write(STARTPOS_Y);
  setup_mpu_6050(); //startup the MPU6050 and configure the MPU6050
  delay(1000);//wait 1 second before starting the mainloop
}

void loop()
{
  static float pitch = 0.0f, roll = 0.0f;
  float measuredPitch, measuredRoll;
  //calculate 5000 times pitch and roll to get  better and acurate results
  acc_t xyz_acc = {.x = 0, .y = 0, .z = 0};
  static acc_t xyz_acc_avg = xyz_acc;
  const int divider = 15;
  for (int i = 0; i < divider; i++) {
    acc_t reading = read_mpu_6050_data();
    read_mpu_6050_data_old(); // read the raw gyro and accel data
    xyz_acc.x += reading.y; // x and y are switched
    xyz_acc.y += reading.x;
    xyz_acc.z += reading.z;
    measuredPitch += PitchRoll(acc_y, acc_x, acc_z); //calculate pitch angle with PitchRoll function
    measuredRoll += PitchRoll(acc_x, acc_y, acc_z); //calculate roll angle with PitchRoll function
    delay(1);
  }
  //    Serial.printf(" xyza_acc.x=%d ", xyz_acc.x);
  //  Serial.printf(" accX:%-02d accY:%-02d accZ:%-02d", acc_x, acc_y, acc_z);
  //devide the pitch and roll by 5000 to get an avarage
  measuredPitch /= divider;
  measuredRoll  /= divider;

  xyz_acc.x /= divider;
  xyz_acc.y /= divider;
  xyz_acc.z /= divider;
  const int num_readings = 10;
  static acc_t lastReadings[num_readings];
  static int lastReadings_i = 0;
  lastReadings[lastReadings_i++] = xyz_acc;
  if (lastReadings_i >= num_readings)
    lastReadings_i = 0;
  xyz_acc_avg.x = 0;
  xyz_acc_avg.y = 0;
  xyz_acc_avg.z = 0;
  for (int i = 0; i < num_readings; i++) {
    xyz_acc_avg.x += lastReadings[i].x;
    xyz_acc_avg.y += lastReadings[i].y;
    xyz_acc_avg.z += lastReadings[i].z;
  }

  xyz_acc_avg.x /= num_readings;
  xyz_acc_avg.y /= num_readings;
  xyz_acc_avg.z /= num_readings;
  //  const float factor = 0.9; // low = fast; high = slow
  //  xyz_acc_avg.x = factor * xyz_acc_avg.x + (1.0 - factor) * xyz_acc.x;
  //  xyz_acc_avg.y = factor * xyz_acc_avg.y + (1.0 - factor) * xyz_acc.y;
  //  xyz_acc_avg.z = factor * xyz_acc_avg.z + (1.0 - factor) * xyz_acc.z;

  pitch = pitch * 0.5 + measuredPitch * 0.5;
  roll = roll * 0.5 + measuredRoll * 0.5;
  //  Serial.printf(" accX:%-02d accY:%-02d accZ:%-02d", xyz_acc_avg.x, xyz_acc_avg.y, xyz_acc_avg.z);
  Serial.printf(" accX:%-02d accY:%-02d", xyz_acc_avg.x, xyz_acc_avg.y);
  //  Serial.printf(" Pitch:%.2f Roll:%.2f", pitch, roll);

  if (0) { // set platform manually. Comment other ```controlServo(pitch,roll)''' functions
    static float manual_pitch = 90.0f, manual_roll = 90.0f;
    while (Serial.available()) {
      char in = Serial.read();
      switch (in) {
        case 'u': manual_pitch += 1.0f; break;
        case 'd': manual_pitch -= 1.0f; break;
        case 'l': manual_roll += 1.0f; break;
        case 'r': manual_roll -= 1.0f; break;
        default: return;
      }
      controlServo(manual_pitch, manual_roll);
    }
    Serial.printf(" ManualPitch:%.2f; ManualRoll:%.2f...", manual_pitch, manual_roll);
  }

  if (1) { // auto mode
    static float auto_pitch = 90.0f, auto_roll = 90.0f;
    const int setpointX = -1000, // left: increase; right: decrease
              setpointY = 2500; // point camera at 0deg up: increase; point camera at 0deg down: decrease

    static pid_params_t roll_servo = { // X
      .kp = -0.0015f, .ki = 0.000, .kd = -0.00008,
      .error_integral = 0,
      .previous_error = 0
    };
    auto_roll = auto_roll - pid(&roll_servo, setpointX - xyz_acc_avg.x, 0.05);

    static pid_params_t pitch_servo = { // Y
      .kp = 0.0015f, .ki = 0.0, .kd = 0.00008,
      .error_integral = 0,//(xyz_acc_avg.y/0.1),
      .previous_error = 0
    };
    auto_pitch = auto_pitch - pid(&pitch_servo, setpointY - xyz_acc_avg.y, 0.05);

    static bool control = true;
    float factor = 0.7;
    static float avg_pitch = auto_pitch;
    avg_pitch = factor * avg_pitch + (1.0f - factor) * auto_pitch;
    static float avg_roll = auto_roll;
    avg_roll = factor * avg_roll + (1.0f - factor) * auto_roll;
    Serial.printf(" 50*auto_pitch:%.2f 50*auto_roll:%.2f", auto_pitch * 50, auto_roll * 50);
    if (control)
      controlServo(avg_pitch, avg_roll);


    while (Serial.available()) {
      char in = Serial.read();
      switch (in) {
        // reset
        case 'r': auto_pitch = 90; auto_roll = 90; controlServo(auto_pitch, auto_roll); delay(500);
          roll_servo.error_integral = 0;
          roll_servo.previous_error = 0;
          pitch_servo.error_integral = 0;
          pitch_servo.previous_error = 0;
          break;
        // stop
        case 's':
          control = false;
          break;
        // continue
        case 'c':
          control = true;
          break;
      }
    }
  }

  Serial.println();
  while (millis() - loop_timer < 50);                                //Wait until the loop_timer reaches 75 milliseconds to slow down each loop
  loop_timer += 50;//Reset the loop timer
}

float pid(pid_params_t *params, float current_error, float dt) {
  // calculate integral part
  params->error_integral += current_error * dt;

  // calculate output
  float control_output;
  // proportional
  control_output = params->kp * current_error;
  // integral
  control_output += params->ki * params->error_integral;
  // derivative
  control_output += params->kd * (current_error - params->previous_error) / dt;

  // copy error to previous_error
  params->previous_error = current_error;
  return control_output;
}

//function to setup the MPU6050 and configure the range by writing a certain HEX value to the right register
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

// Subroutine for reading and storing the raw gyro and accel data
void read_mpu_6050_data_old()
{
  Wire.beginTransmission(MPU);             // Start communicating with the MPU-6050
  Wire.write(0x3B);                        // Send the requested starting register
  Wire.endTransmission();                  // End the transmission
  Wire.requestFrom(MPU, 6, true);         // request a total of 14 registers
  acc_x = Wire.read() << 8 | Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)
  acc_y = Wire.read() << 8 | Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  acc_z = Wire.read() << 8 | Wire.read();  // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
  //  temp = Wire.read() << 8 | Wire.read();   // 0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)
  //  gyro_x = Wire.read() << 8 | Wire.read(); // 0x43 (GYRO_XOUT_H) & 0x44 (GYRO_XOUT_L)
  //  gyro_y = Wire.read() << 8 | Wire.read(); // 0x45 (GYRO_YOUT_H) & 0x46 (GYRO_YOUT_L)
  //  gyro_z = Wire.read() << 8 | Wire.read(); // 0x47 (GYRO_ZOUT_H) & 0x48 (GYRO_ZOUT_L)
}

// Subroutine for reading and storing the raw gyro and accel data
acc_t read_mpu_6050_data()
{
  acc_t acc;
  Wire.beginTransmission(MPU);             // Start communicating with the MPU-6050
  Wire.write(0x3B);                        // Send the requested starting register
  Wire.endTransmission();                  // End the transmission
  Wire.requestFrom(MPU, 6, true);         // request a total of 14 registers
  acc.x = (int16_t)(Wire.read() << 8 | Wire.read());  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)
  acc.y = (int16_t)(Wire.read() << 8 | Wire.read());  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  acc.z = (int16_t)(Wire.read() << 8 | Wire.read());  // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
  //  temp = Wire.read() << 8 | Wire.read();   // 0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)
  //  gyro_x = Wire.read() << 8 | Wire.read(); // 0x43 (GYRO_XOUT_H) & 0x44 (GYRO_XOUT_L)
  //  gyro_y = Wire.read() << 8 | Wire.read(); // 0x45 (GYRO_YOUT_H) & 0x46 (GYRO_YOUT_L)
  //  gyro_z = Wire.read() << 8 | Wire.read(); // 0x47 (GYRO_ZOUT_H) & 0x48 (GYRO_ZOUT_L)
  return acc;
}

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

void controlServo(float p, float r) {
  //  p = constrain(p, 47, 124);
  //  r = constrain(r, 13, 135);
  ServoPitch_X.write_f(p);
  ServoRoll_Y.write_f(r);
}
