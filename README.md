# OmniBlade

A motion-based adaptive game controller for players with limb differences. Strap it to your arms, tilt to move, flick to attack. No buttons. No joysticks. Just motion.

---

## The Idea

Most adaptive controllers are expensive, limited, or designed as an afterthought. OmniBlade is built from scratch around a simple idea — if someone has an arm, they can play. Two IMU sensors read the motion of each arm in real time and map it to a full Xbox controller input. Voice handles the rest.

---

## Hardware

- 2x ESP32 DEVKIT V1 (CP2102, USB-C)
- 2x MPU-6050 6-axis IMU
- 2x Half-size breadboard
- Jumper wires
- 3D printed forearm housing (3MF files in `/housing`)
- Velcro straps

## Wiring (each unit)

| MPU-6050 | ESP32 |
|---|---|
| VCC | 3.3V |
| GND | GND |
| SDA | GPIO21 |
| SCL | GPIO22 |

---

## How It Works

Each ESP32 reads accelerometer and gyroscope data from its MPU-6050 over I2C at 50Hz. A complementary filter fuses the two signals into stable roll and pitch angles. Gyroscope spikes above a threshold are classified as flick gestures. All of this streams over USB serial to a Python script that maps the data to a virtual Xbox controller using vgamepad.

Voice commands are handled separately by VoiceAttack, which sends F-key presses that the script listens for via pynput.

---

## Setup

Flash `main.cpp` to both ESP32s using PlatformIO or Arduino IDE. Then install Python dependencies:

```
pip install pyserial vgamepad pynput
```

Find your COM ports:

```
[System.IO.Ports.SerialPort]::GetPortNames()
```

Update `LEFT_PORT` and `RIGHT_PORT` in the script, then run:

```
python dual_imu.py
```

Hold both arms neutral for 3 seconds on startup for calibration.

---

## Scripts

- `dual_imu.py` — universal script, works for any game
- `dual_forza.py` — Forza specific, analog throttle and brake on right arm tilt

---

## Button Mapping

**Left arm** — tilt for left stick, flicks for X / LT / Y / LB

**Right arm** — tilt for right stick, flicks for RT / A / B / RB

**Voice** — Start, Select, D-pad, L3, R3 via VoiceAttack

Full mapping in the user guide.

---

## Known Issues

- Hold arms neutral on startup or calibration will be off
- Some power banks auto-shutoff at low current draw
- vgamepad requires the correct Python environment on Windows


