# IoT_Smart_Toolbox
A Raspberry Pi‑powered smart toolbox that uses an RFID reader and a load‑cell scale to track when a tool is taken out or returned.

# System Overview
1. RFID security is implemented to track which users have taken tools out of the box, preventing loss and theft.
2. Load Cell sensors are added to drawers to monitor what is take in and out of toolbox.
3. Managers and Employees have access to a webpage showing current stock levels and who is using which tool.

# Code description
1. RFID Security: The system starts by checking scanned RFID tags against authorized IDs. If access is granted, a green LED lights up. If denied, a red LED lights up.
2. External User Database: User information is stored in a separate user_data module for better security and easier future updates or scaling.
3. Tool Detection: The HX711 module monitors tool movement by detecting changes in weight. A predefined threshold is used to determine if the tool has been taken out or returned.
4. Activity Logging: Each tool interaction (with user name, timestamp, and tool status) is logged into a CSV file. This data is later displayed on a connected web interface.
5. Library Support: The project relies on external libraries (SimpleMFRC522 for RFID, HX711 for the load cell, and a custom user_data module for access control).


