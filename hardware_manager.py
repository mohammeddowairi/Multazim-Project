import serial
import time
import threading

class HardwareManager:
    def __init__(self, port='COM3', baudrate=9600):
        self.arduino = None
        try:
            # Initialize connection with a 1s timeout
            self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=1)
            # Give Arduino 2 seconds to reboot after Serial connection opens
            time.sleep(2) 
            self.last_open_time = 0
            print(f"✅ Hardware System: Connected on {port}")
        except Exception as e:
            print(f"❌ Hardware Error: {e}")

    def unlock_door(self):
        """Sends 'O' to open the solenoid via relay."""
        current_time = time.time()
        # Cooldown prevents spamming the Arduino
        if self.arduino and (current_time - self.last_open_time > 1):
            self.arduino.write(b'O')
            self.last_open_time = current_time
            print(">>> [HARDWARE] Command 'O' Sent <<<")
            
            # Start a background timer to lock after 3 seconds
            threading.Timer(3.0, self.lock_door).start()

    def lock_door(self):
        """Sends 'C' to deactivate the relay."""
        if self.arduino and self.arduino.is_open:
            self.arduino.write(b'C')
            print(">>> [HARDWARE] Command 'C' Sent (Door Locked) <<<")