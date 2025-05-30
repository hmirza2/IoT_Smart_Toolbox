import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import user_data # Imports user data form an external file
from hx711 import HX711

# Tool constants
TOOL_NAME = "Wrench"
WEIGHT_THRESHOLD = 141.2   # change means that the wrench was moved

def cleanAndExit():
    print("Cleaning...")
    GPIO.cleanup()
    exit(0)
    
# Setup HX711 Weight Sensor
hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
referenceUnit = -103.8573
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()  

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

        # Watch the scale for any movement
        print("Monitoring tool weight...")
        while True:
            try:
                val1 = hx.get_weight(5)
                val2 = hx.get_weight(5)
                delta = val1 + val2         # Total change in grams
                print(f"Weight Delta: {delta:.2f}g")

               # Decide if the wrench was taken or returned
               if delta < -WEIGHT_THRESHOLD:  # Tool Removed
                    print(f"{TOOL_NAME} OUT")
                    hx.reset()
                    hx.tare()
                
                elif delta > WEIGHT_THRESHOLD:  # Tool Returned
                    print(f"{TOOL_NAME} IN")
                    hx.reset()
                    hx.tare()

                hx.power_down()
                hx.power_up()
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                cleanAndExit()
                
    else:
        print("Access Denied") # Access denied
        # Turn on Red LED for 3 seconds
        GPIO.output(RED_LED, GPIO.HIGH)
        time.sleep(3)
        GPIO.output(RED_LED, GPIO.LOW)

finally:
    GPIO.cleanup()  # Ensure cleanup to reset GPIO states
