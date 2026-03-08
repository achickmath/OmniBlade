#include <Arduino.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <BluetoothSerial.h>

BluetoothSerial SerialBT;
Adafruit_MPU6050 mpu;

float roll = 0, pitch = 0;
unsigned long lastTime = 0;
const float ALPHA = 0.96;

float roll_offset = 0, pitch_offset = 0;
bool calibrated = false;
int cal_count = 0;
float cal_roll_sum = 0, cal_pitch_sum = 0;
const int CAL_SAMPLES = 150;

const float FLICK_THRESHOLD = 600.0;
const unsigned long FLICK_COOLDOWN = 250;
unsigned long last_flick_time = 0;

String detectFlick(float gx, float gy) {
  unsigned long now = millis();
  if (now - last_flick_time < FLICK_COOLDOWN) return "";

  if (gy > FLICK_THRESHOLD)  { last_flick_time = now; return "FLICK_FORWARD"; }
  if (gy < -FLICK_THRESHOLD) { last_flick_time = now; return "FLICK_BACK"; }
  if (gx > FLICK_THRESHOLD)  { last_flick_time = now; return "FLICK_RIGHT"; }
  if (gx < -FLICK_THRESHOLD) { last_flick_time = now; return "FLICK_LEFT"; }

  return "";
}

void setup() {
  Serial.begin(115200);
  SerialBT.begin("OmniController");
  Wire.begin(21, 22);
  delay(1000);

  if (!mpu.begin()) {
    Serial.println("MPU6050 not found!");
    while (1) delay(10);
  }

  mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
  mpu.setGyroRange(MPU6050_RANGE_2000_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  lastTime = millis();
  Serial.println("READY - Hold neutral position for calibration...");
}

void loop() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  unsigned long now = millis();
  float dt = (now - lastTime) / 1000.0;
  lastTime = now;

  float accelRoll  = atan2(a.acceleration.y, a.acceleration.z) * 180.0 / PI;
  float accelPitch = atan2(-a.acceleration.x, sqrt(a.acceleration.y * a.acceleration.y + a.acceleration.z * a.acceleration.z)) * 180.0 / PI;

  float gyroRollRate  = g.gyro.x * 180.0 / PI;
  float gyroPitchRate = g.gyro.y * 180.0 / PI;

  roll  = ALPHA * (roll  + gyroRollRate  * dt) + (1 - ALPHA) * accelRoll;
  pitch = ALPHA * (pitch + gyroPitchRate * dt) + (1 - ALPHA) * accelPitch;

  if (!calibrated) {
    cal_roll_sum  += roll;
    cal_pitch_sum += pitch;
    cal_count++;

    if (cal_count >= CAL_SAMPLES) {
      roll_offset  = cal_roll_sum  / CAL_SAMPLES;
      pitch_offset = cal_pitch_sum / CAL_SAMPLES;
      calibrated = true;
      Serial.println("Calibration done.");
      SerialBT.println("Calibration done.");
    }
    return;
  }

  float cal_roll  = roll  - roll_offset;
  float cal_pitch = pitch - pitch_offset;

  float gx_deg = g.gyro.x * 180.0 / PI;
  float gy_deg = g.gyro.y * 180.0 / PI;
  float gz_deg = g.gyro.z * 180.0 / PI;

  String flick = detectFlick(gx_deg, gy_deg);

  String data = String(a.acceleration.x, 3) + "," +
                String(a.acceleration.y, 3) + "," +
                String(a.acceleration.z, 3) + "," +
                String(gx_deg, 3) + "," +
                String(gy_deg, 3) + "," +
                String(gz_deg, 3) + "," +
                String(cal_roll, 3) + "," +
                String(cal_pitch, 3) + "," +
                String(0.0, 3) + "," +
                flick;

  Serial.println(data);
  SerialBT.println(data);

  delay(20);
}