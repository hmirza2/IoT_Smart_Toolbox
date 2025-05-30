import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import user_data # Imports user data form an external file

# LED Pins Setup
GREEN_LED = 16  # Access Granted LED (Green)
RED_LED = 20    # Access Denied LED (Red)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)

reader = SimpleMFRC522()

try:
    print("Please scan your card...")
    id, text = reader.read()
    uid_str = str(id)

    # RFID Security Check
    if uid_str in user_data.authorized_users:
        user_name = user_data.authorized_users[uid_str] # Access granted
        print(f"Access Granted, Hello {user_name}")
        
        # Turn on Green LED for 3 seconds
        GPIO.output(GREEN_LED, GPIO.HIGH)
        time.sleep(3)
        GPIO.output(GREEN_LED, GPIO.LOW)
        
    else:
        print("Access Denied") # Access denied
        # Turn on Red LED for 3 seconds
        GPIO.output(RED_LED, GPIO.HIGH)
        time.sleep(3)
        GPIO.output(RED_LED, GPIO.LOW)

finally:
    GPIO.cleanup()  # Ensure cleanup to reset GPIO states
