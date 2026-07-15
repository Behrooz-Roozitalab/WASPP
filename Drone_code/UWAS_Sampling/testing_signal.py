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

def check_celluar_signal(trial):
	hologram = HologramCloud({'devicekey': 'OdZcEJzu'}, network='cellular')
	messages = ['------------------START SIGNAL TESTING------------------',
				'']
	print_msg(messages)
	write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
	 
	for i in range(trial):
		rssi, qual = hologram.network.signal_strength.split(',')
		if int(rssi) > 10 and int(rssi) <=31:
			messages = ['Celluar signal is strong: ' + str(int(rssi)),
						'------------------END SIGNAL TESTING------------------',
						'',
						'']
			print_msg(messages)
			write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
			return int(rssi), hologram
	
	messages = ['Not enough signal: ' + str(int(rssi)),
				'------------------END SIGNAL TESTING------------------',
						'',
						'']
	print_msg(messages)
	write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
	return int(rssi), None
	
	
check_celluar_signal(20)
