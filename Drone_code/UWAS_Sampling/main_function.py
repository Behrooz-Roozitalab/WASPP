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
              '------ Wait for 15 sec ------']
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
					
					global curr_bt
					bt_start = curr_bt
					
					global curr_trh
					trh_start = curr_trh
					
					messages = ['Match_key: ' + str(mk_start),
				'GPS_Start (Date, lat, lon, alt): ' + str(gps_start[0]) + ', ' + str(gps_start[1]) + ', ' + str(gps_start[2]) + ', ' + str(gps_start[3]),
                'BT_Start (BattVoltage, Flow, 10V): ' + str(bt_start[0]) + ', ' + str(bt_start[1]) + ', ' + str(bt_start[2]),
                'TRH_Start (RH, T, Psys, Pamb): ' + str(trh_start[0]) + ', ' + str(trh_start[1]) + ', ' + str(trh_start[2]) + ', ' + str(trh_start[3])]
					print_msg(messages)
					write_files(OUTPUT_FOLDER, LOG_OPERATION, messages)
					
					### 4. Flushing for FLUSHING_TIME ###
					time.sleep(FLUSHING_TIME)
					
					### 5. Record sensor data (End) ### 
					global match_key
					mk_end = match_key
					
					global curr_gps
					gps_end = curr_gps
					
					global curr_bt
					bt_end = curr_bt
					
					global curr_trh
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
					
					messages = [str(chr(Pos1_start[0])) + str(chr(Pos1_start[1])) + ',' + str(mk_start) + ',' + str(mk_end) + ','
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
				
	except Exception as e:
		messages = [e]
		print_msg(messages)
		write_files(OUTPUT_FOLDER, LOG_OPERATION, messages)
	finally:
		hologram.network.disconnect()
		messages = ['End all operation']
		print_msg(messages)
		write_files(OUTPUT_FOLDER, LOG_OPERATION, messages)
	
		
		
		
		
	            
