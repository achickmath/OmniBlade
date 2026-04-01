import serial
import time
import threading
import vgamepad as vg
from pynput import keyboard

# --- Config ---
LEFT_PORT  = "COM6"
RIGHT_PORT = "COM9"
BAUD = 115200

LEFT_DEADZONE = 5.0
LEFT_MAX = 20.0
RIGHT_DEADZONE = 10.0
RIGHT_MAX = 40.0

gamepad = vg.VX360Gamepad()

def on_press(key):
    try:
        if key == keyboard.Key.f13:
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
            gamepad.update()
            time.sleep(0.05)
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
            gamepad.update()
            print("*** START ***")
        elif key == keyboard.Key.f14:
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK)
            gamepad.update()
            time.sleep(0.05)
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK)
            gamepad.update()
            print("*** SELECT ***")
        elif key == keyboard.Key.f15:
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
            gamepad.update()
            time.sleep(0.05)
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
            gamepad.update()
        elif key == keyboard.Key.f16:
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
            gamepad.update()
            time.sleep(0.05)
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
            gamepad.update()
        elif key == keyboard.Key.f17:
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            gamepad.update()
            time.sleep(0.05)
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            gamepad.update()
        elif key == keyboard.Key.f18:
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
            gamepad.update()
            time.sleep(0.05)
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
            gamepad.update()
    except Exception as e:
        print(f"Key error: {e}")

listener = keyboard.Listener(on_press=on_press)
listener.start()

def normalize(val, deadzone, max_angle):
    if abs(val) < deadzone:
        return 0.0
    sign = 1.0 if val > 0 else -1.0
    normalized = (abs(val) - deadzone) / (max_angle - deadzone)
    return max(-1.0, min(1.0, sign * normalized))

def normalize_trigger(val, deadzone, max_angle):
    if val < deadzone:
        return 0
    normalized = (val - deadzone) / (max_angle - deadzone)
    return int(min(1.0, normalized) * 255)

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

def handle_flick_left(flick):
    if flick == "FLICK_FORWARD":
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.update()
        time.sleep(0.05)
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.update()
        print("*** A (rewind) ***")
    elif flick == "FLICK_BACK":
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
        gamepad.update()
        time.sleep(0.05)
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
        gamepad.update()
        print("*** X ***")
    elif flick == "FLICK_LEFT":
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
        gamepad.update()
        time.sleep(0.05)
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
        gamepad.update()
        print("*** Y ***")
    elif flick == "FLICK_RIGHT":
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
        gamepad.update()
        time.sleep(0.05)
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
        gamepad.update()
        print("*** B ***")

def handle_flick_right(flick):
    if flick == "FLICK_FORWARD":
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
        gamepad.update()
        time.sleep(0.05)
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
        gamepad.update()
        print("*** RB ***")
    elif flick == "FLICK_BACK":
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
        gamepad.update()
        time.sleep(0.05)
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
        gamepad.update()
        print("*** LB ***")

def left_arm_loop():
    port = serial.Serial(LEFT_PORT, BAUD, timeout=1)
    time.sleep(3)
    print("Left arm connected.")
    while True:
        if port.in_waiting > 0:
            try:
                line = port.readline().decode('utf-8').strip()
                if not line or "," not in line:
                    continue
                roll, pitch, flick = parse_line(line)
                if roll is None:
                    continue

                # Steering — left stick X only
                lx = normalize(pitch, LEFT_DEADZONE, LEFT_MAX)
                gamepad.left_joystick_float(x_value_float=lx, y_value_float=0.0)
                gamepad.update()

                if flick:
                    handle_flick_left(flick)
            except Exception as e:
                print(f"Left arm error: {e}")

def right_arm_loop():
    port = serial.Serial(RIGHT_PORT, BAUD, timeout=1)
    time.sleep(3)
    print("Right arm connected.")
    while True:
        if port.in_waiting > 0:
            try:
                line = port.readline().decode('utf-8').strip()
                if not line or "," not in line:
                    continue
                roll, pitch, flick = parse_line(line)
                if roll is None:
                    continue

                # Roll forward = throttle (RT), roll back = brake (LT)
                if roll > RIGHT_DEADZONE:
                    rt = normalize_trigger(roll, RIGHT_DEADZONE, RIGHT_MAX)
                    gamepad.right_trigger(value=rt)
                    gamepad.left_trigger(value=0)
                elif roll < -RIGHT_DEADZONE:
                    lt = normalize_trigger(-roll, RIGHT_DEADZONE, RIGHT_MAX)
                    gamepad.left_trigger(value=lt)
                    gamepad.right_trigger(value=0)
                else:
                    gamepad.right_trigger(value=0)
                    gamepad.left_trigger(value=0)
                gamepad.update()

                if flick:
                    handle_flick_right(flick)
            except Exception as e:
                print(f"Right arm error: {e}")

t1 = threading.Thread(target=left_arm_loop, daemon=True)
t2 = threading.Thread(target=right_arm_loop, daemon=True)
t1.start()
t2.start()

print("OmniBlade Forza running. Ctrl+C to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped.")