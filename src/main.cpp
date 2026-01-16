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
const int16_t HIT_THRESHOLD = 10000;
const unsigned long HIT_COOLDOWN_MS = 200;

// ---- Timing ----
const unsigned long SAMPLE_DELAY_MS = 10;     
const unsigned long LED_BLINK_MS     = 200;   

unsigned long lastHitMs   = 0;
unsigned long lastBlinkMs = 0;

#define LED_PIN 13
bool ledState = false;

static void printConnectionStatus(bool ok) {
  static bool lastOk = true; 
  if (ok != lastOk) {
    Serial.println(ok ? "MPU6050 connection OK" : "MPU6050 connection LOST");
    lastOk = ok;
  }
}

void setup() {
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
  Wire.begin();
  Wire.setClock(100000);
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

  // I did this test because of bad wiring connections.
  bool ok = accelgyro.testConnection();
  printConnectionStatus(ok);

  if (ok) {
    accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    // Simple hit detection using gyro Y-axis threshold + cooldown
    if (gy > HIT_THRESHOLD && (now - lastHitMs) > HIT_COOLDOWN_MS) {
      Serial.println("isku");
      lastHitMs = now;
    }
  }

  delay(SAMPLE_DELAY_MS);
}
