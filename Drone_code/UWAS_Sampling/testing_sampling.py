# Import necessary Libraries
import time
import numpy
import os
import sys
import csv
import math
import threading
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
		global curr_gps		
		curr_gps = gpsData
		
		global curr_wind
		curr_wind = wind
		
		global curr_bt
		curr_bt = BT
		
		global curr_trh
		curr_trh = TRH
		
		Date, Lat, Lon, Alt, sat = gpsData[0], gpsData[1], gpsData[2], gpsData[3], gpsData[4] # Date format is hhmmss.ss
		BatVolt, Flow, Pwr10V = BT[0], BT[1], BT[2]
		RH, Temp, pSys, pAmb = TRH[0], TRH[1], TRH[2], TRH[3]
		
		### Logging the raw data
		messages = [str(match_key) + ',' + str(Date) + ',' + str(Lat) + ',' + str(Lon) + ',' + str(Alt) + ',' + str(sat) + ',' + str(BatVolt) + ',' + str(Flow) + ',' + str(Pwr10V) + ',' + str(RH) + ',' + str(Temp) + ',' + str(pSys) + ',' + str(pAmb)]
		#print_msg(messages)
		write_files(OUTPUT_FOLDER, LOG_RAW, messages)
		
		global flag_op
		if flag_op == 1:
			break
		
		match_key += 1
		time.sleep(0.1)
		
def sampling(no_can, hologram):
	
	try:
		print('Connection start')
		hologram.network.connect()
		print('Connection Successful')
	except Exception as e:
		print('Exception occured, ' + str(e))
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
				print('Waiting for 10 sec')
				time.sleep(10)
				hologram.closeReceiveSocket()
				recv = hologram.popReceivedMessage()
				if recv is not None:
					messages = ['Message received, Start Sampling']
					print_msg(messages)
					write_files(OUTPUT_FOLDER, LOG_OPERATION, messages)
					
					############### CANISTER SAMPLING ###########
					### 1. Turn on pump ###
					onOff = 1
					PumpStatus = Pumpcom.pumpOn(onOff)
					
					messages = ['Pump on']
					print_msg(messages)
					write_files(OUTPUT_FOLDER, LOG_OPERATION, messages)
					
					time.sleep(2)
					
					###  2. Move Valco valve position (even to odd) & Fill a canister ###
					sendTo = 2 # Valco valve position from even to odd
					Pos1_start = Valcocom.comValco(sendTo)
					
					### 3. Record sensor data (Start) ###
					global match_key
					mk_start = match_key
					
					global curr_gps
					gps_start = curr_gps
					if gps_start is None:
						gps_start = [0,0,0,0,0,0,0]
					
					global curr_bt
					bt_start = curr_bt
					if bt_start is None:
						bt_start = [0,0,0,0,0]
					
					global curr_trh
					trh_start = curr_trh
					if trh_start is None:
						trh_start = [0,0,0,0,0]
					
					messages = ['Match_key: ' + str(mk_start),
				'GPS_Start (Date, lat, lon, alt): ' + str(gps_start[0]) + ', ' + str(gps_start[1]) + ', ' + str(gps_start[2]) + ', ' + str(gps_start[3]),
                'BT_Start (BattVoltage, Flow, 10V): ' + str(bt_start[0]) + ', ' + str(bt_start[1]) + ', ' + str(bt_start[2]),
                'TRH_Start (RH, T, Psys, Pamb): ' + str(trh_start[0]) + ', ' + str(trh_start[1]) + ', ' + str(trh_start[2]) + ', ' + str(trh_start[3])]
					print_msg(messages)
					write_files(OUTPUT_FOLDER, LOG_OPERATION, messages)
					
					### 4. Flushing for FLUSHING_TIME ###
					time.sleep(FLUSHING_TIME)
					
					### 5. Record sensor data (End) ### 
					mk_end = match_key
					
					gps_end = curr_gps
					
					bt_end = curr_bt
					
					trh_end = curr_trh
					
					messages = ['Match_key: ' + str(mk_end),
				'GPS_End (Date, lat, lon, alt): ' + str(gps_end[0]) + ', ' + str(gps_end[1]) + ', ' + str(gps_end[2]) + ', ' + str(gps_end[3]),
                'BT_End (BattVoltage, Flow, 10V): ' + str(bt_end[0]) + ', ' + str(bt_end[1]) + ', ' + str(bt_end[2]),
                'TRH_End (RH, T, Psys, Pamb): ' + str(trh_end[0]) + ', ' + str(trh_end[1]) + ', ' + str(trh_end[2]) + ', ' + str(trh_end[3])]
					print_msg(messages)
					write_files(OUTPUT_FOLDER, LOG_OPERATION, messages)
					
					### 6. Move Valco valve position (odd to even) ###
					sendTo = 2 # Valco valve position from odd to even
					Pos1_end = Valcocom.comValco(sendTo)
					
					### 7. Turn off pump ###
					onOff = 0
					PumpStatus = Pumpcom.pumpOn(onOff)
					
					messages = ['Pump off']
					print_msg(messages)
					write_files(OUTPUT_FOLDER, LOG_OPERATION, messages)
					
					
					### 7. Save data for analysis ###
					# Pos_start, Pos_end, mk_start, mk_end, Date_start,Date_end,lat_start,lat_end,lon_start,lon_end,alt_start,alt_end,BattVol_start,BattVol_end,Flow_start,Flow_end,10V_start,10V_end,RH_start,RH_end,T_start,T_end,Psys_start,Psys_end,Pamb_start,Pamb_end
					messages = ['>>>>>>>> Recording data for analysis:']
					print_msg(messages)
					
					messages = [str(chr(Pos1_start[0])) + str(chr(Pos1_start[1])) + ',' + str(mk_start) + ',' + str(mk_end) + ',' +
                str(gps_start[0]) + ',' + str(gps_end[0]) + ',' +
                str(gps_start[1]) + ',' + str(gps_end[1]) + ',' +
                str(gps_start[2]) + ',' + str(gps_end[2]) + ',' +
                str(gps_start[3]) + ',' + str(gps_end[3]) + ',' +
                str(bt_start[0]) + ',' + str(bt_end[0]) + ',' +
                str(bt_start[1]) + ',' + str(bt_end[1]) + ',' +
                str(bt_start[2]) + ',' + str(bt_end[2]) + ',' +
                str(trh_start[0]) + ',' + str(trh_end[0]) + ',' +
                str(trh_start[1]) + ',' + str(trh_end[1]) + ',' +
                str(trh_start[2]) + ',' + str(trh_end[2]) + ',' +
                str(trh_start[3]) + ',' + str(trh_end[3]),
                '']    
					print_msg(messages)
					write_files(OUTPUT_FOLDER, DATA, messages)
									
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
		global flag_op
		flag_op = 1
				
	except Exception as e:
		messages = [e]
		print_msg(messages)
		write_files(OUTPUT_FOLDER, LOG_OPERATION, messages)
	finally:
		hologram.network.disconnect()
		messages = ['End all operation']
		print_msg(messages)
		write_files(OUTPUT_FOLDER, LOG_OPERATION, messages)
		flag_op = 1
		
hologram = HologramCloud({'devicekey': 'OdZcEJzu'}, network='cellular')
		
t1 = threading.Thread(target=reading_sensors, name='t1')
t2 = threading.Thread(target=sampling, name='t2', args=(8, hologram))

t1.start()
t2.start()

t1.join()
t2.join()
