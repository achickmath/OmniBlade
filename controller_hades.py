import serial
import time
import vgamepad as vg
from pynput.keyboard import Key, Controller
from pynput.mouse import Button, Controller as MouseController

# --- Config ---
PORT = "COM11"
BAUD = 115200

# --- Thresholds ---
FORWARD_THRESHOLD  =  35.0
BACKWARD_THRESHOLD = -35.0
LEFT_THRESHOLD     = -35.0
RIGHT_THRESHOLD    =  35.0

keyboard = Controller()
mouse = MouseController()
gamepad = vg.VX360Gamepad()

keys_pressed = set()

def press(key):
    if key not in keys_pressed:
        keyboard.press(key)
        keys_pressed.add(key)

def release(key):
    if key in keys_pressed:
        keyboard.release(key)
        keys_pressed.discard(key)

def parse_line(line):
    try:
        val = line.split(",")
        if len(val) == 10:
            roll  = float(val[7])
            pitch = float(val[6])
            flick = val[9].strip()
            return roll, pitch, flick
    except:
        pass
    return None, None, None

def handle_flick(flick):
    if flick == "FLICK_RIGHT":
        # Attack - left mouse click
        mouse.press(Button.left)
        time.sleep(0.05)
        mouse.release(Button.left)
        print("*** ATTACK (LMB) ***")
    elif flick == "FLICK_LEFT":
        # Dash - spacebar
        keyboard.press(Key.space)
        time.sleep(0.05)
        keyboard.release(Key.space)
        print("*** DASH (Space) ***")
    elif flick == "FLICK_FORWARD":
        # Special - Q
        keyboard.press('q')
        time.sleep(0.05)
        keyboard.release('q')
        print("*** SPECIAL (Q) ***")
    elif flick == "FLICK_BACK":
        # Interact - E
        keyboard.press('e')
        time.sleep(0.05)
        keyboard.release('e')
        print("*** INTERACT (E) ***")

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

            roll, pitch, flick = parse_line(line)
            if roll is None:
                continue

            # --- Movement ---
            moving = False

            if roll > FORWARD_THRESHOLD:
                press('w'); release('s')
                moving = True
            elif roll < BACKWARD_THRESHOLD:
                press('s'); release('w')
                moving = True
            else:
                release('w'); release('s')

            if pitch < LEFT_THRESHOLD:
                press('a'); release('d')
                moving = True
            elif pitch > RIGHT_THRESHOLD:
                press('d'); release('a')
                moving = True
            else:
                release('a'); release('d')

            # --- Flicks ---
            if flick:
                handle_flick(flick)

            print(f"roll:{roll:+6.1f} pitch:{pitch:+6.1f} keys:{keys_pressed} {flick}")

        except Exception as e:
            print(e)