/*
 * MidiMotion - Motion sensor percussion instrument by Toni Taikina-aho (in progress)
 * 
 * 
 * Based on Jeff Rowberg's I2Cdev MPU6050 example (MIT license)
 * Original source: https://github.com/jrowberg/i2cdevlib
 *
 * Modifications:
 * - Added motion threshold detection ("hit") with cooldown (debounce)
 * - Serial output for sensor validation
 */

#include <Arduino.h>
#include "I2Cdev.h"
#include "MPU6050.h"

#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
  #include <Wire.h>
#endif

// ---- MPU6050 ----
MPU6050 accelgyro;
int16_t ax, ay, az;
int16_t gx, gy, gz;

// ---- Hit detection settings ----
const int16_t HIT_THRESHOLD = 10000;   // min gyro magnitude to start detection
const int16_t HIT_MAX       = 30000;   // gyro magnitude that maps to velocity 127 (calibrate!)
const unsigned long HIT_COOLDOWN_MS  = 200;
const unsigned long PEAK_WINDOW_MS   = 40;    // ms to search for peak after threshold crossing

// ---- Hit state machine ----
enum HitState { IDLE, PEAK_DETECT };
HitState hitState       = IDLE;
unsigned long peakWindowStart = 0;
int16_t peakSample      = 0;

// ---- Timing ----
const unsigned long SAMPLE_DELAY_MS = 10;
const unsigned long LED_BLINK_MS     = 200;

unsigned long lastHitMs   = 0;
unsigned long lastBlinkMs = 0;

#define LED_PIN 13
bool ledState = false;

static void printConnectionStatus(bool ok) {
  static bool lastOk = true; // so we print only on change
  if (ok != lastOk) {
    Serial.println(ok ? "MPU6050 connection OK" : "MPU6050 connection LOST");
    lastOk = ok;
  }
}

void setup() {
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
  Wire.begin();
  Wire.setClock(100000); // slower I2C = more stable on protoboards
#elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
  Fastwire::setup(400, true);
#endif

  Serial.begin(9600);
  delay(200);

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  Serial.println("Initializing MPU6050...");
  accelgyro.initialize();

  bool ok = accelgyro.testConnection();
  Serial.println(ok ? "MPU6050 connection successful" : "MPU6050 connection failed");
}

void loop() {
  unsigned long now = millis();

  // Optional: detect if sensor disappears (e.g. bad jumper wires)
  bool ok = accelgyro.testConnection();
  printConnectionStatus(ok);

  if (ok) {
    accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    // Hit detection with peak-window velocity measurement
    int16_t gyAbs = abs(gy);

    if (hitState == IDLE) {
      if (gyAbs > HIT_THRESHOLD && (now - lastHitMs) > HIT_COOLDOWN_MS) {
        hitState        = PEAK_DETECT;
        peakWindowStart = now;
        peakSample      = gyAbs;
      }
    } else { // PEAK_DETECT
      if (gyAbs > peakSample) peakSample = gyAbs;

      if (now - peakWindowStart >= PEAK_WINDOW_MS) {
        int velocity = map(constrain(peakSample, HIT_THRESHOLD, HIT_MAX),
                           HIT_THRESHOLD, HIT_MAX, 1, 127);
        Serial.print("hit velocity=");
        Serial.println(velocity);
        lastHitMs = now;
        hitState  = IDLE;
      }
    }
  }

  delay(SAMPLE_DELAY_MS);
}