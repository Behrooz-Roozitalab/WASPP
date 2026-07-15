|| Network Demo 
|| Nathan Bartley
|| SIParCS Internship 2026
|| Early Stage WASPP communication integration

Demonstrates communication between Base Station Raspberry Pi 3, Feather w LoRa, and Drone Pi 2
Commands for Drone Pi simply return an Ack
Base station uses LoRa/OLED hat as UI

1] Drone Pi (DrPi):			|	RPi 2. Full WASPP implementation expects custom hat for power
					|	WAS control, and other peripherals
					
2] Adafruit RP2040 Feather (FTR)	|	Network Demo implementation only handles LTR390, PM2.5, BME680,
					|	and TMP114. More Sensors added as needed. LoRa antenna is needed. 
					|	USB connection to DrPi is needed only to forward commands/acks 
					|	to/from DrPi.

3] Base Station Pi (BS)			|	RPi 3 b with Adafruit RFM95+ OLED Bonnet. Needs .service script
					|	to run on start, but does not require internet once implemented.
					|	use battery pack for portability. Interact with the system using 
					|	the OLED display on the bonnet. can send commands and view live
					|	sensor data.


----------------------------- USAGE ------------------------------------------------------
Use OLED interface on BS.

Buttons:

 A: --- Sample (demo) --> Feather --> DrPi	| Expects an Ack packet from DrPi
 B: --- Status (demo) --> Feather --> DrPi	| Expects an Ack packet from DrPi
 C: --- Live Sensor  --> Feather		| Switches display to live sensor reading.
						| Expects sensor updates every ~3 seconds.
						| Live_Mode off when another command is sent
						| C button cycles through available sensors

---------------------------- LOGS -------------------------------------------------------
creates two .jsonl files:

[1] waspp_base_station.jsonl	|	saves all packets sent and received from the base station
[2] sensor_log.jsonl 		|	only logs sensor packets received

