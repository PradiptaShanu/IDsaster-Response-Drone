import time
from pymavlink import mavutil

def map_to_movement(cx, cy, fx=320, fy=240, deadzone=30):
    dx = cx - fx
    dy = cy - fy

    if abs(dx) < deadzone:
        roll = 0
    else:
        roll = 0.5 if dx > 0 else -0.5

    if abs(dy) < deadzone:
        pitch = 0
    else:
        pitch = -0.5 if dy > 0 else 0.5

    return pitch, roll

def send_mavlink_command(master, pitch, roll):
    master.mav.manual_control_send(
        master.target_system,
        int(roll * 1000),
        int(pitch * 1000),
        500,  # Throttle fixed
        0,    # Yaw
        0     # Buttons
    )

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')  # Change this to your serial port if needed
master.wait_heartbeat()

print("Connected to drone")

while True:
    try:
        with open("coordinates_log.txt", "r") as file:
            lines = file.readlines()
            if lines:
                last = lines[-1].strip()
                cx, cy = map(int, last.split(","))
                pitch, roll = map_to_movement(cx, cy)
                send_mavlink_command(master, pitch, roll)
                print(f"Sent pitch={pitch}, roll={roll}")
        time.sleep(0.5)
    except KeyboardInterrupt:
        print("Stopped by user")
        break
    except:
        continue
