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

def sampling(no_can, hologram):
	
	try:
		hologram.network.connect()
	except Exception as e:
		messages = [e]
		print_msg(messages)
		write_files(OUTPUT_FOLDER, LOG_OPERATION, messages)
	
	try:
		for no in range(no_can):
			messages = ['Waiting for ' + str(no+1) + ' canister']
			print_msg(messages)
			write_files(OUTPUT_FOLDER, LOG_OPERATION, messages)
			
			while True:
				hologram.openReceiveSocket()
				# Wait for 10 sec
				time.sleep(10)
				hologram.closeReceiveSocket()
				recv = hologram.popReceivedMessage()
				if recv is not None:
					messages = ['Message received, Start Sampling']
					print_msg(messages)
					write_files(OUTPUT_FOLDER, LOG_OPERATION, messages)
					
					############### CANISTER SAMPLING ###########
					
					print('action')
					time.sleep(5)
					print('action end')
					
					messages = ['Cansiter Sampling completed']
					print_msg(messages)
					write_files(OUTPUT_FOLDER, LOG_OPERATION, messages)
					
					return_msg = 'Canister ' + str(no+1) + ' Sampling Completed.'
					response_code = hologram.sendMessage(return_msg)
					messages = ['Return message sent']
					print_msg(messages)
					write_files(OUTPUT_FOLDER, LOG_OPERATION, messages)
					break
			messages = ['End of cansiter sampling']
			print_msg(messages)
			write_files(OUTPUT_FOLDER, LOG_OPERATION, messages)
				
	except Exception as e:
		messages = [e]
		print_msg(messages)
		write_files(OUTPUT_FOLDER, LOG_OPERATION, messages)
	finally:
		hologram.network.disconnect()
		messages = ['End all operation']
		print_msg(messages)
		write_files(OUTPUT_FOLDER, LOG_OPERATION, messages)

hologram = HologramCloud({'devicekey': 'OdZcEJzu'}, network='cellular')		
sampling(8, hologram)
