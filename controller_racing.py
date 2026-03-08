import serial
import time
import vgamepad as vg

# --- Config ---
PORT = "COM11"
BAUD = 115200

# --- Thresholds ---
STEER_MAX  = 80.0
ACCEL_MAX  = 91.0
BRAKE_MAX  = 96.0
DEADZONE   = 8.0

gamepad = vg.VX360Gamepad()

def normalize(value, max_val, deadzone):
    if abs(value) < deadzone:
        return 0.0
    clamped = max(min(value, max_val), -max_val)
    return clamped / max_val

def parse_line(line):
    try:
        val = line.split(",")
        if len(val) == 10:
            roll  = float(val[7])
            pitch = float(val[6])
            return roll, pitch
    except:
        pass
    return None, None

print("Connecting...")
port = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(3)
print("Connected. Hold neutral for calibration...")

while True:
    if port.in_waiting > 0:
        try:
            line = port.readline().decode('utf-8').strip()
            if not line or "," not in line:
                print(f"[status] {line}")
                continue

            roll, pitch = parse_line(line)
            if roll is None:
                continue

            # Steer left/right — roll axis (inverted)
            steer = -normalize(roll, STEER_MAX, DEADZONE)

            # Accelerate/brake — pitch axis
            if pitch > DEADZONE:
                accel = normalize(pitch, ACCEL_MAX, DEADZONE)
                brake = 0.0
            elif pitch < -DEADZONE:
                accel = 0.0
                brake = normalize(-pitch, BRAKE_MAX, DEADZONE)
            else:
                accel = 0.0
                brake = 0.0

            gamepad.left_joystick_float(x_value_float=steer, y_value_float=0.0)
            gamepad.right_trigger_float(value_float=accel)
            gamepad.left_trigger_float(value_float=brake)
            gamepad.update()

            print(f"roll:{roll:+6.1f} pitch:{pitch:+6.1f} steer:{steer:+.2f} accel:{accel:.2f} brake:{brake:.2f}")

        except Exception as e:
            print(e)