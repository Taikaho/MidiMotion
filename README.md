# MidiMotion

MidiMotion is an experimental embedded project that explores using motion sensor data to trigger MIDI events.  
The goal is to build a wrist-mounted motion controller for music production, where physical gestures (hits, swings) are translated into MIDI notes and velocities.

The project is developed as a hands-on learning platform for embedded C/C++, sensor data processing, and real-time event detection.

---

## Hardware Platform

- Microcontroller: ESP32 (DFRobot FireBeetle series)  
- Motion sensor: MPU6050 (accelerometer + gyroscope)  
- Communication: I2C (sensor), Serial (debug), planned Bluetooth (BLE MIDI)

---

## Project Overview

MidiMotion uses an MPU6050 motion sensor connected to an ESP32-based DFRobot FireBeetle microcontroller to detect motion events.  
At the current stage, the project focuses on:

- Reliable sensor communication over I2C
- Raw motion data validation on ESP32
- Simple hit detection using gyroscope thresholds
- Preparing the signal path for future MIDI event generation

---

## Current Status

- MPU6050 communication verified over I2C on ESP32
- Raw accelerometer and gyroscope data read and validated
- Simple hit detection implemented using a gyroscope threshold with cooldown (debounce)
- Serial output used for debugging and motion validation

---

## Planned Next Steps

### 1. Velocity Calculation
- Calculate hit intensity based on motion magnitude
- Map motion strength to MIDI velocity values (0–127)
- Enable expressive control instead of simple on/off triggering

### 2. MIDI Output
- Generate MIDI note events from detected hits
- Define a simple mapping between gestures and MIDI notes
- Support standard MIDI message formats

### 3. Integration with Music Software
- Define a clear interface for connecting the controller to DAWs (e.g. Ableton Live)
- Test MIDI input recognition in music production software
- Validate timing and latency characteristics

### 4. Wireless Operation (Bluetooth MIDI)
- Explore wireless communication using ESP32 Bluetooth capabilities
- Implement Bluetooth MIDI (BLE MIDI) for cable-free operation
- Evaluate latency, stability, and power consumption in wireless mode

---

## Motivation

The purpose of MidiMotion is not only to build a functional controller, but to gain deeper understanding of:

- Embedded programming in C/C++ on ESP32
- Sensor data interpretation and filtering
- Real-time constraints in interactive systems
- Hardware–software integration for creative applications

The project serves as a continuously evolving learning platform rather than a fixed end product.

---

## Credits

This project is based on the I2Cdev / MPU6050 library by Jeff Rowberg (MIT license):  
https://github.com/jrowberg/i2cdevlib

All modifications and additional logic are implemented as part of the MidiMotion project.
