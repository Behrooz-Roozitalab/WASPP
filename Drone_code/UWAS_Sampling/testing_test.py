# Import necessary Libraries
import time
import numpy
import os
import sys
import csv
import math
from Hologram.HologramCloud import HologramCloud
from Hdwcom import GPScom, Windcom, RunSignal, Valcocom, ADCcom, Pumpcom

# Simulation Flag
'''
  0: Field experiment
  1: Simulation in lab
'''
SIM_FLAG = 0

# Parameters
OUTPUT_FOLDER = '/home/ljs/outputs/'
LOG_TESTCONF = 'testConfigLog.txt'
LOG_OPERATION = 'OperationLog.txt'
LOG_RAW = 'RawLog.txt'
DATA = 'Data.csv'
NO_SAT = 6 # Minimum number of satellite (GPS Configuration)
TRY_GPS_NUM = 15 # Number of tries to get the GPS (GPS Configuration)
# readADC_bat_flow
BAT_THRES = 3.65 # Minimum battery voltage (Battery Configuration)
DP_THRES = 2 # Minimum difference between Psys and Pamb (Pressure Configuration)
FLOW_THRES = 0.3 # Minimum flow (Flow Configuration)
FLUSHING_TIME = 30 # Flushing time for each sampling

# Global Variable for sensors
curr_gps = None
curr_wind = None
curr_bt = None
curr_trh = None 
flag_op = 0  # 0: operating, 1: Ending
match_key = 0

def write_files(folder, file, messages):
	'''
	This function writes txt or csv files for recording.
	It writes a list of messages line by line

	Input:
	folder>> a folder to write
	file>> a file to write on
	meassges>> a list of messages (doesn't have \n character in each message)
  
	Output:
	Only modify a file specified by folder & file variables
	'''
	os.chdir(folder)
	temp_data_file = open(file, 'a')
	for message in messages:
		temp_data_file.write(message + '\n')
	temp_data_file.close()

def print_msg(messages):
	'''
	This function prints out a list of messages line by line

	Input:
	messages>> a list of messages

	Output:
	None
	'''
	for message in messages:
		print(message)

def testing_sensors():
	'''
	This function conducts a series of testings on sensors.
	- GPS
	- Wind
	- Valco Valve
	- Battery & Flow (Thermistor)
	- Temp/Humidity/Pressure sensors
	- Testing each sensor's data
	- Testing pump / Signal
	- Program running singal
	''' 
	messages = ['------------------TESTING SENSORS------------------',
              '']
	print_msg(messages)
	write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
  
	### Getting GPS data ###
	gpsData = GPScom.getGPS()
	Date, Lat, Lon, Alt, sat = gpsData[0], gpsData[1], gpsData[2], gpsData[3], gpsData[4] # Date format is hhmmss.ss
  
	messages = ['>>>>>> Testing GPS:',
              'Date: ' + str(Date) + ', Lat: ' + str(Lat) + ', Lon: ' + str(Lon) + ', Alt: ' + str(Alt) + ', sat: ' + str(sat),
              '',
              '']
	print_msg(messages)
	write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)

	### Getting wind sensor (TriSonica Mini Wind & Weather Sensor) ###
	wind = Windcom.getWind(Date)
  
	messages = ['>>>>>> Testing wind sensor:',
              'Date: ' + str(Date) + ', wind: ' + str(wind),
              '',
              '']
	print_msg(messages)
	write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)            

  
	### Communicating with Valco Valve ###
	sendTo = 0 # Getting current position
	Pos1 = Valcocom.comValco(sendTo)

	messages = ['>>>>>> Testing Valco Valve:',
              'Current Position: ' + chr(Pos1[0]) + chr(Pos1[1]),
              '',
              '']
	print_msg(messages)
	write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)

	### Testing Battery & Flow (Thermistor) ###
	BT = ADCcom.readADC_bat_flow(Date)
  
	messages = ['>>>>>> Testing Battery & Flow:',
              'Battery voltage: ' + str(BT[0]),
              'Flow: ' + str(BT[1]),
              'Pwr10V: ' + str(BT[2]),
              '',
              '']
	print_msg(messages)
	write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)

	### Testing Temp/Humidity/Pressure sensors ###
	TRH = ADCcom.readADC_temp_rh_ps_pa(Date)
	RH, Temp, pSys, pAmb = TRH[0], TRH[1], TRH[2], TRH[3]

	messages = ['>>>>>> Testing Temp/Humidity/Pressure:',
              'RH: ' + str(RH),
              'Temp: ' + str(Temp),
              'pSys: ' + str(pSys),
              'pAmb: ' + str(pAmb),
              '',
              '']
	print_msg(messages)
	write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
  
	### Testing each sensor's data ###
	# Output: [pSysTest, pAmbTest, TempTest, RHTest, BTTest, ComTest, Overall]
	# sensors[0]: 0 - pass, 1 - pSys < 8
	# sensors[1]: 0 - pass, 2 - pAmb < 8
	# sensors[2]: 0 - pass, 3 - Temp < -5
	# sensors[3]: 0 - pass, 4 - RH < 2
	# sensors[4]: 0 - pass, 5 - BT < 3.65
	# sensors[5]: 0 - pass, 6 - abs(pSys-pAmb) > 1 # prior to pump test, system pressure and ambient pressure should be equal
	# sensors[6]: 0 - All pass, 1 - At least one test fails
	# Light on D4 & D6 (D4: Battery OK, D6: All sensor OK)
	sensors = RunSignal.testSensors(RH, Temp, pSys, pAmb, BT[0])
  
	messages = ['>>>>>> Testing sensors:',
              'Test Results: ' + str(sensors),
              '',
              '']
	print_msg(messages)
	write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)

	### Testing pump ###
	onOff = 1
	PumpStatus = Pumpcom.pumpOn(onOff)
  
	messages = ['>>>>>> Testing pump:',
              'Pump is On, Pump Status: ' + str(PumpStatus),
              '------ Wait for 5 sec ------']
	print_msg(messages)
	write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)

	time.sleep(15)
  
	onOff = 0
	PumpStatus = Pumpcom.pumpOn(onOff)

	messages = ['Pump is Off, Pump Status: ' + str(PumpStatus)]
	print_msg(messages)
	write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
  
	# Signal the success of pump test (Light on D7)
	PumpWorks = 1
	RunSignal.pumpTestSig(PumpWorks) # D7 lights on

	messages = ['Pump test Success!!!']
	print_msg(messages)
	write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)

	### Program running singal ###
	# Should be modified when all thresholds are set and sensors are working
	runningNow = RunSignal.programRunning(1)  # D5 lights on

	messages = ['------------------END TESTING SENSORS------------------',
             '',
             '',
             '']
	print_msg(messages)
	write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)


testing_sensors()
