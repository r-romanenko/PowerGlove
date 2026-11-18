import serial
import pyautogui
import time

SERIAL_PORT = 'COM7' 
BAUD_RATE = 115200
SENSITIVITY = 50.0  # Increased so small movements translate to whole pixels

# Disable PyAutoGUI's hidden delay
pyautogui.PAUSE = 0 
pyautogui.FAILSAFE = True 

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print("Connected to Arduino! Letting IMU settle...")
    time.sleep(2) 
    ser.reset_input_buffer() 
except Exception as e:
    print(f"Error opening serial port: {e}")
    exit()

prev_yaw = None
prev_pitch = None
prev_button = 0
startup_discard = 20 # Throw away the first 20 readings



while True:
    try:
        if ser.in_waiting > 0:
            # errors='ignore' prevents weird startup bytes from silently breaking the script
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            
            parts = line.split(',')
            if len(parts) == 3:
                yaw = float(parts[0])
                pitch = float(parts[1])
                button = int(parts[2])
                
                if startup_discard > 0:
                    startup_discard -= 1
                    prev_yaw = yaw
                    prev_pitch = pitch
                    continue 
                
                if prev_yaw is not None and prev_pitch is not None:
                    # Calculate movement
                    dx = (yaw - prev_yaw) * SENSITIVITY
                    dy = (pitch - prev_pitch) * SENSITIVITY
                    
                    move_x = int(dx)
                    move_y = int(-dy) # Inverted so tilting down moves cursor down
                    
                    print(f"IMU: {yaw:.2f}, {pitch:.2f} | Moving Mouse: X={move_x}, Y={move_y}")
                    
                    # Only send command if movement is at least 1 pixel
                    if move_x != 0 or move_y != 0:
                        pyautogui.move(-move_x, -move_y) 

                if button == 0 and prev_button == 1:
                    pyautogui.mouseDown()
                    print("Left Click DOWN")
                elif button == 1 and prev_button == 0:
                    pyautogui.mouseUp()
                    print("Left Click UP")

                prev_yaw = yaw
                prev_pitch = pitch
                prev_button = button

                


                
    except ValueError:
        pass # Silently ignore non-number text like "BNO08x Found!"
    except KeyboardInterrupt:
        print("\nExiting...")
        break