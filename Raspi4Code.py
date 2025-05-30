import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import user_data # Imports user data form an external file
from hx711 import HX711
import csv
from datetime import datetime
import os

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

# File locations
LOG_FILE = "/home/hxm113/smart_toolbox_web/data/log.csv"
TOOLS_CSV = "/home/hxm113/smart_toolbox_web/data/tools.csv"

# Ensure CSV files exist
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "User", "Tool"])

if not os.path.exists(TOOLS_CSV):
    with open(TOOLS_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Tool", "Status", "Last Updated"])
        writer.writerow([TOOL_NAME, "IN", ""])

# Update tool status
def update_tool_status(tool_name, status):
    rows = []
    with open(TOOLS_CSV, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Tool"] == tool_name:
                row["Status"] = status
                row["Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rows.append(row)
    with open(TOOLS_CSV, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Tool", "Status", "Last Updated"])
        writer.writeheader()Add commentMore actions
        writer.writerows(rows)

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
                    update_tool_status(TOOL_NAME, "OUT")
                    with open(LOG_FILE, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            user_name,
                            f"{TOOL_NAME} OUT"
                        ])
                    hx.reset()
                    hx.tare()
                
                elif delta > WEIGHT_THRESHOLD:  # Tool Returned
                    print(f"{TOOL_NAME} IN")
                    update_tool_status(TOOL_NAME, "IN")
                    with open(LOG_FILE, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            user_name,
                            f"{TOOL_NAME} IN"Add commentMore actions
                        ])
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
