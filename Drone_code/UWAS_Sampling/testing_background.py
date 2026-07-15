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
		


def reading_sensors():
	# Internal clock for matching key
	global match_key
	match_key=0
	
	while True:
		### Getting GPS data ###
		gpsData = GPScom.getGPS()
		
		### Getting wind sensor (TriSonica Mini Wind & Weather Sensor) ###
		wind = Windcom.getWind('')
		
		### Getting Battery & Flow (Thermistor) ###
		BT = ADCcom.readADC_bat_flow('')
		
		### Getting Temp/Humidity/Pressure sensors ###
		TRH = ADCcom.readADC_temp_rh_ps_pa('')
		
		### Global Variable
		global curr_GPS		
		curr_GPS = gpsData
		
		global curr_Wind
		curr_Wind = wind
		
		global curr_BT
		curr_BT = BT
		
		global curr_TRH
		curr_TRH = TRH
		
		Date, Lat, Lon, Alt, sat = gpsData[0], gpsData[1], gpsData[2], gpsData[3], gpsData[4] # Date format is hhmmss.ss
		BatVolt, Flow, Pwr10V = BT[0], BT[1], BT[2]
		RH, Temp, pSys, pAmb = TRH[0], TRH[1], TRH[2], TRH[3]
		
		### Logging the raw data
		messages = [str(match_key) + ',' + str(Date) + ',' + str(Lat) + ',' + str(Lon) + ',' + str(Alt) + ',' + str(sat) + ',' + str(BatVolt) + ',' + str(Flow) + ',' + str(Pwr10V) + ',' + str(RH) + ',' + str(Temp) + ',' + str(pSys) + ',' + str(pAmb)]
		print_msg(messages)
		write_files(OUTPUT_FOLDER, LOG_RAW, messages)
		
		global flag_op
		if flag_op == 1:
			break
		
		match_key += 1
		time.sleep(0.1)

reading_sensors()
