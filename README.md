WASPP Handbook (WIP): https://docs.google.com/document/d/1IceIdq9c53aDnLVoJMZE6vS1mh8t16MDo0X86kv3OAQ/edit?usp=sharing

WASPP Wireless Codebase
=======================

This repository contains an early-stage wireless communication integration for the WASPP
system. It connects three pieces:

1. Base Station Pi with an RFM95 LoRa radio and OLED button interface.
2. Adafruit RP2040 Feather acting as the LoRa relay and local sensor node.
3. Drone Pi handling sampling hardware and status reporting over USB serial.

The goal of this code is to demonstrate end-to-end command passing, telemetry
delivery, and basic operator control before the full field system is deployed.

System Objectives
-----------------

- Send operator commands from the Base Station to the Feather over LoRa.
- Relay supported commands from the Feather to the Drone Pi over USB serial.
- Return ACK packets for commands and status packets for telemetry.
- Stream live Feather sensor readings when live mode is enabled.
- Log packet traffic so the radio link and command flow can be inspected later.

How the System Works
--------------------

Base Station UI

- The Base Station uses the OLED bonnet as the primary interface.
- Button A sends a sample command to the Drone Pi through the Feather.
- Button B requests Drone Pi status through the Feather.
- Button C enables Feather live-sensor mode, then cycles through the sensor pages.

Packet Flow

- Base Station sends JSON command packets over LoRa.
- Feather validates packets, relays Drone Pi commands over USB, and forwards
  responses back to the Base Station.
- Drone Pi runs the sampling hardware, responds with ACK packets, and sends
  status packets after successful status requests.
- Feather also sends periodic sensor packets while live mode is active.

Main Entry Points
-----------------

- Base station UI: `Base_station/waspp_com/main.py`
- Drone Pi controller: `DrPi/NB_2026_UWAS/UWAS_MAIN.py`
- Feather firmware: `WASPP_Relay.ino`

Startup and Usage
-----------------

1. Flash the Feather with `WASPP_Relay.ino`.
2. Connect the Feather to the Drone Pi by USB and install the Python
   dependencies needed by the Drone Pi environment.
3. Connect and configure the LoRa hardware on the Base Station Pi and Feather.
4. Start the Drone Pi program from `DrPi/NB_2026_UWAS/UWAS_MAIN.py`.
5. Start the Base Station program from `Base_station/waspp_com/main.py`.
6. Use the OLED buttons to send commands and view sensor or status pages.

Button Behavior
---------------

- A: send sample command to the Drone Pi.
- B: request Drone Pi status.
- C: start live sensor mode on the Feather, then cycle through sensor pages.

Notes
-----

- The Python scripts currently assume the Feather appears as `/dev/ttyACM0`.
  Update the serial port in the scripts if your device enumerates differently.
- The `.service` files in this repository are deployment examples. Update the
  `User`, `WorkingDirectory`, and `ExecStart` paths before using them on your
  own machine.
- Drone Pi Python dependencies are listed in
  `DrPi/NB_2026_UWAS/requirements.txt`.

Logging
-------

The code writes JSONL logs so packet traffic can be reviewed later:

- Base Station: `waspp_packet_log.jsonl` and `waspp_sensors.jsonl`
- Drone Pi: `packet_log.jsonl` and `local_log.jsonl`

Repository Layout
-----------------

- `Base_station/` contains the LoRa + OLED operator interface.
- `DrPi/` contains the Drone Pi controller and hardware wrapper code.
- `WASPP_Relay.ino` contains the Feather firmware that bridges LoRa and USB.
