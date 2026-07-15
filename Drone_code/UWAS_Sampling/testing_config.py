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

def config_system(wayPoints):
	'''
	This function conducts a series of final tests on sensors.
	If any of tests fails, it shutdowns the system & Raspberry pi.
	- Waypoints # If there are more then 16 waypoints, shut down the program
	- GPS
	- Battery
	- Flow & Pressure
	- Valco valve position   # Set the initial position to 16 to ensure that first sampling position is always 01   
	'''

	messages = ['------------------START CONFIGURATION------------------',
              '']
	print_msg(messages)
	write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)

	### Check the number of waypoints ###
	# If there are more then 8 waypoints, shut down the program
	messages = ['>>>>>> Checking the number of waypoints:']
	print_msg(messages)
	write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
  
	if wayPoints>8:
		messages = ['Number of waypoints should be less than 9...',
                'Number of waypoints: ' + str(wayPoints),
                '......SHUTTING DOWN......',
                '',
                '']
		print_msg(messages)
		write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
 
    # Shut down the program & Raspberry pi
		if SIM_FLAG==0:
			messages = ['Quit for Number of waypoints']
			print_msg(messages)
			write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
			# quit()
			# softshutdown()
	else:
		messages = ['Number of waypoints: ' + str(wayPoints),
                '',
                '']
		print_msg(messages)
		write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
    

	### Configure GPS ### 
	# Getting GPS data until number of GPS satellites is greater than NO_SAT
	# Try TRY_GPS_NUM times and abort the program (default: 100 times)
	messages = ['>>>>>> Configuring GPS:']
	print_msg(messages)
	write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)

	flag = 0
	# Try TRY_GPS_NUM times
	for _ in range(TRY_GPS_NUM):
		# Getting GPS data
		gpsData = GPScom.getGPS()
		sat = float(gpsData[4])

		# if number of satellites is greater than the threshold
		if sat > NO_SAT:
			messages = ['Configuring GPS SUCCESS!!!',
                  'Num of satellites: ' + str(sat),
                  '',
                  '']
			print_msg(messages)
			write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
			flag = 1
			break

	# If GPS configuration fails
	if flag == 0:
		messages = ['Configuring GPS FAILS...',
                'Num of satellites: ' + str(sat),
                '......SHUTTING DOWN......',
                '',
                '']
		print_msg(messages)
		write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
		# Shut down the program & Raspberry pi
		if SIM_FLAG==0:
			messages = ['Quit for Number of satellites']
			print_msg(messages)
			write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
			# quit()
			# softshutdown()

	### Configure Battery ###
	messages = ['>>>>>> Configuring Battery:']
	print_msg(messages)
	write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
  
	BT = ADCcom.readADC_bat_flow(gpsData[0])
	BAT = BT[0]
	if BAT < BAT_THRES:
		messages = ['Configuring Battery FAILS...',
                'Battery Volt: value(' + str(BAT) + ') > threshold(' + str(BAT_THRES) + ')',
                '......SHUTTING DOWN......',
                '',
                '']
		print_msg(messages)
		write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
		# Shut down the program & Raspberry pi
		if SIM_FLAG==0:
			messages = ['Quit for Battery']
			print_msg(messages)
			write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
			# quit()
			# softshutdown()
	else:
		messages = ['Configuring Battery SUCCESS!!!',
                'Battery Volt: value(' + str(BAT) + ') > threshold(' + str(BAT_THRES) + ')',
                '',
                '']
		print_msg(messages)
		write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)

	### Configure Flow & Pressure ###
	messages = ['>>>>>> Configuring Flow & Pressure:']
	print_msg(messages)
	write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
  
	# Reading sensors' data
	BT = ADCcom.readADC_bat_flow(gpsData[0])
	TRH = ADCcom.readADC_temp_rh_ps_pa(gpsData[0])

	Flow = BT[1]
	pSys = TRH[2]
	pAmb = TRH[3]
	DP = abs(pSys-pAmb) 
  
	if not ((DP>DP_THRES) & (Flow>FLOW_THRES)):
		messages = ['Configuring Flow & Pressure FAILS...',
                'Diff between pSys & pAmb: value(' + str(DP) + ') > threshold(' + str(DP_THRES) + ')',
                'Flow: value(' + str(Flow) + ') > threshold(' + str(FLOW_THRES) + ')',
                '......SHUTTING DOWN......',
                '',
                '']
		print_msg(messages)
		write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
		# Shut down the program & Raspberry pi
		if SIM_FLAG==0:
			messages = ['Quit for DP']
			print_msg(messages)
			write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
			# quit()
			# softshutdown()
	else:
		messages = ['Configuring Flow & Pressure SUCCESS!!!',
                'Diff between pSys & pAmb: value(' + str(DP) + ') > threshold(' + str(DP_THRES) + ')',
                'Flow: value(' + str(Flow) + ') > threshold(' + str(FLOW_THRES) + ')',
                '',
                '']
		print_msg(messages)
		write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
  

	messages = ['------------------END CONFIGURATION------------------',
             '',
             '',
             '']
	print_msg(messages)
	write_files(OUTPUT_FOLDER, LOG_TESTCONF, messages)
	
config_system(8)
